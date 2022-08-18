import re
from collections import defaultdict
from typing import List, Optional

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

_hitas_cost_areas = defaultdict(lambda: 4)
_hitas_cities = defaultdict(lambda: "Helsinki")


def _init_cost_areas() -> None:
    def init_cost_areas(index: int, postal_codes: List[str]) -> None:
        for postal_code in postal_codes:
            _hitas_cost_areas[postal_code] = index

    init_cost_areas(1, ["00100", "00120", "00130", "00140", "00150", "00160", "00170", "00180", "00220", "00260"])
    init_cost_areas(
        2,
        [
            "00200",
            "00210",
            "00250",
            "00270",
            "00280",
            "00290",
            "00300",
            "00310",
            "00320",
            "00330",
            "00340",
            "00380",
            "00500",
            "00510",
            "00520",
            "00530",
            "00540",
            "00550",
            "00560",
            "00570",
            "00580",
            "00590",
            "00610",
            "00810",
            "00850",
            "00990",
        ],
    )
    init_cost_areas(
        3,
        [
            "00240",
            "00350",
            "00360",
            "00370",
            "00400",
            "00430",
            "00440",
            "00620",
            "00650",
            "00660",
            "00670",
            "00680",
            "00690",
            "00730",
            "00780",
            "00790",
            "00800",
            "00830",
            "00840",
            "00950",
        ],
    )


_init_cost_areas()


def hitas_cost_area(postal_code: str) -> int:
    return _hitas_cost_areas[postal_code]


def hitas_city(postal_code: str) -> str:
    return _hitas_cities[postal_code]


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
