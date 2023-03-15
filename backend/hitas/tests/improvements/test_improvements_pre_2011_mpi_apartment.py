import datetime
from decimal import Decimal

from hitas.calculations.improvements.common import ImprovementData
from hitas.calculations.improvements.rules_pre_2011_mpi import (
    calculate_apartment_improvements_pre_2011_market_price_index,
    calculate_single_apartment_improvement_pre_2011_market_price_index,
)
from hitas.utils import roundup


def test_calculate__single_improvement__apartment__pre_2011__market_price_index():
    improvement = ImprovementData(
        name="Test improvement",
        value=Decimal(150_000),
        completion_date=datetime.date(2009, 5, 1),
        completion_date_index=Decimal(129.2),
    )

    result = calculate_single_apartment_improvement_pre_2011_market_price_index(
        improvement,
        calculation_date=datetime.date(2022, 5, 1),
        calculation_date_index=Decimal(100.0),
        apartment_surface_area=Decimal(20.0),
    )

    assert result is not None

    # Verify item
    assert result.name == improvement.name
    assert result.value == improvement.value
    assert result.completion_date == improvement.completion_date
    assert result.value_without_excess == 148_000  # 150_000 - 20 * 100
    assert result.depreciation is not None
    assert result.depreciation.amount == 148_000  # 148_000 / (15 * 12) * (12 * 13)
    assert result.depreciation.time is not None
    assert result.depreciation.time.years == 13
    assert result.depreciation.time.months == 0
    assert roundup(result.accepted_value) == 0  # 18_000 / 100 * 20


def test_calculate__multiple_improvements__apartment__pre_2011__market_price_index():
    improvement = ImprovementData(
        name="Test improvement",
        value=Decimal(150_000),
        completion_date=datetime.date(2009, 5, 1),
        completion_date_index=Decimal(129.2),
    )

    result = calculate_apartment_improvements_pre_2011_market_price_index(
        [improvement, improvement],
        calculation_date=datetime.date(2022, 5, 1),
        calculation_date_index=Decimal(100.0),
        apartment_surface_area=Decimal(20.0),
    )

    assert result is not None

    # Verify item
    assert result.items[0].name == improvement.name
    assert result.items[0].value == improvement.value
    assert result.items[0].completion_date == improvement.completion_date
    assert result.items[0].value_without_excess == 148_000  # 150_000 - 20 * 100
    assert result.items[0].depreciation is not None
    assert result.items[0].depreciation.amount == 148_000  # 148_000 / (15 * 12) * (12 * 13)
    assert result.items[0].depreciation.time is not None
    assert result.items[0].depreciation.time.years == 13
    assert result.items[0].depreciation.time.months == 0
    assert roundup(result.items[0].accepted_value) == 0  # 18_000 / 100 * 20

    # Verify summary
    assert result.summary is not None
    assert result.summary.value == 300_000
    assert result.summary.excess is not None
    assert result.summary.excess.surface_area == 20
    assert result.summary.excess.value_per_square_meter == 100
    assert result.summary.excess.total == 2000
    assert result.summary.value_without_excess == 296_000
    assert result.summary.depreciation == 296_000
    assert result.summary.accepted_value == 0


def test_calculate__singe_improvement__apartment__pre_2011__market_price_index__no_deductions():
    improvement = ImprovementData(
        name="Test improvement",
        value=Decimal(150_000),
        completion_date=datetime.date(2009, 5, 1),
        completion_date_index=Decimal(100),
        no_deductions=True,
    )

    result = calculate_single_apartment_improvement_pre_2011_market_price_index(
        improvement,
        calculation_date=datetime.date(2022, 5, 1),
        calculation_date_index=Decimal(120.0),
        apartment_surface_area=Decimal(20.0),
    )

    assert result is not None

    # Verify item
    assert result.name == improvement.name
    assert result.value == improvement.value
    assert result.completion_date == improvement.completion_date
    assert result.value_without_excess == 180_000
    assert result.depreciation is not None
    assert result.depreciation.amount == 0
    assert result.depreciation.time is not None
    assert result.depreciation.time.years == 0
    assert result.depreciation.time.months == 0
    assert roundup(result.accepted_value) == 180_000


def test_calculate__multiple_improvements__apartment__pre_2011__market_price_index__no_deductions():
    improvement = ImprovementData(
        name="Test improvement",
        value=Decimal(150_000),
        completion_date=datetime.date(2009, 5, 1),
        completion_date_index=Decimal(100),
        no_deductions=True,
    )

    result = calculate_apartment_improvements_pre_2011_market_price_index(
        [improvement, improvement],
        calculation_date=datetime.date(2022, 5, 1),
        calculation_date_index=Decimal(120.0),
        apartment_surface_area=Decimal(20.0),
    )

    assert result is not None

    # Verify item
    assert result.items[0].name == improvement.name
    assert result.items[0].value == improvement.value
    assert result.items[0].completion_date == improvement.completion_date
    assert result.items[0].value_without_excess == 180_000
    assert result.items[0].depreciation is not None
    assert result.items[0].depreciation.amount == 0
    assert result.items[0].depreciation.time is not None
    assert result.items[0].depreciation.time.years == 0
    assert result.items[0].depreciation.time.months == 0
    assert roundup(result.items[0].accepted_value) == 180_000

    # Verify summary
    assert result.summary is not None
    assert result.summary.value == 300_000
    assert result.summary.excess is not None
    assert result.summary.excess.surface_area == 20
    assert result.summary.excess.value_per_square_meter == 100
    assert result.summary.excess.total == 2000
    assert result.summary.value_without_excess == 360_000
    assert result.summary.depreciation == 0
    assert result.summary.accepted_value == 360_000
