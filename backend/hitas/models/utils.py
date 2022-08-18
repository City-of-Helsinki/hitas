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
    # Example valid value: '1234567-8'
    match = re.search(r"^(\d{7})-(\d)$", value)

    if match is None:
        raise ValidationError(
            _("'%(value)s' is not a valid business id."),
            params={"value": value},
        )

    # TODO: verify business id with the check digit


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


def validate_share_numbers(start: Optional[int], end: Optional[int]) -> None:
    # TODO Validate overlap in share numbers across other HousingCompany shares
    if not start and not end:
        return
    if not start or not end:
        raise ValidationError(
            _("You must enter both: %(start)s and %(end)s or neither."),
            params={"start": "share_number_start", "end": "share_number_end"},
        )
    if start > end:
        raise ValidationError(
            _("%(start)s must not be greater than %(end)s"),
            params={"start": "share_number_start", "end": "share_number_end"},
        )
