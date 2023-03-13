import datetime
import logging
from decimal import Decimal
from typing import TypedDict

from dateutil.relativedelta import relativedelta

from hitas.exceptions import ModelConflict
from hitas.models import HousingCompanyState, SurfaceAreaPriceCeiling
from hitas.models.housing_company import HousingCompanyWithAnnotations
from hitas.services.housing_company import get_completed_housing_companies, make_index_adjustment_for_housing_companies
from hitas.utils import hitas_calculation_quarter, roundup

logger = logging.getLogger()


class SurfaceAreaPriceCeilingResult(TypedDict):
    month: str  # YearMonth, e.g. "2022-01"
    value: Decimal


def calculate_surface_area_price_ceiling(calculation_date: datetime.date) -> list[SurfaceAreaPriceCeilingResult]:
    calculation_month = hitas_calculation_quarter(calculation_date)

    logger.info(f"Calculating surface area price ceiling for {calculation_month.isoformat()!r}...")

    logger.info("Fetching housing companies...")
    housing_companies = get_completed_housing_companies(
        completion_month=calculation_month,
        states=[
            HousingCompanyState.LESS_THAN_30_YEARS,
            HousingCompanyState.GREATER_THAN_30_YEARS_NOT_FREE,
        ],
    )

    if not housing_companies:
        raise ModelConflict(
            f"No housing companies completed before {calculation_date.isoformat()!r} or all have wrong state.",
            error_code="missing",
        )

    logger.info("Making index adjustments...")
    make_index_adjustment_for_housing_companies(housing_companies, calculation_month)

    # TODO: Save housing company details to database (HT-434)

    logger.info(
        f"Setting surface area price ceiling for the next three months "
        f"starting from {calculation_month.isoformat()!r}..."
    )
    total = _calculate_surface_area_price_ceiling_for_housing_companies(housing_companies)
    results = _create_surface_area_price_ceiling_for_next_three_months(calculation_month, total)

    logger.info("Surface area price ceiling calculation complete!")
    return results


def _calculate_surface_area_price_ceiling_for_housing_companies(
    housing_companies: list[HousingCompanyWithAnnotations],
) -> Decimal:
    total: Decimal = sum((housing_company.avg_price_per_square_meter for housing_company in housing_companies))
    return roundup(total / len(housing_companies), precision=0)


def _create_surface_area_price_ceiling_for_next_three_months(
    from_: datetime.date,
    value: Decimal,
) -> list[SurfaceAreaPriceCeilingResult]:
    results: list[SurfaceAreaPriceCeilingResult] = []
    for month in range(3):
        surface_area_price_ceiling, _ = SurfaceAreaPriceCeiling.objects.update_or_create(
            month=from_ + relativedelta(months=month),
            defaults={"value": value},
        )
        results.append(
            SurfaceAreaPriceCeilingResult(
                month=surface_area_price_ceiling.month.isoformat()[:-3],
                value=surface_area_price_ceiling.value,
            )
        )
    return results
