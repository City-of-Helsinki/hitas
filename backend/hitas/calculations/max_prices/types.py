import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional

from hitas.types import Month


@dataclass
class MaxPriceImprovements:
    @dataclass
    class Improvement:
        @dataclass
        class Depreciation:
            @dataclass
            class DepreciationTime:
                years: int
                months: int

            amount: Decimal
            time: DepreciationTime

        name: str
        value: Decimal
        completion_date: Month
        value_added: Decimal
        depreciation: Optional[Depreciation]
        value_for_housing_company: Decimal
        value_for_apartment: Decimal

    @dataclass
    class Summary:
        @dataclass
        class Excess:
            surface_area: Decimal
            value_per_square_meter: Decimal
            total: Decimal

        value: Decimal
        value_added: Decimal
        excess: Excess
        depreciation: Decimal
        value_for_housing_company: Decimal
        value_for_apartment: Decimal

    items: List[Improvement]
    summary: Summary


@dataclass
class IndexCalculation:
    @dataclass
    class CalculationVars:
        acquisition_price: Decimal
        additional_work_during_construction: Optional[Decimal]
        interest_during_construction: Optional[Decimal]
        basic_price: Decimal
        index_adjustment: Decimal
        apartment_improvements: Optional[MaxPriceImprovements]
        housing_company_improvements: MaxPriceImprovements
        debt_free_price: Decimal
        debt_free_price_m2: Decimal
        apartment_share_of_housing_company_loans: Decimal
        apartment_share_of_housing_company_loans_date: datetime.date
        completion_date: datetime.date
        completion_date_index: Decimal
        calculation_date: datetime.date
        calculation_date_index: Decimal

    maximum_price: Decimal
    valid_until: datetime.date
    calculation_variables: CalculationVars
    maximum: bool = False


@dataclass
class SurfaceAreaPriceCeilingCalculation:
    @dataclass
    class CalculationVars:
        calculation_date: datetime.date
        calculation_date_value: Decimal
        surface_area: Decimal
        apartment_share_of_housing_company_loans: Decimal
        apartment_share_of_housing_company_loans_date: datetime.date

    maximum_price: Decimal
    valid_until: datetime.date
    calculation_variables: CalculationVars
    maximum: bool = False
