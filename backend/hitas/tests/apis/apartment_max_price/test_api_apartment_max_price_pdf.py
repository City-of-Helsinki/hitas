import pytest
from django.urls import reverse
from rest_framework import status

from hitas.models import ApartmentMaximumPriceCalculation
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories.apartment import create_apartment_max_price_calculation


@pytest.mark.django_db
def test__api__apartment_max_price_pdf__retrieve(api_client: HitasAPIClient):
    mpc: ApartmentMaximumPriceCalculation = create_apartment_max_price_calculation()

    response = api_client.post(
        reverse(
            "hitas:apartment-detail",
            args=[mpc.apartment.housing_company.uuid.hex, mpc.apartment.uuid.hex],
        )
        + "/reports/download-latest-confirmed-prices",
        data={"request_date": "2022-01-01"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.get("content-type") == "application/pdf"


@pytest.mark.django_db
def test__api__apartment_max_price_pdf__retrieve__unconfirmed(api_client: HitasAPIClient):
    mpc: ApartmentMaximumPriceCalculation = create_apartment_max_price_calculation(confirmed_at=None)

    response = api_client.post(
        reverse(
            "hitas:apartment-detail",
            args=[mpc.apartment.housing_company.uuid.hex, mpc.apartment.uuid.hex],
        )
        + "/reports/download-latest-confirmed-prices",
        data={"request_date": "2022-01-01"},
        format="json",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


@pytest.mark.django_db
def test__api__apartment_max_price_pdf__retrieve__migrated(api_client: HitasAPIClient):
    mpc: ApartmentMaximumPriceCalculation = create_apartment_max_price_calculation(json=None, json_version=None)

    response = api_client.post(
        reverse(
            "hitas:apartment-detail",
            args=[mpc.apartment.housing_company.uuid.hex, mpc.apartment.uuid.hex],
        )
        + "/reports/download-latest-confirmed-prices",
        data={"request_date": "2022-01-01"},
        format="json",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
