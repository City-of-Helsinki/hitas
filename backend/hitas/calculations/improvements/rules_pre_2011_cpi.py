import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import Callable, List

from hitas.calculations.exceptions import IndexMissingException
from hitas.calculations.helpers import months_between_dates
from hitas.calculations.improvements.common import ImprovementData


@dataclass
class ApartmentImprovementCalculationResult:
    @dataclass
    class Depreciation:
        @dataclass
        class DepreciationTime:
            years: int
            months: int

            @classmethod
            def create(cls, months: int):
                return cls(years=int(months / 12), months=months % 12)

        # Depreciation time for this improvement
        time: DepreciationTime
        # The total depreciation amount
        amount: Decimal
        # Improvement depreciation percentage
        percentage: Decimal

    # Name for the improvement
    name: str
    # Original value for the improvement
    value: Decimal
    # Calculation date index for the improvement
    calculation_date_index: Decimal
    # Completion date index for the improvement
    completion_date_index: Decimal
    # When the improvement was completed
    completion_date: datetime.date
    # Index adjusted value of this improvement
    index_adjusted: Decimal
    # Depreciation information for this improvement
    depreciation: Depreciation
    # Final accepted value for the apartment
    value_for_apartment: Decimal


@dataclass
class ApartmentImprovementCalculationSummary:
    # Original value for the improvement
    value: Decimal
    # Index adjusted value of this improvement
    index_adjusted: Decimal
    # Sum of all depreciation
    depreciation: Decimal
    # Improvement share of a housing company's improvement value
    value_for_apartment: Decimal


@dataclass
class ApartmentImprovementsResult:
    items: List[ApartmentImprovementCalculationResult]
    summary: ApartmentImprovementCalculationSummary


def calculate_apartment_improvements_pre_2011_construction_price_index(
    improvements: List[ImprovementData],
    calculation_date: datetime.date,
    calculation_date_index: Decimal,
) -> ApartmentImprovementsResult:
    def calc_fn(improvement):
        return calculate_single_apartment_improvement_pre_2011_construction_price_index(
            improvement,
            calculation_date=calculation_date,
            calculation_date_index=calculation_date_index,
        )

    return calculate_multiple_apartment_improvements(
        improvements,
        calc_fn,
    )


def calculate_single_apartment_improvement_pre_2011_construction_price_index(
    improvement: ImprovementData,
    calculation_date: datetime.date,
    calculation_date_index: Decimal,
) -> ApartmentImprovementCalculationResult:
    if improvement.treat_as_additional_work:
        return calculate_additional_work(improvement, calculation_date, calculation_date_index)

    if improvement.completion_date_index is None or calculation_date_index is None:
        raise IndexMissingException()

    #
    # Calculate the accepted value ('hyväksytty') for this improvement
    #
    # Adjust the accepted value with the index check
    index_adjusted = improvement.value * calculation_date_index / improvement.completion_date_index

    depreciation_time_months = months_between_dates(improvement.completion_date, calculation_date)

    depreciation_amount = min(
        (
            calculation_date_index
            * improvement.value
            * depreciation_time_months
            * improvement.depreciation_percentage
            / 100
        )
        / (improvement.completion_date_index * 12),
        index_adjusted,
    )

    depreciation_result = ApartmentImprovementCalculationResult.Depreciation(
        time=ApartmentImprovementCalculationResult.Depreciation.DepreciationTime.create(depreciation_time_months),
        amount=depreciation_amount,
        percentage=improvement.depreciation_percentage,
    )

    #
    # Return the result
    #
    return ApartmentImprovementCalculationResult(
        name=improvement.name,
        value=improvement.value,
        completion_date=improvement.completion_date,
        calculation_date_index=calculation_date_index,
        completion_date_index=improvement.completion_date_index,
        index_adjusted=index_adjusted,
        depreciation=depreciation_result,
        value_for_apartment=index_adjusted - depreciation_amount,
    )


