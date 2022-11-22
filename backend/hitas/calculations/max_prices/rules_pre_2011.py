import datetime
from decimal import Decimal
from typing import List

from hitas.calculations.max_prices.rules import CalculatorRules
from hitas.calculations.max_prices.types import IndexCalculation
from hitas.models import Apartment


class RulesPre2011(CalculatorRules):
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
