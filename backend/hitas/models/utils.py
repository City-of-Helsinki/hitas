import datetime
import re
from typing import Optional

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_property_id(value: str) -> None:
    # Example valid value: '1-1234-321-56'
    match = re.search(r"^\d{1,4}-\d{1,4}-\d{1,4}-\d{1,4}$", value)

    if match is None:
        raise ValidationError(
            _("%(value)s is not an valid property id"),
            params={"value": value},
        )


def validate_business_id(value: str) -> None:
    # Don't raise on None
    if value is None:
        return

    result = check_business_id(value)

    if not result:
        raise ValidationError("'%(value)s' is not a valid business id.", params={"value": value})


def check_business_id(value: str) -> bool:
    if value is None:
        return False

    # Example valid value: '1234567-1'
    match = re.search(r"^(\d{7})-(\d)$", value)
    if match is None:
        return False

    seqnum = match.group(1)
    check_digit = int(match.group(2))

    # Calculate checksum
    checksum = (
        int(seqnum[0]) * 7
        + int(seqnum[1]) * 9
        + int(seqnum[2]) * 10
        + int(seqnum[3]) * 5
        + int(seqnum[4]) * 8
        + int(seqnum[5]) * 4
        + int(seqnum[6]) * 2
    ) % 11

    match checksum:
        case 0:
            return check_digit == 0
        case 1:
            # 1 is not a valid checksum
            return False
        case _:
            return (11 - checksum) == check_digit


def validate_building_id(value: Optional[str]) -> None:
    if value is None:
        return

    # Example valid value: '100012345A'
    permanent_building_id_match = re.search(r"^1(\d{8})[A-Za-z0-9]$", value)
    if permanent_building_id_match is not None:
        # TODO: verify building id with the check digit
        return

    building_id_match = re.search(r"^\d{1,4}-\d{1,4}-\d{1,4}-\d{1,4} [A-Za-z0-9] \d{3}$", value)
    if building_id_match is None:
        raise ValidationError(
            _("%(value)s is not an valid building id"),
            params={"value": value},
        )
    # TODO: verify building id with the check digit


# fmt: off
_SSN_CHECK_DIGITS = [
    "0", "1", "2", "3",
    "4", "5", "6", "7",
    "8", "9", "A", "B",
    "C", "D", "E", "F",
    "H", "J", "K", "L",
    "M", "N", "P", "R",
    "S", "T", "U", "V",
    "W", "X", "Y",
]
# fmt: on


def validate_social_security_number(value: str) -> bool:
    if value is None:
        return False

    ssn_match = re.search(r"^(\d{6})([A-FYXWVU+-])(\d{3})([\dA-Z])$", value.upper())
    if ssn_match is None:
        return False

    date_str = ssn_match.group(1)
    century_sign = ssn_match.group(2)
    individual_number_str = ssn_match.group(3)
    check_digit = ssn_match.group(4)

    # Figure out the century from the century sign
    match century_sign:
        case "A" | "B" | "C" | "D" | "E" | "F":
            century = 2000
        case "-" | "Y" | "X" | "W" | "V" | "U":
            century = 1900
        case "+":
            century = 1800
        case _:
            # Regexp should have prevented this
            raise NotImplementedError(f"Invalid sign '{century_sign}'.")

    # Validate date (make sure date parts like '310222' are not valid)
    try:
        day, month, year = int(date_str[:2]), int(date_str[2:4]), int(date_str[4:])
        datetime.datetime(year=century + year, month=month, day=day)
    except ValueError:
        return False

    # Validate individual number, it must be between 002-899
    # 900-999 are temporary social security numbers.
    individual_number = int(individual_number_str)
    if individual_number < 2 or individual_number > 899:
        return False

    # Validate check digit
    return _SSN_CHECK_DIGITS[int(date_str + individual_number_str) % 31] == check_digit
