import uuid

import pytest
from dateutil import parser as dateparser
from django.urls import reverse
from rest_framework import status

from hitas.models import Apartment, ApartmentMaximumPriceCalculation, HousingCompany
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import HousingCompanyFactory
from hitas.tests.factories.apartment import (
    ApartmentFactory,
    ApartmentMaximumPriceCalculationFactory,
    create_apartment_max_price_calculation,
)


@pytest.mark.django_db
def test__api__apartment_max_price__retrieve__unconfirmed(api_client: HitasAPIClient):
    mpc: ApartmentMaximumPriceCalculation = create_apartment_max_price_calculation(confirmed_at=None)

    response = api_client.get(
        reverse(
            "hitas:maximum-price-detail",
            args=[mpc.apartment.housing_company.uuid.hex, mpc.apartment.uuid.hex, mpc.uuid.hex],
        )
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_json = response.json()
    assert response_json.pop("confirmed_at") is None
    assert response_json == mpc.json


@pytest.mark.django_db
def test__api__apartment_max_price__retrieve__confirmed(api_client: HitasAPIClient):
    mpc: ApartmentMaximumPriceCalculation = create_apartment_max_price_calculation()

    response = api_client.get(
        reverse(
            "hitas:maximum-price-detail",
            args=[mpc.apartment.housing_company.uuid.hex, mpc.apartment.uuid.hex, mpc.uuid.hex],
        )
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_json = response.json()
    # `mpc.confirmed_at` is a datetime, `response_json` is a string. use `dateparser.parse` as
    # `response_json` goes through `JsonEncoder` which replaces the string timezone `+00:00` with `Z` and
    # `str(mpc.confirmed_at)` returns a result with a `+00:00` suffix and `datetime.datetime.fromisoformat()` does not
    # recognize `Z`. FIXME: change this to `fromisoformat` after we migrate to python 3.11.
    assert mpc.confirmed_at == dateparser.parse(response_json.pop("confirmed_at"))
    assert response_json == mpc.json


@pytest.mark.django_db
def test__api__apartment_max_price__retrieve__migrated(api_client: HitasAPIClient):
    mpc: ApartmentMaximumPriceCalculation = create_apartment_max_price_calculation(json=None, json_version=None)

    response = api_client.get(
        reverse(
            "hitas:maximum-price-detail",
            args=[mpc.apartment.housing_company.uuid.hex, mpc.apartment.uuid.hex, mpc.uuid.hex],
        )
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "apartment_maximum_price_calculation_not_found",
        "message": "Apartment maximum price calculation not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__apartment_max_price__retrieve__incorrect_housing_company_uuid(api_client: HitasAPIClient):
    mpc: ApartmentMaximumPriceCalculation = ApartmentMaximumPriceCalculationFactory.create()
    another_housing_company: HousingCompany = HousingCompanyFactory.create()

    # Create max price calculation
    response = api_client.get(
        reverse(
            "hitas:maximum-price-detail",
            args=[another_housing_company.uuid.hex, mpc.apartment.uuid.hex, mpc.uuid.hex],
        )
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "apartment_not_found",
        "message": "Apartment not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__apartment_max_price__retrieve__nonexistent_housing_company_id(api_client: HitasAPIClient):
    mpc: ApartmentMaximumPriceCalculation = ApartmentMaximumPriceCalculationFactory.create()

    # Create max price calculation
    response = api_client.get(
        reverse(
            "hitas:maximum-price-detail",
            args=[uuid.uuid4().hex, mpc.apartment.uuid.hex, mpc.uuid.hex],
        )
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "housing_company_not_found",
        "message": "Housing company not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__apartment_max_price__retrieve__apartment_id_in_another_housing_company(api_client: HitasAPIClient):
    mpc: ApartmentMaximumPriceCalculation = ApartmentMaximumPriceCalculationFactory.create()
    another_apartment: Apartment = ApartmentFactory.create()

    # Create max price calculation
    response = api_client.get(
        reverse(
            "hitas:maximum-price-detail",
            args=[mpc.apartment.housing_company.uuid.hex, another_apartment.uuid.hex, mpc.uuid.hex],
        )
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "apartment_not_found",
        "message": "Apartment not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__apartment_max_price__retrieve__incorrect_apartment_id(api_client: HitasAPIClient):
    mpc: ApartmentMaximumPriceCalculation = ApartmentMaximumPriceCalculationFactory.create()
    another_apartment: Apartment = ApartmentFactory.create(building=mpc.apartment.building)

    # Create max price calculation
    response = api_client.get(
        reverse(
            "hitas:maximum-price-detail",
            args=[mpc.apartment.housing_company.uuid.hex, another_apartment.uuid.hex, mpc.uuid.hex],
        )
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "apartment_maximum_price_calculation_not_found",
        "message": "Apartment maximum price calculation not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__apartment_max_price__confirm__nonexistent_apartment_id(api_client: HitasAPIClient):
    mpc: ApartmentMaximumPriceCalculation = ApartmentMaximumPriceCalculationFactory.create()

    # Create max price calculation
    response = api_client.get(
        reverse(
            "hitas:maximum-price-detail",
            args=[mpc.apartment.housing_company.uuid.hex, uuid.uuid4().hex, mpc.uuid.hex],
        )
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "apartment_not_found",
        "message": "Apartment not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__apartment_max_price__retrieve__invalid_id(api_client: HitasAPIClient):
    mpc: ApartmentMaximumPriceCalculation = ApartmentMaximumPriceCalculationFactory.create()
    # Create another calculation to different apartment (and housing company)
    another_mpc: ApartmentMaximumPriceCalculation = ApartmentMaximumPriceCalculationFactory.create()

    # Create max price calculation
    response = api_client.get(
        reverse(
            "hitas:maximum-price-detail",
            args=[mpc.apartment.housing_company.uuid.hex, mpc.apartment.uuid.hex, another_mpc.uuid.hex],
        )
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "apartment_maximum_price_calculation_not_found",
        "message": "Apartment maximum price calculation not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__apartment_max_price__retrieve__nonexistent_calculation_id(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create()

    # Create max price calculation
    response = api_client.get(
        reverse("hitas:maximum-price-detail", args=[a.housing_company.uuid.hex, a.uuid.hex, uuid.uuid4().hex]),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "apartment_maximum_price_calculation_not_found",
        "message": "Apartment maximum price calculation not found",
        "reason": "Not Found",
        "status": 404,
    }
