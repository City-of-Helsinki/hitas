import datetime
from decimal import Decimal
from typing import List

from dateutil.relativedelta import relativedelta

from hitas.calculations.depreciation_percentage import depreciation_multiplier
from hitas.calculations.exceptions import IndexMissingException, InvalidCalculationResultException
from hitas.calculations.helpers import months_between_dates
from hitas.calculations.improvements.common import ImprovementData
from hitas.calculations.improvements.rules_pre_2011_cpi import (
    calculate_apartment_improvements_pre_2011_construction_price_index,
    calculate_housing_company_improvements_pre_2011_construction_price_index,
)
from hitas.calculations.improvements.rules_pre_2011_mpi import (
    calculate_apartment_improvements_pre_2011_market_price_index,
    calculate_housing_company_improvements_pre_2011_market_price_index,
)
from hitas.calculations.max_prices.rules import CalculatorRules
from hitas.calculations.max_prices.types import IndexCalculation
from hitas.models.apartment import ApartmentWithAnnotationsMaxPrice


class RulesPre2011(CalculatorRules):
    def validate_indices(self, apartment: ApartmentWithAnnotationsMaxPrice) -> None:
        if (
            apartment.calculation_date_cpi is None
            or apartment.completion_date_cpi is None
            or apartment.calculation_date_mpi is None
            or apartment.completion_date_mpi is None
            or apartment.surface_area_price_ceiling is None
        ):
            raise IndexMissingException()

    def calculate_construction_price_index_max_price(
        self,
        apartment: ApartmentWithAnnotationsMaxPrice,
        total_surface_area: Decimal,
        apartment_share_of_housing_company_loans: int,
        apartment_share_of_housing_company_loans_date: datetime.date,
        apartment_improvements: List,
        housing_company_improvements: List,
        calculation_date: datetime.date,
    ) -> IndexCalculation:
        housing_company_index_adjusted_acquisition_price = (
            apartment.completion_date_realized_housing_company_acquisition_price
            * apartment.calculation_date_cpi
            * depreciation_multiplier(months_between_dates(apartment.completion_date, calculation_date))
        ) / apartment.completion_date_cpi

        hc_improvements_result = calculate_housing_company_improvements_pre_2011_construction_price_index(
            [
                ImprovementData(
                    name=i.name,
                    value=i.value,
                    completion_date=i.completion_date,
                    completion_date_index=i.completion_date_index,
                )
                for i in housing_company_improvements
            ],
            completion_date_acquisition_price=apartment.completion_date_realized_housing_company_acquisition_price,
            total_acquisition_price=apartment.realized_housing_company_acquisition_price,
        )

        housing_company_assets = (
            housing_company_index_adjusted_acquisition_price + hc_improvements_result.summary.value_for_apartment
        )

        # Apartment share share
        apartment_share_of_housing_company_assets = (
            housing_company_assets
            * apartment.first_sale_acquisition_price
            / apartment.completion_date_realized_housing_company_acquisition_price
        )

        # Apartment improvements
        apartment_improvements_list = [
            ImprovementData(
                name=i.name,
                value=i.value,
                completion_date=i.completion_date,
                completion_date_index=i.completion_date_index,
                depreciation_percentage=i.depreciation_percentage.value,
            )
            for i in apartment_improvements
        ]
        apartment_improvements_result = calculate_apartment_improvements_pre_2011_construction_price_index(
            apartment_improvements_list,
            calculation_date=calculation_date,
            calculation_date_index=apartment.calculation_date_cpi,
        )

        # Interest during construction
        if apartment.completion_date < datetime.date(2005, 1, 1):
            interest_during_construction = apartment.interest_during_construction_14 or 0
            interest_during_construction_percentage = 14
        else:
            interest_during_construction = apartment.interest_during_construction_6 or 0
            interest_during_construction_percentage = 6

        index_adjusted_additional_work_during_construction = (
            (apartment.additional_work_during_construction or 0)
            * apartment.calculation_date_cpi
            / apartment.completion_date_cpi
        )

        # Debt free shares price
        debt_free_shares_price = (
            apartment_share_of_housing_company_assets
            + interest_during_construction
            + apartment_improvements_result.summary.value_for_apartment
            + index_adjusted_additional_work_during_construction
        )

        # Final maximum price
        max_price = debt_free_shares_price - apartment_share_of_housing_company_loans

        if max_price <= 0:
            raise InvalidCalculationResultException()

        return IndexCalculation(
            maximum_price=max_price,
            valid_until=calculation_date + relativedelta(months=3),
            calculation_variables=IndexCalculation.CalculationVarsConstructionPriceIndexBefore2011(
                housing_company_acquisition_price=housing_company_index_adjusted_acquisition_price,
                housing_company_assets=housing_company_assets,
                apartment_share_of_housing_company_assets=apartment_share_of_housing_company_assets,
                interest_during_construction=interest_during_construction,
                interest_during_construction_percentage=interest_during_construction_percentage,
                additional_work_during_construction=apartment.additional_work_during_construction or 0,
                index_adjusted_additional_work_during_construction=index_adjusted_additional_work_during_construction,
                apartment_improvements=apartment_improvements_result,
                housing_company_improvements=hc_improvements_result,
                debt_free_price=debt_free_shares_price,
                debt_free_price_m2=debt_free_shares_price / apartment.surface_area,
                apartment_share_of_housing_company_loans=apartment_share_of_housing_company_loans,
                apartment_share_of_housing_company_loans_date=apartment_share_of_housing_company_loans_date,
                completion_date=apartment.completion_date,
                completion_date_index=apartment.completion_date_cpi,
                calculation_date=calculation_date,
                calculation_date_index=apartment.calculation_date_cpi,
            ),
        )

    def calculate_market_price_index_max_price(
        self,
        apartment: ApartmentWithAnnotationsMaxPrice,
        total_surface_area: Decimal,
        apartment_share_of_housing_company_loans: int,
        apartment_share_of_housing_company_loans_date: datetime.date,
        apartment_improvements: List,
        housing_company_improvements: List,
        calculation_date: datetime.date,
    ) -> IndexCalculation:
        # Start calculations

        # Basic price
        basic_price = (
            apartment.first_sale_acquisition_price
            + (apartment.interest_during_construction_6 or 0)
            + (apartment.additional_work_during_construction or 0)
        )

        # Index adjustment
        index_adjustment = (apartment.calculation_date_mpi / apartment.completion_date_mpi) * basic_price - basic_price

        # Apartment improvements
        apartment_improvements_list = [
            ImprovementData(
                name=i.name,
                value=i.value,
                completion_date=i.completion_date,
                completion_date_index=i.completion_date_index,
            )
            for i in apartment_improvements
        ]
        apartment_improvements_result = calculate_apartment_improvements_pre_2011_market_price_index(
            apartment_improvements_list,
            calculation_date=calculation_date,
            calculation_date_index=apartment.calculation_date_mpi,
            apartment_surface_area=apartment.surface_area,
        )

        # Housing company improvements
        hc_improvements_result = calculate_housing_company_improvements_pre_2011_market_price_index(
            [
                ImprovementData(
                    name=i.name,
                    value=i.value,
                    completion_date=i.completion_date,
                    completion_date_index=i.completion_date_index,
                )
                for i in housing_company_improvements
            ],
            calculation_date=calculation_date,
            calculation_date_index=apartment.calculation_date_mpi,
            total_surface_area=total_surface_area,
            apartment_surface_area=apartment.surface_area,
        )

        # Debt free shares price
        debt_free_shares_price = (
            basic_price
            + index_adjustment
            + apartment_improvements_result.summary.accepted_value
            + hc_improvements_result.summary.accepted_value
        )

        # Final maximum price
        max_price = debt_free_shares_price - apartment_share_of_housing_company_loans

        if max_price <= 0:
            raise InvalidCalculationResultException()

        return IndexCalculation(
            maximum_price=max_price,
            valid_until=calculation_date + relativedelta(months=3),
            calculation_variables=IndexCalculation.CalculationVarsMarketPriceIndexBefore2011(
                first_sale_acquisition_price=apartment.first_sale_acquisition_price,
                interest_during_construction=apartment.interest_during_construction_6 or 0,
                interest_during_construction_percentage=6,
                additional_work_during_construction=apartment.additional_work_during_construction or 0,
                basic_price=basic_price,
                index_adjustment=index_adjustment,
                apartment_improvements=apartment_improvements_result,
                housing_company_improvements=hc_improvements_result,
                debt_free_price=debt_free_shares_price,
                debt_free_price_m2=debt_free_shares_price / apartment.surface_area,
                apartment_share_of_housing_company_loans=apartment_share_of_housing_company_loans,
                apartment_share_of_housing_company_loans_date=apartment_share_of_housing_company_loans_date,
                completion_date=apartment.completion_date,
                completion_date_index=apartment.completion_date_mpi,
                calculation_date=calculation_date,
                calculation_date_index=apartment.calculation_date_mpi,
            ),
        )
