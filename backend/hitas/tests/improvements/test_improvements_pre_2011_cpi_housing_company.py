import datetime
from decimal import Decimal

from hitas.calculations.improvements.common import ImprovementData
from hitas.calculations.improvements.rules_pre_2011_cpi import (
    calculate_housing_company_improvements_pre_2011_construction_price_index,
    calculate_single_housing_company_improvement_pre_2011_construction_price_index,
)


def test_calculate__single_improvement__housing_company__pre_2011__construction_price_index():
    improvement = ImprovementData(
        name="Test improvement",
        value=Decimal(150_000),
        completion_date=datetime.date(2020, 5, 1),
        completion_date_index=Decimal(129.2),
    )

    result = calculate_single_housing_company_improvement_pre_2011_construction_price_index(
        improvement, completion_date_acquisition_price=Decimal(50.0), total_acquisition_price=Decimal(100.0)
    )

    assert result is not None

    # Verify item
    assert result.name == improvement.name
    assert result.value == improvement.value
    assert result.value_for_apartment == 75_000


def test_calculate__multiple_improvements__housing_company__pre_2011__construction_price_index():
    improvement = ImprovementData(
        name="Test improvement",
        value=Decimal(150_000),
        completion_date=datetime.date(2020, 5, 1),
        completion_date_index=Decimal(129.2),
    )

    result = calculate_housing_company_improvements_pre_2011_construction_price_index(
        [improvement, improvement],
        completion_date_acquisition_price=Decimal(50.0),
        total_acquisition_price=Decimal(100.0),
    )

    assert result is not None

    # Verify single item
    assert len(result.items) == 2
    assert result.items[0].name == improvement.name
    assert result.items[0].value == improvement.value
    assert result.items[0].value_for_apartment == 75_000

    # Verify summary
    assert result.summary is not None
    assert result.summary.value == 300_000
    assert result.summary.value_for_apartment == 150_000
