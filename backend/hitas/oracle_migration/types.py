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

        return value if not should_anonymize() else faker.ssn()


class HitasAnonymizedName(types.TypeDecorator):
    impl = types.String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        return value if not should_anonymize() else faker.name()


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
