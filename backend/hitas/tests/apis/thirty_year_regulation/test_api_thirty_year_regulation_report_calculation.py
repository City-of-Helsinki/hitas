import datetime
from decimal import Decimal

import pytest

from hitas.models.thirty_year_regulation import (
    RegulationResult,
    ThirtyYearRegulationResults,
    ThirtyYearRegulationResultsRow,
)
from hitas.services.thirty_year_regulation import get_thirty_year_regulation_results_for_housing_company
from hitas.tests.apis.thirty_year_regulation.utils import create_thirty_year_old_housing_company


@pytest.mark.parametrize(
    "surface_area_price_ceiling, adjusted_average_price_per_square_meter, expected_difference",
    [
        # ceiling lower, average higher, should use average
        ("5000.00", "12000.00", "7100.00"),
        # ceiling higher, average lower, should use ceiling
        ("13000.00", "12000.00", "8100.00"),
    ],
)
@pytest.mark.django_db
def test__api__results_difference_logic(
    surface_area_price_ceiling: str,
    adjusted_average_price_per_square_meter: str,
    expected_difference: str,
):
    old_housing_company = create_thirty_year_old_housing_company()
    created_results = ThirtyYearRegulationResults.objects.create(
        regulation_month=datetime.datetime(1993, 2, 1),
        calculation_month=datetime.date(2023, 2, 1),
        surface_area_price_ceiling=Decimal(surface_area_price_ceiling),
        sales_data={
            "external": {},
            "internal": {"00001": {"2022Q4": {"price": 4900.0, "sale_count": 1}}},
            "price_by_area": {"00001": 4900.0},
        },
        replacement_postal_codes=[],
    )
    ThirtyYearRegulationResultsRow.objects.create(
        parent=created_results,
        housing_company=old_housing_company,
        completion_date=datetime.date(1993, 2, 1),
        surface_area=Decimal("10.00"),
        postal_code="00001",
        realized_acquisition_price=Decimal("60000.00"),
        unadjusted_average_price_per_square_meter=Decimal("6000.00"),
        adjusted_average_price_per_square_meter=Decimal(adjusted_average_price_per_square_meter),
        completion_month_index=Decimal("100.00"),
        calculation_month_index=Decimal("200.00"),
        regulation_result=RegulationResult.RELEASED_FROM_REGULATION,
    )
    results = get_thirty_year_regulation_results_for_housing_company(
        old_housing_company.uuid, datetime.date(2023, 2, 1)
    )
    assert results.difference == Decimal(expected_difference)