def calculate_multiple_apartment_improvements(
    improvements,
    calc_fn: Callable[[ImprovementData], ApartmentImprovementCalculationResult],
) -> ApartmentImprovementsResult:
    results: List[ApartmentImprovementCalculationResult] = []

    summary_value = Decimal(0)
    summary_index_adjusted = Decimal(0)
    summary_depreciation = Decimal(0)
    summary_value_for_apartment = Decimal(0)

    # Calculate result for each improvement and calculate the summary
    for improvement in improvements:
        result = calc_fn(improvement)

        # Summary calculation
        summary_value += result.value
        summary_index_adjusted += result.index_adjusted
        summary_depreciation += result.depreciation.amount
        summary_value_for_apartment += result.value_for_apartment

        results.append(result)

    # Generate summary report
    summary = ApartmentImprovementCalculationSummary(
        value=summary_value,
        index_adjusted=summary_index_adjusted,
        depreciation=summary_depreciation,
        value_for_apartment=summary_value_for_apartment,
    )

    return ApartmentImprovementsResult(items=results, summary=summary)


#
# Housing company
#


@dataclass
class HousingCompanyImprovementCalculationResult:
    # Name for the improvement
    name: str
    # Original value for the improvement
    value: Decimal
    # Improvement share of a housing company's improvement value
    value_for_apartment: Decimal


@dataclass
class HousingCompanyImprovementCalculationSummary:
    # Sum of all improvement values
    value: Decimal
    # Sum of all improvement shares of a housing company's improvements
    value_for_apartment: Decimal


@dataclass
class HousingCompanyImprovementsResult:
    items: List[HousingCompanyImprovementCalculationResult]
    summary: HousingCompanyImprovementCalculationSummary


def calculate_housing_company_improvements_pre_2011_construction_price_index(
    improvements: List[ImprovementData],
    completion_date_acquisition_price: Decimal,
    total_acquisition_price: Decimal,
) -> HousingCompanyImprovementsResult:
    def calc_fn(improvement):
        return calculate_single_housing_company_improvement_pre_2011_construction_price_index(
            improvement,
            completion_date_acquisition_price=completion_date_acquisition_price,
            total_acquisition_price=total_acquisition_price,
        )

    return calculate_multiple_housing_company_improvements(improvements, calc_fn)


def calculate_single_housing_company_improvement_pre_2011_construction_price_index(
    improvement: ImprovementData,
    completion_date_acquisition_price: Decimal,
    total_acquisition_price: Decimal,
) -> HousingCompanyImprovementCalculationResult:
    value = completion_date_acquisition_price / total_acquisition_price * improvement.value

    #
    # Return the result
    #
    return HousingCompanyImprovementCalculationResult(
        name=improvement.name,
        value=improvement.value,
        value_for_apartment=value,
    )


def calculate_multiple_housing_company_improvements(
    improvements,
    calc_fn: Callable[[ImprovementData], HousingCompanyImprovementCalculationResult],
) -> HousingCompanyImprovementsResult:
    results: List[HousingCompanyImprovementCalculationResult] = []

    summary_value = Decimal(0)
    summary_value_for_apartment = Decimal(0)

    # Calculate result for each improvement and calculate the summary
    for improvement in improvements:
        result = calc_fn(improvement)

        # Summary calculation
        summary_value += result.value
        summary_value_for_apartment += result.value_for_apartment

        results.append(result)

    # Generate summary report
    summary = HousingCompanyImprovementCalculationSummary(
        value=summary_value,
        value_for_apartment=summary_value_for_apartment,
    )

    return HousingCompanyImprovementsResult(items=results, summary=summary)


def calculate_additional_work(
    improvement: ImprovementData,
    calculation_date: datetime.date,
    calculation_date_index: Decimal,
):
    if improvement.completion_date_index is None or calculation_date_index is None:
        raise IndexMissingException()

    # Adjust the accepted value with the index check
    accepted = improvement.value * calculation_date_index / improvement.completion_date_index

    #
    # Return the result
    #
    return ApartmentImprovementCalculationResult(
        name=improvement.name,
        value=improvement.value,
        completion_date=improvement.completion_date,
        calculation_date_index=calculation_date_index,
        completion_date_index=improvement.completion_date_index,
        index_adjusted=accepted,
        depreciation=ApartmentImprovementCalculationResult.Depreciation(
            time=ApartmentImprovementCalculationResult.Depreciation.DepreciationTime.create(
                months_between_dates(improvement.completion_date, calculation_date)
            ),
            amount=Decimal(0),
            percentage=Decimal(0),
        ),
        value_for_apartment=accepted,
    )
