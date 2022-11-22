import datetime
from decimal import Decimal
from typing import List

from dateutil.relativedelta import relativedelta

from hitas.calculations.improvement import ImprovementCalculationResult, ImprovementsResult
from hitas.calculations.max_prices.types import (
    IndexCalculation,
    MaxPriceImprovements,
    SurfaceAreaPriceCeilingCalculation,
)
from hitas.models import Apartment
from hitas.types import Month


class CalculatorRules:
    def validate_indices(self, apartment: Apartment) -> None:
        raise NotImplementedError()

    def calculate_construction_price_index_max_price(
        self,
        apartment: Apartment,
        total_surface_area: Decimal,
        apartment_share_of_housing_company_loans: Decimal,
        apartment_share_of_housing_company_loans_date: datetime.date,
        apartment_improvements: List,
        housing_company_improvements: List,
        calculation_date: datetime.date,
    ) -> IndexCalculation:
        raise NotImplementedError()

    def calculate_market_price_index_max_price(
        self,
        apartment: Apartment,
        total_surface_area: Decimal,
        apartment_share_of_housing_company_loans: Decimal,
        apartment_share_of_housing_company_loans_date: datetime.date,
        apartment_improvements: List,
        housing_company_improvements: List,
        calculation_date: datetime.date,
    ) -> IndexCalculation:
        raise NotImplementedError()

    @staticmethod
    def calculate_surface_area_price_ceiling(
        apartment: Apartment, calculation_date: datetime.date
    ) -> SurfaceAreaPriceCeilingCalculation:
        return SurfaceAreaPriceCeilingCalculation(
            maximum_price=apartment.surface_area_price_ceiling,
            valid_until=surface_area_price_ceiling_validity(calculation_date),
            calculation_variables=SurfaceAreaPriceCeilingCalculation.CalculationVars(
                calculation_date=calculation_date,
                calculation_date_value=apartment.surface_area_price_ceiling_m2,
                surface_area=apartment.surface_area,
            ),
        )


def improvement_to_obj(result: ImprovementCalculationResult) -> MaxPriceImprovements.Improvement:
    return MaxPriceImprovements.Improvement(
        name=result.name,
        value=result.value,
        completion_date=Month(result.completion_date),
        value_added=result.value_added,
        depreciation=MaxPriceImprovements.Improvement.Depreciation(
            amount=result.depreciation.amount,
            time=MaxPriceImprovements.Improvement.Depreciation.DepreciationTime(
                years=int(result.depreciation.time_months / 12),
                months=result.depreciation.time_months % 12,
            ),
        )
        if result.depreciation
        else None,
        value_for_housing_company=result.improvement_value_for_housing_company,
        value_for_apartment=result.improvement_value_for_apartment,
    )


def improvement_result_to_obj(result: ImprovementsResult) -> MaxPriceImprovements:
    return MaxPriceImprovements(
        items=list(map(improvement_to_obj, result.items)),
        summary=MaxPriceImprovements.Summary(
            value=result.summary.value,
            value_added=result.summary.value_added,
            excess=MaxPriceImprovements.Summary.Excess(
                surface_area=result.summary.excess.surface_area,
                value_per_square_meter=result.summary.excess.value_per_square_meter,
                total=result.summary.excess.total,
            ),
            depreciation=result.summary.depreciation,
            value_for_housing_company=result.summary.improvement_value_for_housing_company,
            value_for_apartment=result.summary.improvement_value_for_apartment,
        ),
    )


def surface_area_price_ceiling_validity(date: datetime.date) -> datetime.date:
    """
    1.2 - 30.4 -> end of May (31.5)
    1.5 - 31.7 -> end of August (31.8)
    1.8 - 31.10 -> end of November (30.11)
    1.11 - 31.1 -> end of February (28/29.2)
    """

    if date.month == 1:
        return date.replace(month=3, day=1) - relativedelta(days=1)
    if 2 <= date.month <= 4:
        return date.replace(month=5, day=31)
    elif 5 <= date.month <= 7:
        return date.replace(month=8, day=31)
    elif 8 <= date.month <= 10:
        return date.replace(month=11, day=30)
    else:
        return date.replace(year=date.year + 1, month=3, day=1) - relativedelta(days=1)
