import datetime
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from hitas.calculations.exceptions import IndexMissingException
from hitas.calculations.helpers import NoneSum, months_between_dates


@dataclass
class ImprovementData:
    # Name of the improvement
    name: str
    # Original value of the improvement
    value: int
    # Completion date of the improvement
    completion_date: datetime.date
    # Completion date index for this improvement. Not needed for all the calculations.
    completion_date_index: Optional[Decimal] = None
    # Depreciation percentage for this improvement. Not needed for all the calculations.
    deprecation_percentage: Optional[Decimal] = None


class Excess(Enum):
    AFTER_2010_HOUSING_COMPANY = 30
    BEFORE_2010_HOUSING_COMPANY = 150
    BEFORE_2010_APARTMENT = 100


@dataclass
class ImprovementCalculationResult:
    @dataclass
    class Depreciation:
        # How many months depreciation has occurred
        time_months: int
        # The total depreciation amount
        amount: Decimal
        # Percentage
        percentage: Optional[Decimal]

    # Name for the improvement
    name: str
    # Original value for the improvement
    value: int
    # When the improvement was completed
    completion_date: datetime.date
    # Calculated excess for the improvement or None when excess is not used in the calculation
    excess: Optional[Decimal]
    # Calculated value added by the improvement (original value - the excess)
    value_added: Decimal
    # Deprecation information or None when depreciation is not used in the calculation
    depreciation: Optional[Depreciation]
    # Improvement value for the whole housing company when the improvement is housing company improvement.
    # None when the improvement is an apartment improvement.
    improvement_value_for_housing_company: Optional[Decimal]
    # Improvement share of a housing company's improvement value OR the whole value when the improvement
    # is an apartment improvement.
    improvement_value_for_apartment: Decimal


@dataclass
class ImprovementCalculationSummary:
    @dataclass
    class ExcessSummary:
        surface_area: Decimal
        value_per_square_meter: int

        @property
        def total(self) -> Decimal:
            return self.surface_area * self.value_per_square_meter

    # Sum of all improvement values
    value: int
    # Sum of all improvement added values (value - excess)
    value_added: Decimal
    # Excess information (if part of the calculations)
    excess: Optional[ExcessSummary]
    # Sum of all depreciation (if part of the calculations)
    depreciation: Optional[Decimal]
    # Sum of all improvement values for the whole housing company when the improvements are housing company
    # improvements. None when the improvements are apartment improvements.
    improvement_value_for_housing_company: Optional[Decimal]
    # Sum of all improvement share of a housing company's improvements values OR the whole value when the improvements
    # are apartment improvements.
    improvement_value_for_apartment: Decimal


@dataclass
class ImprovementsResult:
    items: List[ImprovementCalculationResult]
    summary: ImprovementCalculationSummary


@dataclass
class ExcessCalc:
    excess_per_square_meter: Excess
    square_meters: Decimal


@dataclass
class IndexCalc:
    calculation_date_index: Decimal
    completion_date_index: Decimal


@dataclass
class DepreciationCalc:
    total_months: Optional[int]
    calculation_date: datetime.date
    percentage: Optional[Decimal]


@dataclass
class ApartmentShare:
    total_surface_area: Decimal
    apartment_surface_area: Decimal


def calculate_housing_company_improvements_after_2010(
    improvements: List[ImprovementData],
    calculation_date_index: Decimal,
    total_surface_area: Decimal,
    apartment_surface_area: Decimal,
) -> ImprovementsResult:
    def calc_fn(improvement):
        return calculate_single_housing_company_improvement_after_2010(
            improvement,
            calculation_date_index=calculation_date_index,
            total_surface_area=total_surface_area,
            apartment_surface_area=apartment_surface_area,
        )

    return calculate_multiple_improvements(
        improvements, calc_fn, total_surface_area, excess_per_square_meter=Excess.AFTER_2010_HOUSING_COMPANY
    )


def calculate_single_housing_company_improvement_after_2010(
    improvement: ImprovementData,
    calculation_date_index: Decimal,
    total_surface_area: Decimal,
    apartment_surface_area: Decimal,
) -> ImprovementCalculationResult:
    return calculate_improvement(
        improvement,
        excess=ExcessCalc(excess_per_square_meter=Excess.AFTER_2010_HOUSING_COMPANY, square_meters=total_surface_area),
        depreciation=None,
        index_check=IndexCalc(
            calculation_date_index=calculation_date_index, completion_date_index=improvement.completion_date_index
        ),
        apartment_share=ApartmentShare(
            total_surface_area=total_surface_area, apartment_surface_area=apartment_surface_area
        ),
    )


