from decimal import Decimal
from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from hitas.models import HousingCompany, PostalCode
from hitas.models.housing_company import HousingCompanyState
from hitas.tests.factories import (
    BuildingFactory,
    BuildingTypeFactory,
    DeveloperFactory,
    FinancingMethodFactory,
    HousingCompanyFactory,
    PostalCodeFactory,
    PropertyManagerFactory,
)


def get_housing_company_create_data() -> dict[str, Any]:
    developer = DeveloperFactory.create()
    financing_method = FinancingMethodFactory.create()
    property_manager = PropertyManagerFactory.create()
    building_type = BuildingTypeFactory.create()
    postal_code = PostalCodeFactory.create()

    data = {
        "acquisition_price": {"initial": 10.00, "realized": 10.00},
        "address": {
            "street": "test-street-address-1",
            "postal_code": postal_code.value,
        },
        "building_type": {"id": building_type.uuid.hex},
        "business_id": "1234567-8",
        "developer": {"id": developer.uuid.hex},
        "financing_method": {"id": financing_method.uuid.hex},
        "name": {
            "display": "test-housing-company-1",
            "official": "test-housing-company-1-as-oy",
        },
        "notes": "This is a note.",
        "primary_loan": 10.00,
        "property_manager": {"id": property_manager.uuid.hex},
        "state": "not_ready",
        "sales_price_catalogue_confirmation_date": "2022-01-01",
    }
    return data


@pytest.mark.parametrize("minimal_data", [False, True])
@pytest.mark.django_db
def test__api__housing_company__create(api_client: APIClient, minimal_data):
    data = get_housing_company_create_data()
    if minimal_data:
        data.update(
            {
                "acquisition_price": {"initial": 10.00, "realized": None},
                "notes": "",
                "sales_price_catalogue_confirmation_date": None,
            }
        )

    response = api_client.post(reverse("hitas:housing-company-list"), data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    hc = HousingCompany.objects.first()
    assert response.json()["id"] == hc.uuid.hex
    assert response.json()["address"]["postal_code"] == PostalCode.objects.first().value

    get_response = api_client.get(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]))
    assert response.json() == get_response.json()


@pytest.mark.parametrize(
    "invalid_data",
    [
        {"business_id": None},
        {"business_id": "#"},
        {"business_id": "123"},
        {"name": None},
        {"name": 0},
        {"state": None},
        {"state": "failing-state"},
        {"address": None},
        {"address": 123},
        {"financing_method": None},
        {"building_type": None},
        {"developer": None},
        {"property_manager": None},
        {"acquisition_price": None},
        {"primary_loan": None},
        {"primary_loan": "foo"},
    ],
)
@pytest.mark.django_db
def test__api__housing_company__create__invalid_data(api_client: APIClient, invalid_data):
    data = get_housing_company_create_data()
    data.update(invalid_data)

    response = api_client.post(reverse("hitas:housing-company-list"), data=data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test__api__housing_company__create__invalid_foreign_key(api_client: APIClient):
    data = get_housing_company_create_data()
    data.update({"property_manager": {"id": "foo"}})

    response = api_client.post(reverse("hitas:housing-company-list"), data=data, format="json")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test__api__housing_company__update(api_client: APIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    BuildingFactory.create(real_estate__housing_company=hc)
    postal_code = PostalCodeFactory.create(value="99999")
    financing_method = FinancingMethodFactory.create()
    property_manager = PropertyManagerFactory.create()

    data = {
        "acquisition_price": {"initial": 10.01, "realized": None},
        "address": {
            "street": "changed-street-address",
            "postal_code": postal_code.value,
        },
        "building_type": {"id": hc.building_type.uuid.hex},
        "business_id": "1234567-1",
        "developer": {"id": hc.developer.uuid.hex},
        "financing_method": {"id": financing_method.uuid.hex},
        "name": {
            "display": "changed-name",
            "official": "changed-name-as-oy",
        },
        "notes": "",
        "primary_loan": 10.00,
        "property_manager": {"id": property_manager.uuid.hex},
        "state": "less_than_30_years",
        "sales_price_catalogue_confirmation_date": "2022-01-01",
    }

    response = api_client.put(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]), data=data, format="json")
    assert response.status_code == status.HTTP_200_OK

    hc.refresh_from_db()
    assert hc.postal_code == postal_code
    assert hc.financing_method == financing_method
    assert hc.property_manager == property_manager
    assert hc.business_id == "1234567-1"
    assert hc.street_address == "changed-street-address"
    assert hc.state == HousingCompanyState.LESS_THAN_30_YEARS
    assert hc.acquisition_price == Decimal("10.01")
    assert hc.realized_acquisition_price is None
    assert hc.notes == ""
    assert response.json()["date"]

    get_response = api_client.get(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]))
    assert response.json() == get_response.json()
