import pytest
from django.urls import reverse
from rest_framework import status

from hitas.models import ApartmentMaximumPriceCalculation
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories.apartment import create_apartment_max_price_calculation


@pytest.mark.django_db
def test__api__apartment_max_price__retrieve__unconfirmed(api_client: HitasAPIClient):
    mpc: ApartmentMaximumPriceCalculation = create_apartment_max_price_calculation(confirmed_at=None)

    response = api_client.get(
        reverse(
            "hitas:maximum-price-detail",
            args=[mpc.apartment.housing_company.uuid.hex, mpc.apartment.uuid.hex, mpc.uuid.hex],
        )
        + "/download",
    )
    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": "not_confirmed",
        "message": "Maximum price calculation is not confirmed.",
        "reason": "Conflict",
        "status": 409,
    }


@pytest.mark.django_db
def test__api__apartment_max_price__retrieve__confirmed(api_client: HitasAPIClient):
    mpc: ApartmentMaximumPriceCalculation = create_apartment_max_price_calculation()

    response = api_client.get(
        reverse(
            "hitas:maximum-price-detail",
            args=[mpc.apartment.housing_company.uuid.hex, mpc.apartment.uuid.hex, mpc.uuid.hex],
        )
        + "/download",
        # TODO: Write a validator that can handle pdf return types.
        # Skip validating response, this prevents `UnicodeDecodeError: 'utf-8' codec can't decode byte...`
        openapi_validate_response=False,
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.get("content-type") == "application/pdf"


@pytest.mark.django_db
def test__api__apartment_max_price__retrieve__migrated(api_client: HitasAPIClient):
    mpc: ApartmentMaximumPriceCalculation = create_apartment_max_price_calculation(json=None, json_version=None)

    response = api_client.get(
        reverse(
            "hitas:maximum-price-detail",
            args=[mpc.apartment.housing_company.uuid.hex, mpc.apartment.uuid.hex, mpc.uuid.hex],
        )
        + "/download",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
