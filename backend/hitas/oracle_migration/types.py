import datetime

import sqlalchemy.types as types

from hitas.oracle_migration.globals import faker, should_anonymize


class HitasAnonymizedSSN(types.TypeDecorator):
    impl = types.String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        return value if not should_anonymize() else faker().ssn()


class HitasAnonymizedName(types.TypeDecorator):
    impl = types.String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        return value if not should_anonymize() else faker().name()


class HitasAnonymizedNameCommaSeparated(HitasAnonymizedName):
    def process_result_value(self, value, dialect):
        if value is None:
            return None

        return (
            value if not should_anonymize() else f"{faker().last_name()}, {faker().first_name()} {faker().first_name()}"
        )


class HitasBoolean(types.TypeDecorator):
    """
    This is either 'K' (true) or 'E' (false) in the database
    """

    impl = types.String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return "K" if value else "E"

    def process_result_value(self, value, dialect):
        return value == "K"


class HitasYearMonth(types.TypeDecorator):
    """
    String containing year and month, for example '202209'
    """

    impl = types.String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return value.strftime("%Y%m")

    def process_result_value(self, value, dialect):
        return datetime.datetime.strptime(value, "%Y%m")


class HitasDuration(types.TypeDecorator):
    """
    String containing how many years and months, for example:
     - '1310' is 13 years and 10 months
     - '1212' is 13 years
     - '1301' is 13 years 1 month
     - '0001' is 1 month
     - '0000' is 0 months
    """

    impl = types.String
    cache_ok = True

    class InvalidValueException(Exception):
        pass

    class Duration:
        def __init__(self, years: int, months: int):
            if years < 0:
                raise HitasDuration.InvalidValueException(f"Invalid value for years: '{years}'.")
            # Month has to be between 1 and 12 (naturally) but 0 years 0 months is accepted too
            if months > 12 or months < (0 if years == 0 else 1):
                raise HitasDuration.InvalidValueException(f"Invalid value for months: '{months}'.")

            self.years = years
            self.months = months

    def process_bind_param(self, value, dialect):
        return f"{value.years:02d}{value.months:02d}"

    def process_result_value(self, value, dialect):
        years, months = int(value[:2]), int(value[2:])
        return HitasDuration.Duration(years, months)
