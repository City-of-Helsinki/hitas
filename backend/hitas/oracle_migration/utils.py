import sys
import datetime
from functools import wraps
from typing import Optional, Type, ParamSpec, TypeVar, Callable

import pytz
from django.db import models
from django.utils.translation import gettext_lazy as _
from enumfields import Enum
from sqlalchemy.engine import LegacyRow

from hitas.models import BuildingType, HousingCompanyState
from hitas.models.apartment import DepreciationPercentage
from hitas.models.housing_company import RegulationStatus

TZ = pytz.timezone("Europe/Helsinki")
T = TypeVar("T")
P = ParamSpec("P")


def str_to_year_month(value: str) -> datetime.date:
    def parse_date(value: str):
        return datetime.datetime.strptime(value, "%Y%m").date()

    try:
        return parse_date(value)
    except ValueError:
        # If an invalid value is given, try to make sense of the value.
        # These are required due for the oracle migration.
        if value[-1:-2] == "00":
            return parse_date(value[:4] + "01")
        elif len(value) == 4:
            return parse_date(value + "01")


def date_to_datetime(d: datetime.date) -> Optional[datetime.datetime]:
    if d is None:
        return None

    return TZ.localize(datetime.datetime.combine(d, datetime.datetime.min.time()))


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


def housing_company_regulation_status_from(code: str) -> RegulationStatus:
    # These are hardcoded as the code number (C_KOODISTOID) and
    # the name (C_NAME) are the only ones that can be used to
    # identify these types
    if code == "003":
        return RegulationStatus.RELEASED_BY_HITAS
    if code == "004":
        return RegulationStatus.RELEASED_BY_PLOT_DEPARTMENT

    return RegulationStatus.REGULATED


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


def prints_to_file(file: str, mode: str = "w") -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Print to the given file instead of stdout for debugging purposes."""

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            with open(file, mode=mode) as f:
                try:
                    orig_stdout = sys.stdout
                    sys.stdout = f
                    val = func(*args, **kwargs)
                finally:
                    sys.stdout = orig_stdout

            return val

        return wrapper

    return decorator
