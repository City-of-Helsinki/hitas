import datetime
from typing import Optional, Type

import pytz
from django.db import models
from django.utils.translation import gettext_lazy as _
from enumfields import Enum
from sqlalchemy.engine import LegacyRow

from hitas.models import BuildingType, HousingCompanyState
from hitas.models.apartment import DepreciationPercentage

TZ = pytz.timezone("Europe/Helsinki")


def str_to_year_month(value: str) -> datetime.date:
    return datetime.datetime.strptime(value, "%Y%m").date()


def date_to_datetime(d: datetime.date) -> Optional[datetime.datetime]:
    if d is None:
        return None

    return TZ.localize(datetime.datetime.combine(d, datetime.datetime.min.time()))


def turn_off_auto_now(model: Type[models.Model], field_name: str) -> None:
    model._meta.get_field(field_name).auto_now = False


def value_to_depreciation_percentage(value: str) -> DepreciationPercentage:
    match value:  # noqa: E999
        case "000":
            return DepreciationPercentage.ZERO
        case "001":
            return DepreciationPercentage.TWO_AND_HALF
        case "002":
            return DepreciationPercentage.TEN
        case _:
            raise ValueError(f"Invalid value '{value}'.")


def format_building_type(bt: BuildingType) -> None:
    bt.value = bt.value.capitalize()


def combine_notes(a: LegacyRow) -> str:
    return "\n".join(
        [note for note in [a["TEKSTI1"], a["TEKSTI2"], a["TEKSTI3"], a["TEKSTI4"], a["TEKSTI5"]] if note is not None]
    ).replace("-\n", "")


def housing_company_state_from(code: str) -> HousingCompanyState:
    # These are hardcoded as the code number (C_KOODISTOID) and
    # the name (C_NAME) are the only ones that can be used to
    # identify these types
    match code:
        case "000":
            return HousingCompanyState.NOT_READY
        case "001":
            return HousingCompanyState.LESS_THAN_30_YEARS
        case "002":
            return HousingCompanyState.GREATER_THAN_30_YEARS_NOT_FREE
        case "003":
            return HousingCompanyState.GREATER_THAN_30_YEARS_FREE
        case "004":
            return HousingCompanyState.GREATER_THAN_30_YEARS_PLOT_DEPARTMENT_NOTIFICATION
        case "005":
            return HousingCompanyState.HALF_HITAS


class ApartmentSaleMonitoringState(Enum):
    UNKNOWN = "000"  # Not in use
    ACTIVE = "001"  # This is the latest calculation
    CANCELLED = "002"  # Old calculation
    COMPLETE = "003"  # Apartment was sold
    RELATIVE_SALE = "004"  # Apartment was sold to a relative (or similar). Don't include in statistics

    class Labels:
        UNKNOWN = _("not_ready")
        ACTIVE = _("active")
        CANCELLED = _("cancelled")
        COMPLETE = _("complete")
        RELATIVE_SALE = _("relative_sale")
