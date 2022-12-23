import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Type


@dataclass
class MaxPriceImprovements:
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

    items: List
    summary: Summary


@dataclass
class IndexCalculation:
    @dataclass
    class CommonCalculationVars:
        housing_company_improvements: MaxPriceImprovements
        debt_free_price: Decimal
        debt_free_price_m2: Decimal
        apartment_share_of_housing_company_loans: Decimal
        apartment_share_of_housing_company_loans_date: datetime.date
        completion_date: datetime.date
        completion_date_index: Decimal
        calculation_date: datetime.date
        calculation_date_index: Decimal

    @dataclass
    class CalculationVars2011Onwards(CommonCalculationVars):
        acquisition_price: Decimal
        additional_work_during_construction: Decimal
        basic_price: Decimal
        index_adjustment: Decimal

    @dataclass
    class CalculationVarsConstructionPriceIndexBefore2011(CommonCalculationVars):
        housing_company_acquisition_price: Decimal
        housing_company_assets: Decimal
        apartment_share_of_housing_company_assets: Decimal
        interest_during_construction: Decimal
        interest_during_construction_percentage: int
        apartment_improvements: MaxPriceImprovements

    @dataclass
    class CalculationVarsMarketPriceIndexBefore2011(CommonCalculationVars):
        acquisition_price: Decimal
        interest_during_construction: Decimal
        interest_during_construction_percentage: int
        basic_price: Decimal
        index_adjustment: Decimal
        apartment_improvements: MaxPriceImprovements

    maximum_price: Decimal
    valid_until: datetime.date
    calculation_variables: Type[CommonCalculationVars]
    maximum: bool = False


@dataclass
class SurfaceAreaPriceCeilingCalculation:
    @dataclass
    class CalculationVars:
        calculation_date: datetime.date
        calculation_date_value: Decimal
        debt_free_price: Decimal
        surface_area: Decimal
        apartment_share_of_housing_company_loans: Decimal
        apartment_share_of_housing_company_loans_date: datetime.date

    maximum_price: Decimal
    valid_until: datetime.date
    calculation_variables: CalculationVars
    maximum: bool = False
