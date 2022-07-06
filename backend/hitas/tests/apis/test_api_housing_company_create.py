from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from hitas.models import HousingCompany
from hitas.models.housing_company import HousingCompanyState
from hitas.tests.factories import (
    BuildingTypeFactory,
    DeveloperFactory,
    FinancingMethodFactory,
    HousingCompanyFactory,
    PostalCodeFactory,
    PropertyManagerFactory,
    UserFactory,
)


@pytest.mark.django_db
def test__api__housing_company__create(api_client: APIClient):
    api_client.force_authenticate(UserFactory.create())
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
        "building_type": building_type.uuid.hex,
        "business_id": "1234567-8",
        "developer": developer.uuid.hex,
        "financing_method": financing_method.uuid.hex,
        "name": {
            "display": "test-housing-company-1",
            "official": "test-housing-company-1-as-oy",
        },
        "notes": "This is a note.",
        "primary_loan": 10.00,
        "property_manager": property_manager.uuid.hex,
        "state": "not_ready",
        "sales_price_catalogue_confirmation_date": "2022-01-01",
    }

    response = api_client.post(reverse("hitas:housing-company-list"), data=data, format="json")
    # validate_openapi(response)  # TODO

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["id"] == HousingCompany.objects.first().uuid.hex
    assert response.json()["address"]["postal_code"] == postal_code.value


@pytest.mark.django_db
def test__api__housing_company__update(api_client: APIClient):
    api_client.force_authenticate(UserFactory.create())
    hc: HousingCompany = HousingCompanyFactory.create()
    postal_code = PostalCodeFactory.create(value="99999")
    financing_method = FinancingMethodFactory.create()
    property_manager = PropertyManagerFactory.create()

    data = {
        "acquisition_price": {"initial": 10.01, "realized": None},
        "address": {
            "street": "changed-street-address",
            "postal_code": postal_code.value,
        },
        "building_type": hc.building_type.uuid.hex,
        "business_id": "1234567-1",
        "developer": hc.developer.uuid.hex,
        "financing_method": financing_method.uuid.hex,
        "name": {
            "display": "changed-name",
            "official": "changed-name-as-oy",
        },
        "notes": "",
        "primary_loan": 10.00,
        "property_manager": property_manager.uuid.hex,
        "state": "less_than_30_years",
        "sales_price_catalogue_confirmation_date": "2022-01-01",
    }
    response = api_client.put(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]), data=data, format="json")
    # validate_openapi(response)  # TODO
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
