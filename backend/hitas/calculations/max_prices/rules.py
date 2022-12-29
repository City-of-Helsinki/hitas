import datetime
from decimal import Decimal
from typing import List

from dateutil.relativedelta import relativedelta

from hitas.calculations.max_prices.types import IndexCalculation, SurfaceAreaPriceCeilingCalculation
from hitas.models import Apartment


class CalculatorRules:
    def validate_indices(self, apartment: Apartment) -> None:
        raise NotImplementedError()

    def calculate_construction_price_index_max_price(
        self,
        apartment: Apartment,
        total_surface_area: Decimal,
        apartment_share_of_housing_company_loans: int,
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
        apartment_share_of_housing_company_loans: int,
        apartment_share_of_housing_company_loans_date: datetime.date,
        apartment_improvements: List,
        housing_company_improvements: List,
        calculation_date: datetime.date,
    ) -> IndexCalculation:
        raise NotImplementedError()

    @staticmethod
    def calculate_surface_area_price_ceiling(
        apartment: Apartment,
        apartment_share_of_housing_company_loans: int,
        apartment_share_of_housing_company_loans_date: datetime.date,
        calculation_date: datetime.date,
    ) -> SurfaceAreaPriceCeilingCalculation:
        return SurfaceAreaPriceCeilingCalculation(
            maximum_price=apartment.surface_area_price_ceiling - apartment_share_of_housing_company_loans,
            valid_until=surface_area_price_ceiling_validity(calculation_date),
            calculation_variables=SurfaceAreaPriceCeilingCalculation.CalculationVars(
                calculation_date=calculation_date,
                calculation_date_value=apartment.surface_area_price_ceiling_m2,
                debt_free_price=apartment.surface_area_price_ceiling,
                surface_area=apartment.surface_area,
                apartment_share_of_housing_company_loans=apartment_share_of_housing_company_loans,
                apartment_share_of_housing_company_loans_date=apartment_share_of_housing_company_loans_date,
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
