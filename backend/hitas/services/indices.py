import datetime
import logging
from decimal import Decimal
from typing import Literal, Optional

from dateutil.relativedelta import relativedelta
from django.db.models import Case, OuterRef, Q, Subquery, When

from hitas.exceptions import ModelConflict
from hitas.models import (
    ConstructionPriceIndex,
    ConstructionPriceIndex2005Equal100,
    HousingCompanyState,
    SurfaceAreaPriceCeiling,
)
from hitas.models._base import HitasModelDecimalField
from hitas.models.housing_company import HousingCompanyWithAnnotations
from hitas.models.indices import (
    CalculationData,
    HousingCompanyData,
    SurfaceAreaPriceCeilingCalculationData,
    SurfaceAreaPriceCeilingResult,
)
from hitas.services.housing_company import get_completed_housing_companies, make_index_adjustment_for_housing_companies
from hitas.utils import hitas_calculation_quarter, roundup

logger = logging.getLogger()


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

    unadjusted_prices: dict[str, Optional[Decimal]] = {
        housing_company.uuid.hex: housing_company.avg_price_per_square_meter for housing_company in housing_companies
    }

    logger.info("Making index adjustments...")
    indices = make_index_adjustment_for_housing_companies(housing_companies, calculation_month)

    logger.info(
        f"Setting surface area price ceiling for the next three months "
        f"starting from {calculation_month.isoformat()!r}..."
    )
    total = _calculate_surface_area_price_ceiling_for_housing_companies(housing_companies)
    results = _create_surface_area_price_ceiling_for_next_three_months(calculation_month, total)

    logger.info("Saving calculation data for later use...")
    _save_calculation_data(calculation_month, housing_companies, indices, unadjusted_prices, results)

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
                value=float(surface_area_price_ceiling.value),
            )
        )
    return results


def _save_calculation_data(
    calculation_month: datetime.date,
    housing_companies: list[HousingCompanyWithAnnotations],
    indices: dict[Literal["old", "new"], dict[datetime.date, Decimal]],
    unadjusted_prices: dict[str, Optional[Decimal]],
    surface_area_price_ceilings: list[SurfaceAreaPriceCeilingResult],
) -> SurfaceAreaPriceCeilingCalculationData:
    data = CalculationData(
        housing_company_data=[
            HousingCompanyData(
                name=housing_company.display_name,
                completion_date=housing_company.completion_date.isoformat(),
                surface_area=float(housing_company.surface_area),
                realized_acquisition_price=float(housing_company.realized_acquisition_price),
                unadjusted_average_price_per_square_meter=float(unadjusted_prices[housing_company.uuid.hex]),
                adjusted_average_price_per_square_meter=float(housing_company.avg_price_per_square_meter),
                completion_month_index=float(indices[key][housing_company.completion_month]),
                calculation_month_index=float(indices[key][calculation_month]),
            )
            for housing_company in housing_companies
            if (key := "old" if housing_company.financing_method.old_hitas_ruleset else "new")
        ],
        created_surface_area_price_ceilings=surface_area_price_ceilings,
    )
    return SurfaceAreaPriceCeilingCalculationData.objects.create(calculation_month=calculation_month, data=data)


def subquery_appropriate_cpi(outer_ref: str, financing_method_ref: str) -> Case:
    """
    Make a subquery for appropriate construction price index based on housing company's financing method.
    """
    return Case(
        When(
            condition=Q(**{f"{financing_method_ref}__old_hitas_ruleset": True}),
            then=(
                Subquery(
                    queryset=(ConstructionPriceIndex.objects.filter(month=OuterRef(outer_ref)).values("value")[:1]),
                    output_field=HitasModelDecimalField(),
                )
            ),
        ),
        default=(
            Subquery(
                queryset=(
                    ConstructionPriceIndex2005Equal100.objects.filter(month=OuterRef(outer_ref)).values("value")[:1]
                ),
                output_field=HitasModelDecimalField(),
            )
        ),
    )
