import pytest
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from rest_framework import status

from hitas.models import ExternalSalesData
from hitas.models.external_sales_data import CostAreaData, QuarterData
from hitas.tests.apis.helpers import HitasAPIClient, count_queries
from hitas.tests.apis.thirty_year_regulation.utils import (
    create_new_apartment,
    get_relevant_dates,
)
from hitas.tests.factories import ApartmentSaleFactory
from hitas.utils import to_quarter


@pytest.mark.django_db
def test__api__regulation_postal_codes(api_client: HitasAPIClient, freezer):
    this_month, previous_year_last_month, _ = get_relevant_dates(freezer)

    # Apartment where sales happened in the previous year
    apartment = create_new_apartment(
        previous_year_last_month,
        building__real_estate__housing_company__postal_code__cost_area=1,
    )

    # Sale in the previous year, which affect the average price per square meter
    # Average sales price will be: (40_000 + 9_000) / 1 = 49_000
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=40_000,
        apartment_share_of_housing_company_loans=9_000,
    )

    # Create necessary external sales data
    # Average sales price will be: (15_000 + 30_000) / (1 + 2) = 15_000
    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(previous_year_last_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(
            quarter=to_quarter(previous_year_last_month - relativedelta(months=3)),
            areas=[CostAreaData(postal_code="00002", sale_count=1, price=15_000)],
        ),
        quarter_4=QuarterData(
            quarter=to_quarter(previous_year_last_month),
            areas=[
                CostAreaData(postal_code="00002", sale_count=2, price=30_000),
            ],
        ),
    )

    url = reverse("hitas:thirty-year-regulation-postal-codes-list")

    with count_queries(3):
        response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == [
        {
            "postal_code": "00001",
            "price_by_area": 49000.0,
            "cost_area": 1,
        },
        {
            "postal_code": "00002",
            "price_by_area": 15000.0,
            "cost_area": None,
        },
    ]


@pytest.mark.django_db
def test__api__regulation_postal_codes__missing_external_sales_data(api_client: HitasAPIClient, freezer):
    get_relevant_dates(freezer)

    url = reverse("hitas:thirty-year-regulation-postal-codes-list")

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "external_sales_data_not_found",
        "message": "External sales data not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__regulation_postal_codes__wrong_calculation_date(api_client: HitasAPIClient, freezer):
    this_month, previous_year_last_month, _ = get_relevant_dates(freezer)

    # Create necessary external sales data
    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(previous_year_last_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(
            quarter=to_quarter(previous_year_last_month - relativedelta(months=3)),
            areas=[CostAreaData(postal_code="00002", sale_count=1, price=15_000)],
        ),
        quarter_4=QuarterData(
            quarter=to_quarter(previous_year_last_month),
            areas=[
                CostAreaData(postal_code="00002", sale_count=2, price=30_000),
            ],
        ),
    )

    url = reverse("hitas:thirty-year-regulation-postal-codes-list") + "?calculation_date=2022-02-01"

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "external_sales_data_not_found",
        "message": "External sales data not found",
        "reason": "Not Found",
        "status": 404,
    }