def calculate_improvement(
    improvement: ImprovementData,
    excess: Optional[ExcessCalc],
    depreciation: Optional[DepreciationCalc],
    index_check: Optional[IndexCalc],
    apartment_share: Optional[ApartmentShare],
) -> ImprovementCalculationResult:
    deprecation_result = None

    if index_check and (index_check.completion_date_index is None or index_check.calculation_date_index is None):
        raise IndexMissingException()

    #
    # Calculate the excess
    #
    if excess:
        # Calculate value addition by calculating the excess ('omavastuu') first and then reducing that from the
        # improvement's value. Value addition must be always >= 0.
        excess_amount = excess.excess_per_square_meter.value * excess.square_meters
        value_addition = max(improvement.value - excess_amount, Decimal(0))
    else:
        # Value addition always equals to improvement's value when excess is not calculated
        excess_amount = None
        value_addition = improvement.value

    #
    # Calculate the depreciation ('poistot')
    #
    if depreciation and depreciation.total_months is not None:
        # Check how many months has elapsed since the completion of the improvement
        depreciation_time_months = months_between_dates(improvement.completion_date, depreciation.calculation_date)

        if depreciation_time_months > depreciation.total_months:
            # Time has passed more than the total depreciation time so the full value is depreciated
            depreciation_amount = value_addition
        else:
            # Calculate the depreciation amount
            depreciation_amount = Decimal(value_addition) / depreciation.total_months * depreciation_time_months

        deprecation_result = ImprovementCalculationResult.Depreciation(
            time_months=depreciation_time_months, amount=depreciation_amount, percentage=None
        )
    else:
        # set depreciation amount to 0 to help with the next calculations
        depreciation_amount = 0

    #
    # Calculate the accepted value ('hyväksytty') for this improvement
    #
    accepted = value_addition - depreciation_amount

    if index_check:
        # Adjust the accepted value with the index check
        accepted *= index_check.calculation_date_index / index_check.completion_date_index

    if depreciation and improvement.deprecation_percentage:
        depreciation_time_months = months_between_dates(improvement.completion_date, depreciation.calculation_date)
        depreciation_amount = min(accepted * depreciation.percentage * depreciation_time_months, accepted)

        deprecation_result = ImprovementCalculationResult.Depreciation(
            time_months=depreciation_time_months, amount=depreciation_amount, percentage=depreciation.percentage
        )

    #
    # Calculate the housing company's and apartment's share
    #
    if apartment_share:
        # This is a housing company improvement so set the accepted value only for the housing company
        # and calculate the apartment's share
        improvement_share_for_housing_company = accepted
        improvement_share_for_apartment = (
            improvement_share_for_housing_company
            / apartment_share.total_surface_area
            * apartment_share.apartment_surface_area
        )
    else:
        # This is an apartment improvement so set the accepted value only for the apartment
        improvement_share_for_housing_company = None
        improvement_share_for_apartment = accepted

    #
    # Return the result
    #
    return ImprovementCalculationResult(
        name=improvement.name,
        value=improvement.value,
        completion_date=improvement.completion_date,
        excess=excess_amount,
        value_added=value_addition,
        depreciation=deprecation_result,
        improvement_value_for_housing_company=improvement_share_for_housing_company,
        improvement_value_for_apartment=improvement_share_for_apartment,
    )


def calculate_multiple_improvements(improvements, calc_fn, total_surface_area, excess_per_square_meter):
    results: List[ImprovementCalculationResult] = []

    summary_value = 0
    summary_value_added = Decimal(0)
    summary_value_for_housing_company = NoneSum(Decimal)
    summary_value_for_apartment = Decimal(0)
    summary_depreciation = NoneSum(Decimal)

    # Calculate result for each improvement and calculate the summary
    for improvement in improvements:
        result = calc_fn(improvement)

        # Summary calculation
        summary_value += result.value
        summary_value_added += result.value_added
        summary_value_for_housing_company += result.improvement_value_for_housing_company
        summary_value_for_apartment += result.improvement_value_for_apartment
        summary_depreciation += result.depreciation.amount if result.depreciation else None

        results.append(result)

    # Generate summary report
    summary = ImprovementCalculationSummary(
        value=summary_value,
        value_added=summary_value_added,
        depreciation=summary_depreciation.value,
        excess=ImprovementCalculationSummary.ExcessSummary(
            surface_area=total_surface_area,
            value_per_square_meter=excess_per_square_meter.value,
        ),
        improvement_value_for_housing_company=summary_value_for_housing_company.value,
        improvement_value_for_apartment=summary_value_for_apartment,
    )

    return ImprovementsResult(items=results, summary=summary)
