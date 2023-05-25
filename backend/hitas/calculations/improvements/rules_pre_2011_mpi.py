import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import Callable, List, Optional

from hitas.calculations.exceptions import IndexMissingException, InvalidCalculationResultException
from hitas.calculations.helpers import months_between_dates
from hitas.calculations.improvements.common import Excess, ImprovementData
from hitas.calculations.improvements.rules_2011_onwards import calculate_single_housing_company_improvement_2011_onwards


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
        # The depreciation amount reduced
        amount: Decimal

    # Name for the improvement
    name: str
    # Original value for the improvement
    value: Decimal
    # When the improvement was completed
    completion_date: datetime.date
    # Improvement's value with excess reduced
    value_without_excess: Decimal
    # The depreciation information
    depreciation: Depreciation
    # Final accepted value for the improvement
    accepted_value: Decimal
    # Should this improvement be exempt from all deductions (excess, deprecation)
    no_deductions: Optional[bool] = False


@dataclass
class ApartmentImprovementCalculationSummary:
    @dataclass
    class ExcessSummary:
        # Apartment's surface area
        surface_area: Decimal
        # Excess amount per square meter
        value_per_square_meter: Decimal
        # Total excess amount (surface area * value per square meter)
        total: Decimal

    # Total sum of all improvements' original values
    value: Decimal
    # Total sum of all improvements' value with excess reduced
    value_without_excess: Decimal
    # Total sum of all improvements' depreciation amounts
    depreciation: Decimal
    # Excess information
    excess: ExcessSummary
    # Total sum of all improvement's accepted values
    accepted_value: Decimal


@dataclass
class ApartmentImprovementsResult:
    items: List[ApartmentImprovementCalculationResult]
    summary: ApartmentImprovementCalculationSummary


def calculate_apartment_improvements_pre_2011_market_price_index(
    improvements: List[ImprovementData],
    calculation_date: datetime.date,
    calculation_date_index: Decimal,
    apartment_surface_area: Decimal,
) -> ApartmentImprovementsResult:
    def calc_fn(improvement):
        return calculate_single_apartment_improvement_pre_2011_market_price_index(
            improvement,
            calculation_date=calculation_date,
            calculation_date_index=calculation_date_index,
            apartment_surface_area=apartment_surface_area,
        )

    return calculate_multiple_apartment_improvements(improvements, calc_fn, apartment_surface_area)


def calculate_single_apartment_improvement_pre_2011_market_price_index(
    improvement: ImprovementData,
    calculation_date: datetime.date,
    calculation_date_index: Decimal,
    apartment_surface_area: Decimal,
) -> ApartmentImprovementCalculationResult:
    if improvement.completion_date_index is None:
        raise IndexMissingException(error_code="mpi", date=improvement.completion_date)

    # In a few cases the improvement value should be fully accepted without any deductions.
    if improvement.no_deductions:
        index_adjusted = improvement.value * calculation_date_index / improvement.completion_date_index
        return ApartmentImprovementCalculationResult(
            name=improvement.name,
            value=improvement.value,
            completion_date=improvement.completion_date,
            value_without_excess=index_adjusted,
            depreciation=ApartmentImprovementCalculationResult.Depreciation(
                time=ApartmentImprovementCalculationResult.Depreciation.DepreciationTime.create(0),
                amount=Decimal(0),
            ),
            accepted_value=index_adjusted,
            no_deductions=improvement.no_deductions,
        )

    #
    # Calculate the excess
    #
    # Calculate value addition by calculating the excess ('omavastuu') first and then reducing that from the
    # improvement's value. Value without excess must be always >= 0.
    excess_amount = Excess.BEFORE_2010_APARTMENT.value * apartment_surface_area
    value_without_excess = max(improvement.value - excess_amount, Decimal(0))

    #
    # Calculate the depreciation ('poistot')
    #
    # Check how many months has elapsed since the completion of the improvement
    depreciation_time_months = months_between_dates(improvement.completion_date, calculation_date)

    if depreciation_time_months > 10 * 12:
        # Time has passed more than the total depreciation time so the full value is depreciated
        depreciation_amount = value_without_excess
    else:
        # Calculate the depreciation amount
        depreciation_amount = value_without_excess / (10 * 12) * depreciation_time_months

    depreciation_result = ApartmentImprovementCalculationResult.Depreciation(
        time=ApartmentImprovementCalculationResult.Depreciation.DepreciationTime.create(depreciation_time_months),
        amount=depreciation_amount,
    )

    #
    # Calculate the accepted value ('hyväksytty') for this improvement
    #
    accepted = value_without_excess - depreciation_amount

    #
    # Return the result
    #
    return ApartmentImprovementCalculationResult(
        name=improvement.name,
        value=improvement.value,
        completion_date=improvement.completion_date,
        value_without_excess=value_without_excess,
        depreciation=depreciation_result,
        accepted_value=accepted,
        no_deductions=False,
    )


