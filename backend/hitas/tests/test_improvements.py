import datetime
from decimal import Decimal

from hitas.calculations.helpers import roundup
from hitas.calculations.improvements.common import ImprovementData
from hitas.calculations.improvements.rules_2011_onwards import (
    calculate_housing_company_improvements_2011_onwards,
    calculate_single_housing_company_improvement_2011_onwards,
)
from hitas.calculations.improvements.rules_pre_2011_cpi import (
    calculate_apartment_improvements_pre_2011_construction_price_index,
    calculate_housing_company_improvements_pre_2011_construction_price_index,
    calculate_single_apartment_improvement_pre_2011_construction_price_index,
    calculate_single_housing_company_improvement_pre_2011_construction_price_index,
)
from hitas.calculations.improvements.rules_pre_2011_mpi import (
    calculate_apartment_improvements_pre_2011_market_price_index,
    calculate_housing_company_improvements_pre_2011_market_price_index,
    calculate_single_apartment_improvement_pre_2011_market_price_index,
    calculate_single_housing_company_improvement_pre_2011_market_price_index,
)


def test_calculate_single_housing_company_improvement_2011_onwards():
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
    )
    assert result is not None

    # Verify item
    assert result.name == improvement.name
    assert result.value == improvement.value
    assert result.completion_date == improvement.completion_date
    assert result.value_added == 20_040
    assert roundup(result.value_for_apartment) == Decimal("157.26")
    assert roundup(result.value_for_housing_company) == Decimal("22_707.86")


def test_calculate_housing_company_improvements_2011_onwards():
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


def test_calculate_single_housing_company_improvement_before_2011_construction_price_index():
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


def test_calculate_housing_company_improvements_before_2011_construction_price_index():
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


def test_calculate_single_apartment_improvement_before_2011_construction_price_index():
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


def test_calculate_apartment_improvements_before_2011_construction_price_index():
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


def test_calculate_single_housing_company_improvement_before_2011_market_price_index__after_2010():
    improvement = ImprovementData(
        name="Test improvement",
        value=Decimal(150_000),
        completion_date=datetime.date(2020, 5, 1),
        completion_date_index=Decimal(40.0),
    )

    result = calculate_single_housing_company_improvement_pre_2011_market_price_index(
        improvement,
        calculation_date=datetime.date(2022, 5, 1),
        calculation_date_index=Decimal(100.0),
        total_surface_area=Decimal(100.0),
        apartment_surface_area=Decimal(20.0),
    )

    assert result is not None

    # Verify item
    assert result.name == improvement.name
    assert result.value == improvement.value
    assert result.completion_date == improvement.completion_date
    assert result.value_without_excess == 147_000  # 150_000 - (30 * 100)
    assert result.depreciation is not None
    assert result.depreciation.amount == 0  # (100 * 150_000 * 25 * 0.1) / (50 * 12)
    assert result.depreciation.time is not None
    assert result.depreciation.time.years == 0
    assert result.depreciation.time.months == 0
    assert roundup(result.accepted_value_for_housing_company) == 367500  # 147_000 * 100.0 / 40.0
    assert roundup(result.accepted_value) == 73500  # 367_500 / 100 * 20


def test_calculate_housing_company_improvements_before_2011_market_price_index__after_2010():
    improvement = ImprovementData(
        name="Test improvement",
        value=Decimal(150_000),
        completion_date=datetime.date(2020, 5, 1),
        completion_date_index=Decimal(40.0),
    )

    result = calculate_housing_company_improvements_pre_2011_market_price_index(
        [improvement, improvement],
        calculation_date=datetime.date(2022, 5, 1),
        calculation_date_index=Decimal(100.0),
        total_surface_area=Decimal(100.0),
        apartment_surface_area=Decimal(20.0),
    )

    assert result is not None

    # Verify item
    assert len(result.items) == 2
    assert result.items[0].name == improvement.name
    assert result.items[0].value == improvement.value
    assert result.items[0].completion_date == improvement.completion_date
    assert result.items[0].value_without_excess == 147_000  # 150_000 - (30 * 100)
    assert result.items[0].depreciation is not None
    assert result.items[0].depreciation.amount == 0  # (100 * 150_000 * 25 * 0.1) / (50 * 12)
    assert result.items[0].depreciation.time is not None
    assert result.items[0].depreciation.time.years == 0
    assert result.items[0].depreciation.time.months == 0
    assert roundup(result.items[0].accepted_value_for_housing_company) == 367500  # 147_000 * 100.0 / 40.0
    assert roundup(result.items[0].accepted_value) == 73500  # 367_500 / 100 * 20

    # Verify summary
    assert result.summary is not None
    assert result.summary.value == 300_000
    assert result.summary.excess is not None
    assert result.summary.excess.surface_area == 100
    assert result.summary.excess.value_per_square_meter == 150
    assert result.summary.excess.total == 15_000
    assert result.summary.value_without_excess == 294_000
    assert result.summary.depreciation == 0
    assert result.summary.accepted_value_for_housing_company == 735_000
    assert result.summary.accepted_value == 147_000


