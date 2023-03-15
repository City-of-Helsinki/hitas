import datetime
from decimal import Decimal

from hitas.calculations.improvements.common import ImprovementData
from hitas.calculations.improvements.rules_pre_2011_cpi import (
    calculate_apartment_improvements_pre_2011_construction_price_index,
    calculate_single_apartment_improvement_pre_2011_construction_price_index,
)


def test_calculate__single_improvement__apartment__pre_2011__construction_price_index():
    improvement = ImprovementData(
        name="Test improvement",
        value=Decimal(150_000),
        completion_date=datetime.date(2020, 5, 1),
        completion_date_index=Decimal(50.0),
        depreciation_percentage=Decimal(10.0),
    )

    result = calculate_single_apartment_improvement_pre_2011_construction_price_index(
        improvement, calculation_date_index=Decimal(100.0), calculation_date=datetime.date(2022, 6, 1)
    )

    assert result is not None

    # Verify item
    assert result.name == improvement.name
    assert result.value == improvement.value
    assert result.completion_date == improvement.completion_date
    assert result.completion_date_index == improvement.completion_date_index
    assert result.index_adjusted == 300_000  # 100 / 50 * 150_000
    assert result.depreciation is not None
    assert result.depreciation.amount == 62_500  # (100 * 150_000 * 25 * 0.1) / (50 * 12)
    assert result.depreciation.time is not None
    assert result.depreciation.time.years == 2
    assert result.depreciation.time.months == 1
    assert result.depreciation.percentage == 10
    assert result.value_for_apartment == 237_500


def test_calculate__multiple_improvements__apartment__pre_2011__construction_price_index():
    improvement = ImprovementData(
        name="Test improvement",
        value=Decimal(150_000),
        completion_date=datetime.date(2020, 5, 1),
        completion_date_index=Decimal(50.0),
        depreciation_percentage=Decimal(10.0),
    )

    result = calculate_apartment_improvements_pre_2011_construction_price_index(
        [improvement, improvement], calculation_date_index=Decimal(100.0), calculation_date=datetime.date(2022, 6, 1)
    )

    assert result is not None

    # Verify item
    assert len(result.items) == 2
    assert result.items[0].name == improvement.name
    assert result.items[0].value == improvement.value
    assert result.items[0].completion_date == improvement.completion_date
    assert result.items[0].completion_date_index == improvement.completion_date_index
    assert result.items[0].index_adjusted == 300_000  # 100 / 50 * 150_000
    assert result.items[0].depreciation is not None
    assert result.items[0].depreciation.amount == 62_500  # (100 * 150_000 * 25 * 0.1) / (50 * 12)
    assert result.items[0].depreciation.time is not None
    assert result.items[0].depreciation.time.years == 2
    assert result.items[0].depreciation.time.months == 1
    assert result.items[0].depreciation.percentage == 10
    assert result.items[0].value_for_apartment == 237_500

    # Verify summary
    assert result.summary is not None
    assert result.summary.value == 300_000
    assert result.summary.index_adjusted == 600_000
    assert result.summary.depreciation == 125_000
    assert result.summary.value_for_apartment == 475_000
