import datetime
from decimal import Decimal
from typing import List

from dateutil.relativedelta import relativedelta

from hitas.calculations.exceptions import IndexMissingException, InvalidCalculationResultException
from hitas.calculations.improvement import (
    ImprovementData,
    calculate_apartment_improvements_pre_2011,
    calculate_housing_company_improvements_pre_2011,
)
from hitas.calculations.max_prices.rules import CalculatorRules, improvement_result_to_obj
from hitas.calculations.max_prices.types import IndexCalculation, MaxPriceImprovements
from hitas.models import Apartment


class RulesPre2011(CalculatorRules):
    def validate_indices(self, apartment: Apartment) -> None:
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
        apartment: Apartment,
        total_surface_area: Decimal,
        apartment_share_of_housing_company_loans: Decimal,
        apartment_share_of_housing_company_loans_date: datetime.date,
        apartment_improvements: List,
        housing_company_improvements: List,
        calculation_date: datetime.date,
    ) -> IndexCalculation:
        # FIXME: implement
        return IndexCalculation(
            maximum_price=Decimal(0),
            valid_until=calculation_date + relativedelta(months=3),
            calculation_variables=IndexCalculation.CalculationVars(
                acquisition_price=apartment.acquisition_price,
                additional_work_during_construction=None,
                interest_during_construction=apartment.interest_during_construction,
                basic_price=Decimal(0),
                index_adjustment=Decimal(0),
                apartment_improvements=None,
                housing_company_improvements=MaxPriceImprovements(
                    items=[],
                    summary=MaxPriceImprovements.Summary(
                        depreciation=Decimal(0),
                        excess=MaxPriceImprovements.Summary.Excess(
                            surface_area=apartment.surface_area,
                            value_per_square_meter=Decimal(0),
                            total=Decimal(0),
                        ),
                        value=Decimal(0),
                        value_added=Decimal(0),
                        value_for_apartment=Decimal(0),
                        value_for_housing_company=Decimal(0),
                    ),
                ),
                debt_free_price=Decimal(0),
                debt_free_price_m2=Decimal(0),
                apartment_share_of_housing_company_loans=Decimal(0),
                apartment_share_of_housing_company_loans_date=apartment_share_of_housing_company_loans_date,
                completion_date=apartment.completion_date,
                completion_date_index=apartment.completion_date_cpi,
                calculation_date=calculation_date,
                calculation_date_index=apartment.calculation_date_cpi,
            ),
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
        # Start calculations

        # Basic price
        basic_price = apartment.acquisition_price + apartment.interest_during_construction

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
        if apartment.additional_work_during_construction:
            # Add `additional_work_during_construction` as an improvement as it's treated as an improvement
            # with pre 2011 rules
            apartment_improvements_list.append(
                ImprovementData(
                    name="Rakennusaikaiset muutos- ja lisätyöt",
                    value=apartment.additional_work_during_construction,
                    completion_date=apartment.completion_date,
                    completion_date_index=apartment.completion_date_mpi,
                    treat_as_additional_work=True,
                )
            )
        apartment_improvements_result = calculate_apartment_improvements_pre_2011(
            apartment_improvements_list,
            calculation_date=calculation_date,
            calculation_date_index=apartment.calculation_date_mpi,
            total_surface_area=total_surface_area,
            apartment_surface_area=apartment.surface_area,
        )

        # Housing company improvements
        hc_improvements_result = calculate_housing_company_improvements_pre_2011(
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
            + apartment_improvements_result.summary.improvement_value_for_apartment
            + hc_improvements_result.summary.improvement_value_for_apartment
        )

        # Final maximum price
        max_price = debt_free_shares_price - apartment_share_of_housing_company_loans

        if max_price <= 0:
            raise InvalidCalculationResultException()

        return IndexCalculation(
            maximum_price=max_price,
            valid_until=calculation_date + relativedelta(months=3),
            calculation_variables=IndexCalculation.CalculationVars(
                acquisition_price=apartment.acquisition_price,
                additional_work_during_construction=None,
                interest_during_construction=apartment.interest_during_construction,
                basic_price=basic_price,
                index_adjustment=index_adjustment,
                apartment_improvements=improvement_result_to_obj(apartment_improvements_result),
                housing_company_improvements=improvement_result_to_obj(hc_improvements_result),
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
