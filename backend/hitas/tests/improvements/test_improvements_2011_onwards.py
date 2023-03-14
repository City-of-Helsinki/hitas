import datetime
from decimal import Decimal

from hitas.calculations.improvements.common import ImprovementData
from hitas.calculations.improvements.rules_2011_onwards import (
    calculate_housing_company_improvements_2011_onwards,
    calculate_single_housing_company_improvement_2011_onwards,
)
from hitas.utils import roundup


def test_calculate__single_improvement__housing_company__2011_onwards():
    improvement = ImprovementData(
        name="Test improvement",
        value=Decimal(150_000),
        completion_date=datetime.date(2020, 5, 1),
        completion_date_index=Decimal(129.2),
    )

    result = calculate_single_housing_company_improvement_2011_onwards(
        improvement,
        calculation_date_index=Decimal(146.4),
        total_surface_area=Decimal(4332),
        apartment_surface_area=Decimal(30),
        calculation_date=datetime.date(2023, 1, 1),
        index_name="foo",
    )
    assert result is not None

    # Verify item
    assert result.name == improvement.name
    assert result.value == improvement.value
    assert result.completion_date == improvement.completion_date
    assert result.value_added == 20_040
    assert roundup(result.value_for_apartment) == Decimal("157.26")
    assert roundup(result.value_for_housing_company) == Decimal("22_707.86")


def test_calculate__multiple_improvements__housing_company__2011_onwards():
    improvement = ImprovementData(
        name="Test improvement",
        value=Decimal(150_000),
        completion_date=datetime.date(2020, 5, 1),
        completion_date_index=Decimal(129.2),
    )

    result = calculate_housing_company_improvements_2011_onwards(
        improvements=[improvement, improvement],
        calculation_date_index=Decimal(146.4),
        total_surface_area=Decimal(4332),
        apartment_surface_area=Decimal(30),
        calculation_date=datetime.date(2023, 1, 1),
        index_name="foo",
    )
    assert result is not None

    # Verify single item
    assert len(result.items) == 2
    assert result.items[0].name == improvement.name
    assert result.items[0].value == improvement.value
    assert result.items[0].completion_date == improvement.completion_date
    assert result.items[0].value_added == 20_040
    assert roundup(result.items[0].value_for_apartment) == Decimal("157.26")
    assert roundup(result.items[0].value_for_housing_company) == Decimal("22_707.86")

    # Verify summary
    assert result.summary is not None
    assert result.summary.value == 300_000
    assert result.summary.value_added == 40_080
    assert result.summary.excess is not None
    assert result.summary.excess.total == 129960
    assert result.summary.excess.value_per_square_meter == 30.0
    assert result.summary.excess.surface_area == 4332
    assert roundup(result.summary.value_for_housing_company) == Decimal("45_415.73")
    assert roundup(result.summary.value_for_apartment) == Decimal("314.51")