def calculate_multiple_apartment_improvements(
    improvements,
    calc_fn: Callable[[ImprovementData], ApartmentImprovementCalculationResult],
    apartment_surface_area: Decimal,
) -> ApartmentImprovementsResult:
    results: List[ApartmentImprovementCalculationResult] = []

    summary_value = Decimal(0)
    summary_value_without_excess = Decimal(0)
    summary_depreciation = Decimal(0)
    summary_accepted_value = Decimal(0)

    # Calculate result for each improvement and calculate the summary
    for improvement in improvements:
        result = calc_fn(improvement)

        # Summary calculation
        summary_value += result.value
        summary_value_without_excess += result.value_without_excess
        summary_depreciation += result.depreciation.amount
        summary_accepted_value += result.accepted_value

        results.append(result)

    # Generate summary report
    summary = ApartmentImprovementCalculationSummary(
        value=summary_value,
        value_without_excess=summary_value_without_excess,
        depreciation=summary_depreciation,
        excess=ApartmentImprovementCalculationSummary.ExcessSummary(
            surface_area=apartment_surface_area,
            value_per_square_meter=Excess.BEFORE_2010_APARTMENT.value,
            total=apartment_surface_area * Excess.BEFORE_2010_APARTMENT.value,
        ),
        accepted_value=summary_accepted_value,
    )

    return ApartmentImprovementsResult(items=results, summary=summary)


#
# Housing company
#


@dataclass
class HousingCompanyImprovementCalculationResult(ApartmentImprovementCalculationResult):
    # Final accepted value for the whole housing company
    accepted_value_for_housing_company: Decimal = Decimal("0")


@dataclass
class HousingCompanyImprovementCalculationSummary(ApartmentImprovementCalculationSummary):
    @dataclass
    class ExcessSummary:
        # Apartment's surface area
        surface_area: Decimal
        # Excess amount per square meter before 2010/01/01, null if not used
        value_per_square_meter_before_2010: Optional[Decimal]
        # Excess amount per square meter on or after 2010/01/01, null if not used
        value_per_square_meter_after_2010: Optional[Decimal]
        # Total excess amount before 2010 (surface area * value per square meter), null if not used
        total_before_2010: Optional[Decimal]
        # Total excess amount on or after 2010 (surface area * value per square meter), null if not used
        total_after_2010: Optional[Decimal]

    # Final accepted value for the whole housing company
    accepted_value_for_housing_company: Decimal


@dataclass
class HousingCompanyImprovementsResult:
    items: List[HousingCompanyImprovementCalculationResult]
    summary: HousingCompanyImprovementCalculationSummary


def calculate_housing_company_improvements_pre_2011_market_price_index(
    improvements: List[ImprovementData],
    calculation_date: datetime.date,
    calculation_date_index: Decimal,
    total_surface_area: Decimal,
    apartment_surface_area: Decimal,
    housing_company_shares_count: int,
    apartment_shares_count: int,
) -> HousingCompanyImprovementsResult:
    def calc_fn(improvement: ImprovementData) -> HousingCompanyImprovementCalculationResult:
        return calculate_single_housing_company_improvement_pre_2011_market_price_index(
            improvement,
            calculation_date=calculation_date,
            calculation_date_index=calculation_date_index,
            total_surface_area=total_surface_area,
            apartment_surface_area=apartment_surface_area,
            housing_company_shares_count=housing_company_shares_count,
            apartment_shares_count=apartment_shares_count,
        )

    return calculate_multiple_housing_company_improvements(improvements, calc_fn, total_surface_area)


