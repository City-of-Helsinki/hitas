import datetime
import random

import sqlalchemy.types as types
from dateutil.relativedelta import relativedelta

from hitas.oracle_migration.globals import faker, should_anonymize


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
        return str_to_year_month(value)


def str_to_year_month(value: str) -> datetime.date:
    return datetime.datetime.strptime(value, "%Y%m").date()


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


class HitasAnonymized(types.TypeDecorator):
    impl = types.String
    cache_ok = True

    def __init__(self, *args, **kwargs):
        self.unique = kwargs.pop("unique", False)
        self.used_fakes = set()

        super().__init__(*args, **kwargs)

    def fake(self, value):
        raise NotImplementedError()

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        return value if not should_anonymize() else self.generate_fake(value)

    def generate_fake(self, value):
        return self.generate_unique(value) if self.unique else self.fake(value)

    def generate_unique(self, value):
        try_count = 0
        while try_count < 20:
            fake_value = self.fake(value)

            if fake_value in self.used_fakes:
                try_count += 1
                continue

            self.used_fakes.add(fake_value)
            return fake_value

        raise Exception("Unable to generate unique fake value!")


class HitasAnonymizedAddress(HitasAnonymized):
    def fake(self, value):
        return faker().street_address() + str(faker().building_number())


class HitasAnonymizedName(HitasAnonymized):
    def fake(self, value):
        return faker().name()


class HitasAnonymizedNameCommaSeparated(HitasAnonymized):
    def fake(self, value):
        return f"{faker().last_name()}, {faker().first_name()} {faker().first_name()}"


class HitasAnonymizedSSN(HitasAnonymized):
    def fake(self, value):
        return faker().ssn()


class HitasAnonymizedPropertyIdentifier(HitasAnonymized):
    def fake(self, value):
        return (
            "091"
            + "0"
            + str(random.randint(0, 99))
            + "0"
            + str(random.randint(0, 999))
            + "00"
            + str(random.randint(0, 99))
        )


class HitasAnonymizedText(HitasAnonymized):
    def fake(self, value):
        if not value:
            return value

        return faker().text(max_nb_chars=self.length)


class HitasAnonymizedMonthAndDay(HitasAnonymized):
    def fake(self, value):
        beginning_of_year = value.replace(day=1, month=1)
        beginning_of_next_year = beginning_of_year.replace(year=beginning_of_year.year + 1)
        return faker().date_between_dates(beginning_of_year, beginning_of_next_year)


class HitasAnonymizedDay(HitasAnonymized):
    def fake(self, value):
        beginning_of_month = value.replace(day=1)
        beginning_of_next_month = value + relativedelta(months=1)
        return faker().date_between_dates(beginning_of_month, beginning_of_next_month)


class HitasAnonymizedEmail(HitasAnonymized):
    def fake(self, value):
        if not value:
            return value

        return faker().email()


class HitasAnonymizedCompany(HitasAnonymized):
    def fake(self, value):
        return faker().company()


class HitasAnonymizedWord(HitasAnonymized):
    def fake(self, value):
        return faker().word()
