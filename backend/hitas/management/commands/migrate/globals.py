import faker

_anonymize = False
_faker = faker.Factory.create("fi_FI")


def should_anonymize() -> bool:
    return _anonymize


def anonymize_data() -> None:
    global _anonymize
    _anonymize = True


def faker():
    return _faker
