from datetime import date

import pytest
from django.urls import reverse
from rest_framework import status

from hitas import exceptions
from hitas.models import Building, HousingCompany, RealEstate
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import BuildingFactory, HousingCompanyFactory, RealEstateFactory


@pytest.mark.django_db
def test__api__housing_company__retrieve(api_client: HitasAPIClient):
    hc1: HousingCompany = HousingCompanyFactory.create()
    hc1_re1: RealEstate = RealEstateFactory.create(housing_company=hc1)
    hc1_re1_bu1: Building = BuildingFactory.create(real_estate=hc1_re1, completion_date=date(2020, 1, 1))
    hc1_re1_bu2: Building = BuildingFactory.create(real_estate=hc1_re1, completion_date=date(2000, 1, 1))
    hc1_re2: RealEstate = RealEstateFactory.create(housing_company=hc1)
    hc1_re2_bu1: Building = BuildingFactory.create(real_estate=hc1_re2, completion_date=None)

    # Second HousingCompany with a building
    BuildingFactory.create()

    response = api_client.get(reverse("hitas:housing-company-detail", args=[hc1.uuid.hex]))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": hc1.uuid.hex,
        "business_id": hc1.business_id,
        "name": {"display": hc1.display_name, "official": hc1.official_name},
        "state": hc1.state.name.lower(),
        "address": {"city": "Helsinki", "postal_code": hc1.postal_code.value, "street": hc1.street_address},
        "area": {"name": hc1.postal_code.description, "cost_area": hc1.area},
        "date": "2000-01-01",
        "real_estates": [
            {
                "id": hc1_re1.uuid.hex,
                "address": {
                    "city": "Helsinki",
                    "postal_code": hc1_re1.postal_code.value,
                    "street": hc1_re1.street_address,
                },
                "property_identifier": hc1_re1.property_identifier,
                "buildings": [
                    {
                        "id": hc1_re1_bu1.uuid.hex,
                        "address": {
                            "city": "Helsinki",
                            "postal_code": hc1_re1_bu1.postal_code.value,
                            "street": hc1_re1_bu1.street_address,
                        },
                        "building_identifier": hc1_re1_bu1.building_identifier,
                        "completion_date": "2020-01-01",
                    },
                    {
                        "id": hc1_re1_bu2.uuid.hex,
                        "address": {
                            "city": "Helsinki",
                            "postal_code": hc1_re1_bu2.postal_code.value,
                            "street": hc1_re1_bu2.street_address,
                        },
                        "building_identifier": hc1_re1_bu2.building_identifier,
                        "completion_date": "2000-01-01",
                    },
                ],
            },
            {
                "id": hc1_re2.uuid.hex,
                "address": {
                    "city": "Helsinki",
                    "postal_code": hc1_re2.postal_code.value,
                    "street": hc1_re2.street_address,
                },
                "property_identifier": hc1_re2.property_identifier,
                "buildings": [
                    {
                        "id": hc1_re2_bu1.uuid.hex,
                        "address": {
                            "city": "Helsinki",
                            "postal_code": hc1_re2_bu1.postal_code.value,
                            "street": hc1_re2_bu1.street_address,
                        },
                        "building_identifier": hc1_re2_bu1.building_identifier,
                        "completion_date": None,
                    }
                ],
            },
        ],
        "financing_method": {
            "id": hc1.financing_method.uuid.hex,
            "value": hc1.financing_method.value,
            "description": hc1.financing_method.description,
            "code": hc1.financing_method.legacy_code_number,
        },
        "building_type": {
            "id": hc1.building_type.uuid.hex,
            "value": hc1.building_type.value,
            "description": hc1.building_type.description,
            "code": hc1.building_type.legacy_code_number,
        },
        "developer": {
            "id": hc1.developer.uuid.hex,
            "value": hc1.developer.value,
            "description": hc1.developer.description,
            "code": hc1.developer.legacy_code_number,
        },
        "property_manager": {
            "id": hc1.property_manager.uuid.hex,
            "address": {
                "city": "Helsinki",
                "postal_code": hc1.property_manager.postal_code.value,
                "street": hc1.property_manager.street_address,
            },
            "name": hc1.property_manager.name,
            "email": hc1.property_manager.email,
        },
        "acquisition_price": {
            "initial": float(hc1.acquisition_price),
            "realized": float(hc1.realized_acquisition_price),
        },
        "primary_loan": float(hc1.primary_loan),
        "sales_price_catalogue_confirmation_date": str(hc1.sales_price_catalogue_confirmation_date),
        "notes": hc1.notes,
        "legacy_id": hc1.legacy_id,
        "notification_date": str(hc1.notification_date),
        "last_modified": {
            "datetime": hc1.last_modified_datetime.isoformat().replace("+00:00", "Z"),
            "user": {
                "username": hc1.last_modified_by.username,
                "first_name": hc1.last_modified_by.first_name,
                "last_name": hc1.last_modified_by.last_name,
            },
        },
    }


@pytest.mark.parametrize("invalid_id", ["foo", "38432c233a914dfb9c2f54d9f5ad9063"])
@pytest.mark.django_db
def test__api__housing_company__read__fail(api_client: HitasAPIClient, invalid_id):
    HousingCompanyFactory.create()

    response = api_client.get(reverse("hitas:housing-company-detail", args=[invalid_id]))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == exceptions.HitasModelNotFound(model=HousingCompany).data
