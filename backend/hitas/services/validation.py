import re

from rest_framework.exceptions import ValidationError


def validate_postal_code(postal_code: str) -> str:
    """Validates value is a valid finnish postal code, e.g. '00101'."""
    match = re.match(r"^\d{5}$", postal_code)
    if match is None:
        raise ValidationError(f"{postal_code!r} is not a valid postal code.")
    return postal_code


def validate_quarter(value: str) -> str:
    """Validates value is a valid quarter, e.g. '2022Q3'."""
    match = re.match(r"^\d{4}Q[1234]$", value)
    if match is None:
        raise ValidationError(f"{value!r} is not a valid quarter.")
    return value