def calculate_single_housing_company_improvement_pre_2011_market_price_index(
    improvement: ImprovementData,
    calculation_date: datetime.date,
    calculation_date_index: Decimal,
    total_surface_area: Decimal,
    apartment_surface_area: Decimal,
    housing_company_shares_count: int,
    apartment_shares_count: int,
) -> HousingCompanyImprovementCalculationResult:
    if improvement.completion_date_index is None:
        raise IndexMissingException(error_code="mpi", date=improvement.completion_date)

    # In a few cases the improvement value should be fully accepted without any deductions.
    if improvement.no_deductions:
        if not apartment_shares_count:
            raise InvalidCalculationResultException(error_code="missing_shares_count")

        index_adjusted = improvement.value * calculation_date_index / improvement.completion_date_index
        return HousingCompanyImprovementCalculationResult(
            name=improvement.name,
            value=improvement.value,
            completion_date=improvement.completion_date,
            value_without_excess=index_adjusted,
            depreciation=ApartmentImprovementCalculationResult.Depreciation(
                time=HousingCompanyImprovementCalculationResult.Depreciation.DepreciationTime.create(0),
                amount=Decimal(0),
            ),
            accepted_value_for_housing_company=index_adjusted,
            accepted_value=index_adjusted / housing_company_shares_count * apartment_shares_count,
            no_deductions=improvement.no_deductions,
        )

    if improvement.completion_date < datetime.date(2010, 1, 1):
        #
        # Calculate the excess
        #

        # Calculate value addition by calculating the excess ('omavastuu') first and then reducing that from the
        # improvement's value. Value without excess must be always >= 0.
        excess_amount = Excess.BEFORE_2010_HOUSING_COMPANY.value * total_surface_area
        value_without_excess = max(improvement.value - excess_amount, Decimal(0))

        #
        # Calculate the depreciation ('poistot')
        #
        # Check how many months has elapsed since the completion of the improvement
        depreciation_time_months = months_between_dates(improvement.completion_date, calculation_date)

        if depreciation_time_months > 15 * 12:
            # Time has passed more than the total depreciation time so the full value is depreciated
            depreciation_amount = value_without_excess
        else:
            # Calculate the depreciation amount
            depreciation_amount = value_without_excess / (15 * 12) * depreciation_time_months

        depreciation_result = ApartmentImprovementCalculationResult.Depreciation(
            time=ApartmentImprovementCalculationResult.Depreciation.DepreciationTime.create(
                depreciation_time_months if depreciation_amount > 0 else 0
            ),
            amount=depreciation_amount,
        )

        #
        # Calculate the accepted value ('hyväksytty') for this improvement
        #
        accepted = value_without_excess - depreciation_amount

        #
        # Calculate the housing company's and apartment's share
        #

        # This is a housing company improvement so set the accepted value only for the housing company
        # and calculate the apartment's share
        improvement_share_for_apartment = accepted / total_surface_area * apartment_surface_area

        #
        # Return the result
        #
        return HousingCompanyImprovementCalculationResult(
            name=improvement.name,
            value=improvement.value,
            completion_date=improvement.completion_date,
            value_without_excess=value_without_excess,
            depreciation=depreciation_result,
            accepted_value_for_housing_company=accepted,
            accepted_value=improvement_share_for_apartment,
        )
    else:
        # Use 2011 calculations as it's the same as this
        result = calculate_single_housing_company_improvement_2011_onwards(
            improvement, calculation_date_index, total_surface_area, apartment_surface_area, calculation_date, "mpi"
        )
        return HousingCompanyImprovementCalculationResult(
            name=result.name,
            value=result.value,
            completion_date=result.completion_date,
            value_without_excess=result.value_added,
            depreciation=ApartmentImprovementCalculationResult.Depreciation(
                time=ApartmentImprovementCalculationResult.Depreciation.DepreciationTime(years=0, months=0),
                amount=Decimal(0),
            ),
            accepted_value=result.value_for_apartment,
            accepted_value_for_housing_company=result.value_for_housing_company,
        )


def calculate_multiple_housing_company_improvements(
    improvements: List[ImprovementData],
    calc_fn: Callable[[ImprovementData], HousingCompanyImprovementCalculationResult],
    housing_company_surface_area: Decimal,
) -> HousingCompanyImprovementsResult:
    results: List[HousingCompanyImprovementCalculationResult] = []

    summary_value = Decimal(0)
    summary_value_without_excess = Decimal(0)
    summary_depreciation = Decimal(0)
    summary_accepted_value = Decimal(0)
    summary_accepted_value_for_housing_company = Decimal(0)

    has_improvements_before_2010: bool = False
    has_improvements_after_2010: bool = False

    # Calculate result for each improvement and calculate the summary
    for improvement in improvements:
        result = calc_fn(improvement)

        # Summary calculation
        summary_value += result.value
        summary_value_without_excess += result.value_without_excess
        summary_depreciation += result.depreciation.amount
        summary_accepted_value_for_housing_company += result.accepted_value_for_housing_company
        summary_accepted_value += result.accepted_value

        if result.completion_date >= datetime.date(2010, 1, 1):
            has_improvements_after_2010 = True
        else:
            has_improvements_before_2010 = True

        results.append(result)

    # Generate summary report
    summary = HousingCompanyImprovementCalculationSummary(
        value=summary_value,
        value_without_excess=summary_value_without_excess,
        depreciation=summary_depreciation,
        excess=HousingCompanyImprovementCalculationSummary.ExcessSummary(
            surface_area=housing_company_surface_area,
            value_per_square_meter_before_2010=(
                Excess.BEFORE_2010_HOUSING_COMPANY.value if has_improvements_before_2010 else None
            ),
            value_per_square_meter_after_2010=(
                Excess.AFTER_2010_HOUSING_COMPANY.value if has_improvements_after_2010 else None
            ),
            total_before_2010=(
                housing_company_surface_area * Excess.BEFORE_2010_HOUSING_COMPANY.value
                if has_improvements_before_2010
                else None
            ),
            total_after_2010=(
                housing_company_surface_area * Excess.AFTER_2010_HOUSING_COMPANY.value
                if has_improvements_after_2010
                else None
            ),
        ),
        accepted_value=summary_accepted_value,
        accepted_value_for_housing_company=summary_accepted_value_for_housing_company,
    )

    return HousingCompanyImprovementsResult(items=results, summary=summary)
