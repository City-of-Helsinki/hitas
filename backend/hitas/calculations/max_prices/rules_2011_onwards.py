import datetime
from decimal import Decimal
from typing import List

from dateutil.relativedelta import relativedelta

from hitas.calculations.exceptions import IndexMissingException, InvalidCalculationResultException
from hitas.calculations.improvement import ImprovementData, calculate_housing_company_improvements_after_2010
from hitas.calculations.max_prices.rules import CalculatorRules, improvement_result_to_obj
from hitas.calculations.max_prices.types import IndexCalculation
from hitas.models import Apartment


class Rules2011Onwards(CalculatorRules):
    def validate_indices(self, apartment: Apartment) -> None:
        if (
            apartment.calculation_date_cpi_2005eq100 is None
            or apartment.completion_date_cpi_2005eq100 is None
            or apartment.calculation_date_mpi_2005eq100 is None
            or apartment.completion_date_mpi_2005eq100 is None
            or apartment.surface_area_price_ceiling is None
        ):
            raise IndexMissingException()

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
        return self._calculate_max_price(
            apartment,
            apartment.calculation_date_cpi_2005eq100,
            apartment.completion_date_cpi_2005eq100,
            total_surface_area,
            apartment_share_of_housing_company_loans,
            apartment_share_of_housing_company_loans_date,
            housing_company_improvements,
            calculation_date,
        )

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
        return self._calculate_max_price(
            apartment,
            apartment.calculation_date_mpi_2005eq100,
            apartment.completion_date_mpi_2005eq100,
            total_surface_area,
            apartment_share_of_housing_company_loans,
            apartment_share_of_housing_company_loans_date,
            housing_company_improvements,
            calculation_date,
        )

    @staticmethod
    def _calculate_max_price(
        apartment: Apartment,
        calculation_date_index: Decimal,
        completion_date_index: Decimal,
        total_surface_area: Decimal,
        apartment_share_of_housing_company_loans: Decimal,
        apartment_share_of_housing_company_loans_date: datetime.date,
        housing_company_improvements: List,
        calculation_date: datetime.date,
    ) -> IndexCalculation:
        # Start calculations

        # basic price
        basic_price = apartment.acquisition_price + apartment.additional_work_during_construction

        # index adjustment
        index_adjustment = ((calculation_date_index / completion_date_index) * basic_price) - basic_price

        # housing company improvements
        hc_improvements_result = calculate_housing_company_improvements_after_2010(
            [
                ImprovementData(
                    name=i.name,
                    value=i.value,
                    completion_date=i.completion_date,
                    completion_date_index=i.completion_date_index_2005eq100,
                )
                for i in housing_company_improvements
            ],
            calculation_date_index=calculation_date_index,
            total_surface_area=total_surface_area,
            apartment_surface_area=apartment.surface_area,
        )

        # debt free shares price
        debt_free_shares_price = (
            basic_price + index_adjustment + hc_improvements_result.summary.improvement_value_for_apartment
        )

        # maximum price
        max_price = debt_free_shares_price - apartment_share_of_housing_company_loans

        if max_price <= 0:
            raise InvalidCalculationResultException()

        return IndexCalculation(
            maximum_price=max_price,
            valid_until=calculation_date + relativedelta(months=3),
            calculation_variables=IndexCalculation.CalculationVars(
                acquisition_price=apartment.acquisition_price,
                additional_work_during_construction=apartment.additional_work_during_construction,
                interest_during_construction=None,
                basic_price=basic_price,
                index_adjustment=index_adjustment,
                apartment_improvements=None,
                housing_company_improvements=improvement_result_to_obj(hc_improvements_result),
                debt_free_price=debt_free_shares_price,
                debt_free_price_m2=debt_free_shares_price / apartment.surface_area,
                apartment_share_of_housing_company_loans=apartment_share_of_housing_company_loans,
                apartment_share_of_housing_company_loans_date=apartment_share_of_housing_company_loans_date,
                completion_date=apartment.completion_date,
                completion_date_index=completion_date_index,
                calculation_date=calculation_date,
                calculation_date_index=calculation_date_index,
            ),
        )
