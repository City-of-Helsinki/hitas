from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from hitas.models.housing_company import HitasType, RegulationStatus
from hitas.models.thirty_year_regulation import (
    FullSalesData,
    RegulationResult,
    ThirtyYearRegulationResults,
    ThirtyYearRegulationResultsRow,
)
from hitas.services.thirty_year_regulation import RegulationResults
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.apis.thirty_year_regulation.utils import (
    get_comparison_data_for_single_housing_company,
    get_relevant_dates,
)
from hitas.tests.factories import ApartmentSaleFactory

# Read regulation results


@pytest.mark.django_db
def test__api__regulation__fetch_exising(api_client: HitasAPIClient, freezer):
    this_month, _, regulation_month = get_relevant_dates(freezer)

    # Sale in a housing company that already has regulation data
    sale = ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=(
            RegulationStatus.RELEASED_BY_PLOT_DEPARTMENT
        ),
    )

    results = ThirtyYearRegulationResults.objects.create(
        calculation_month=this_month,
        regulation_month=regulation_month,
        surface_area_price_ceiling=Decimal("5000"),
        sales_data=FullSalesData(internal={}, external={}, price_by_area={}),
        replacement_postal_codes=[],
    )
    row = ThirtyYearRegulationResultsRow.objects.create(
        parent=results,
        housing_company=sale.apartment.housing_company,
        completion_date=regulation_month,
        surface_area=10,
        postal_code="00001",
        realized_acquisition_price=Decimal("60000.0"),
        unadjusted_average_price_per_square_meter=Decimal("6000.0"),
        adjusted_average_price_per_square_meter=Decimal("12000.0"),
        completion_month_index=Decimal("100"),
        calculation_month_index=Decimal("200"),
        regulation_result=RegulationResult.STAYS_REGULATED,
        letter_fetched=True,
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == RegulationResults(
        automatically_released=[],
        released_from_regulation=[],
        stays_regulated=[
            get_comparison_data_for_single_housing_company(
                sale.apartment.housing_company,
                regulation_month,
                price=row.adjusted_average_price_per_square_meter,
                current_regulation_status=RegulationStatus.RELEASED_BY_PLOT_DEPARTMENT,
                letter_fetched=True,
            ),
        ],
        skipped=[],
        obfuscated_owners=[],
    )