def test_calculate_single_housing_company_improvement_before_2011_market_price_index__before_2010():
    improvement = ImprovementData(
        name="Test improvement",
        value=Decimal(150_000),
        completion_date=datetime.date(2009, 5, 1),
        completion_date_index=Decimal(129.2),
    )

    result = calculate_single_housing_company_improvement_pre_2011_market_price_index(
        improvement,
        calculation_date=datetime.date(2022, 5, 1),
        calculation_date_index=Decimal(100.0),
        total_surface_area=Decimal(100.0),
        apartment_surface_area=Decimal(20.0),
    )

    assert result is not None

    # Verify item
    assert result.name == improvement.name
    assert result.value == improvement.value
    assert result.completion_date == improvement.completion_date
    assert result.value_without_excess == 135_000
    assert result.depreciation is not None
    assert result.depreciation.amount == 117_000  # (100 * 150_000 * 25 * 0.1) / (50 * 12)
    assert result.depreciation.time is not None
    assert result.depreciation.time.years == 13
    assert result.depreciation.time.months == 0
    assert roundup(result.accepted_value_for_housing_company) == 18_000
    assert roundup(result.accepted_value) == 3600


def test_calculate_housing_company_improvements_before_2011_market_price_index__before_2010():
    improvement = ImprovementData(
        name="Test improvement",
        value=Decimal(150_000),
        completion_date=datetime.date(2009, 5, 1),
        completion_date_index=Decimal(129.2),
    )

    result = calculate_housing_company_improvements_pre_2011_market_price_index(
        [improvement, improvement],
        calculation_date=datetime.date(2022, 5, 1),
        calculation_date_index=Decimal(100.0),
        total_surface_area=Decimal(100.0),
        apartment_surface_area=Decimal(20.0),
    )

    assert result is not None

    # Verify item
    assert result.items[0].name == improvement.name
    assert result.items[0].value == improvement.value
    assert result.items[0].completion_date == improvement.completion_date
    assert result.items[0].value_without_excess == 135_000  # 150_000 - 150 * 100
    assert result.items[0].depreciation is not None
    assert result.items[0].depreciation.amount == 117_000  # 135_000 / (15 * 12) * (12 * 13)
    assert result.items[0].depreciation.time is not None
    assert result.items[0].depreciation.time.years == 13
    assert result.items[0].depreciation.time.months == 0
    assert roundup(result.items[0].accepted_value_for_housing_company) == 18_000  # 135_000 - 117_000
    assert roundup(result.items[0].accepted_value) == 3600  # 18_000 / 100 * 20

    # Verify summary
    assert result.summary is not None
    assert result.summary.value == 300_000
    assert result.summary.excess is not None
    assert result.summary.excess.surface_area == 100
    assert result.summary.excess.value_per_square_meter == 150
    assert result.summary.excess.total == 15_000
    assert result.summary.value_without_excess == 270_000
    assert result.summary.depreciation == 234_000
    assert result.summary.accepted_value_for_housing_company == 36_000
    assert result.summary.accepted_value == 7200


def test_calculate_single_apartment_improvement_before_2011_market_price_index():
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


def test_calculate_apartment_improvements_before_2011_market_price_index():
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
