from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Callable, List

from hitas.calculations.exceptions import IndexMissingException
from hitas.calculations.improvements.common import Excess, ImprovementData


@dataclass
class ImprovementCalculationResult:
    # Name for the improvement
    name: str
    # Original value for the improvement
    value: Decimal
    # When the improvement was completed
    completion_date: datetime.date
    # Calculated value added by the improvement (original value - the excess)
    value_added: Decimal
    # Improvement values for the whole housing company
    value_for_housing_company: Decimal
    # Improvement share of a housing company's improvement value
    value_for_apartment: Decimal


@dataclass
class ImprovementCalculationSummary:
    @dataclass
    class ExcessSummary:
        surface_area: Decimal
        value_per_square_meter: Decimal
        total: Decimal

    # Sum of all improvement values
    value: Decimal
    # Sum of all improvement added values (value - excess)
    value_added: Decimal
    # Excess information
    excess: ExcessSummary
    # Sum of all improvement values for the whole housing company
    value_for_housing_company: Decimal
    # Sum of all improvement shares of a housing company's improvements
    value_for_apartment: Decimal


@dataclass
class ImprovementsResult:
    items: List[ImprovementCalculationResult]
    summary: ImprovementCalculationSummary


def calculate_housing_company_improvements_2011_onwards(
    improvements: List[ImprovementData],
    calculation_date_index: Decimal,
    total_surface_area: Decimal,
    apartment_surface_area: Decimal,
    calculation_date: datetime.date,
    index_name: str,
) -> ImprovementsResult:
    def calc_fn(improvement):
        return calculate_single_housing_company_improvement_2011_onwards(
            improvement,
            calculation_date_index=calculation_date_index,
            total_surface_area=total_surface_area,
            apartment_surface_area=apartment_surface_area,
            calculation_date=calculation_date,
            index_name=index_name,
        )

    return calculate_multiple_improvements(improvements, calc_fn, total_surface_area)


def calculate_single_housing_company_improvement_2011_onwards(
    improvement: ImprovementData,
    calculation_date_index: Decimal,
    total_surface_area: Decimal,
    apartment_surface_area: Decimal,
    calculation_date: datetime.date,
    index_name: str,
) -> ImprovementCalculationResult:
    if improvement.completion_date_index is None:
        raise IndexMissingException(error_code=index_name, date=improvement.completion_date)
    if calculation_date_index is None:
        raise IndexMissingException(error_code=index_name, date=calculation_date)

    #
    # Calculate the excess
    #

    # Calculate value addition by calculating the excess ('omavastuu') first and then reducing that from the
    # improvement's value. Value addition must be always >= 0.
    excess_amount = Excess.AFTER_2010_HOUSING_COMPANY.value * total_surface_area
    value_addition = max(improvement.value - excess_amount, Decimal(0))

    #
    # Calculate the accepted value ('hyväksytty') for this improvement
    #
    accepted = value_addition

    # Adjust the accepted value with the index check
    accepted *= calculation_date_index / improvement.completion_date_index

    #
    # Calculate the housing company's and apartment's share
    #

    # This is a housing company improvement so set the accepted value only for the housing company
    # and calculate the apartment's share
    improvement_share_for_apartment = accepted / total_surface_area * apartment_surface_area

    #
    # Return the result
    #
    return ImprovementCalculationResult(
        name=improvement.name,
        value=improvement.value,
        completion_date=improvement.completion_date,
        value_added=value_addition,
        value_for_housing_company=accepted,
        value_for_apartment=improvement_share_for_apartment,
    )


def calculate_multiple_improvements(
    improvements,
    calc_fn: Callable[[ImprovementData], ImprovementCalculationResult],
    total_surface_area: Decimal,
) -> ImprovementsResult:
    results: List[ImprovementCalculationResult] = []

    summary_value = Decimal(0)
    summary_value_added = Decimal(0)
    summary_value_for_housing_company = Decimal(0)
    summary_value_for_apartment = Decimal(0)

    # Calculate result for each improvement and calculate the summary
    for improvement in improvements:
        result = calc_fn(improvement)

        # Summary calculation
        summary_value += result.value
        summary_value_added += result.value_added
        summary_value_for_housing_company += result.value_for_housing_company
        summary_value_for_apartment += result.value_for_apartment

        results.append(result)

    # Generate summary report
    summary = ImprovementCalculationSummary(
        value=summary_value,
        value_added=summary_value_added,
        excess=ImprovementCalculationSummary.ExcessSummary(
            surface_area=total_surface_area,
            value_per_square_meter=Excess.AFTER_2010_HOUSING_COMPANY.value,
            total=total_surface_area * Excess.AFTER_2010_HOUSING_COMPANY.value,
        ),
        value_for_housing_company=summary_value_for_housing_company,
        value_for_apartment=summary_value_for_apartment,
    )

    return ImprovementsResult(items=results, summary=summary)
