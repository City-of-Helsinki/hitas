import datetime
from dataclasses import dataclass
from decimal import Decimal

from hitas.calculations.improvement import (
    ImprovementData,
    calculate_housing_company_improvements_after_2010,
    calculate_single_housing_company_improvement_after_2010,
)
from hitas.calculations.max_price import roundup


@dataclass
class ImprovementCalculationRequest:
    value: int
    completion_date_index: Decimal
    completion_date: datetime.date


def test_calculate_single_housing_company_improvement_after_2010():
    result = calculate_single_housing_company_improvement_after_2010(
        ImprovementData(
            name="Testi",
            value=150_000,
            completion_date=datetime.date(2020, 5, 1),
            completion_date_index=Decimal(129.2),
        ),
        calculation_date_index=Decimal(146.4),
        total_surface_area=Decimal(4332),
        apartment_surface_area=Decimal(30),
    )
    assert result is not None
    assert result.value == 150_000
    assert result.completion_date == datetime.date(2020, 5, 1)
    assert result.value_added == 20_040
    assert result.depreciation is None
    assert roundup(result.improvement_value_for_housing_company) == Decimal(22_707.86)
    assert roundup(result.improvement_value_for_apartment) == Decimal(157.26)


def test_calculate_housing_company_improvements_after_2010():
    result = calculate_housing_company_improvements_after_2010(
        improvements=[
            ImprovementData(
                name="Testi",
                value=150_000,
                completion_date=datetime.date(2020, 5, 1),
                completion_date_index=Decimal(129.2),
            )
        ],
        calculation_date_index=Decimal(146.4),
        total_surface_area=Decimal(4332),
        apartment_surface_area=Decimal(30),
    )
    assert result is not None
    assert len(result.items) == 1

    # Verify summary
    assert result.summary is not None
    assert result.summary.value == 150_000
    assert result.summary.value_added == 20_040
    assert result.summary.excess is not None
    assert result.summary.excess.total == 129960
    assert result.summary.excess.value_per_square_meter == 30
    assert result.summary.excess.surface_area == 4332
    assert result.summary.depreciation is None
    assert roundup(result.summary.improvement_value_for_housing_company) == Decimal(22_707.86)
    assert roundup(result.summary.improvement_value_for_apartment) == Decimal(157.26)
