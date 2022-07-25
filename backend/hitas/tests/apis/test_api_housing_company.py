from datetime import date
from decimal import Decimal
from typing import Any

import pytest
from django.db.models import ProtectedError
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status

from hitas import exceptions
from hitas.models import (
    Building,
    BuildingType,
    Developer,
    FinancingMethod,
    HousingCompany,
    HousingCompanyState,
    PostalCode,
    PropertyManager,
    RealEstate,
)
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import (
    BuildingFactory,
    BuildingTypeFactory,
    DeveloperFactory,
    FinancingMethodFactory,
    HousingCompanyFactory,
    PostalCodeFactory,
    PropertyManagerFactory,
    RealEstateFactory,
)

# List tests


@pytest.mark.django_db
def test__api__housing_company__list__empty(api_client: HitasAPIClient):
    response = api_client.get(reverse("hitas:housing-company-list"))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == []
    assert response.json()["page"] == {
        "size": 0,
        "current_page": 1,
        "total_items": 0,
        "total_pages": 1,
        "links": {
            "next": None,
            "previous": None,
        },
    }


@pytest.mark.django_db
def test__api__housing_company__list(api_client: HitasAPIClient):
    hc1: HousingCompany = HousingCompanyFactory.create()
    hc2: HousingCompany = HousingCompanyFactory.create()
    BuildingFactory.create(real_estate__housing_company=hc1, completion_date=date(2020, 1, 1))
    bu2: Building = BuildingFactory.create(real_estate__housing_company=hc1, completion_date=date(2000, 1, 1))

    response = api_client.get(reverse("hitas:housing-company-list"))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "id": hc1.uuid.hex,
            "name": hc1.display_name,
            "state": hc1.state.value,
            "address": {
                "street": hc1.street_address,
                "postal_code": hc1.postal_code.value,
                "city": "Helsinki",
            },
            "area": {"name": hc1.postal_code.description, "cost_area": hc1.area},
            "date": str(bu2.completion_date),
        },
        {
            "id": hc2.uuid.hex,
            "name": hc2.display_name,
            "state": hc2.state.value,
            "address": {
                "street": hc2.street_address,
                "postal_code": hc2.postal_code.value,
                "city": "Helsinki",
            },
            "area": {"name": hc2.postal_code.description, "cost_area": hc2.area},
            "date": None,
        },
    ]
    assert response.json()["page"] == {
        "size": 2,
        "current_page": 1,
        "total_items": 2,
        "total_pages": 1,
        "links": {
            "next": None,
            "previous": None,
        },
    }


@pytest.mark.django_db
def test__api__housing_company__list__paging(api_client: HitasAPIClient):
    HousingCompanyFactory.create_batch(size=45)

    response = api_client.get(reverse("hitas:housing-company-list"))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["page"] == {
        "size": 10,
        "current_page": 1,
        "total_items": 45,
        "total_pages": 5,
        "links": {
            "next": "http://testserver/api/v1/housing-companies?page=2",
            "previous": None,
        },
    }

    # Make the second page request
    response = api_client.get(reverse("hitas:housing-company-list"), {"page": 2})
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["page"] == {
        "size": 10,
        "current_page": 2,
        "total_items": 45,
        "total_pages": 5,
        "links": {
            "next": "http://testserver/api/v1/housing-companies?page=3",
            "previous": "http://testserver/api/v1/housing-companies",
        },
    }

    # Make the last page request
    response = api_client.get(reverse("hitas:housing-company-list"), {"page": 5})
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["page"] == {
        "size": 5,
        "current_page": 5,
        "total_items": 45,
        "total_pages": 5,
        "links": {
            "next": None,
            "previous": "http://testserver/api/v1/housing-companies?page=4",
        },
    }


@pytest.mark.parametrize("page_number", ["a", "#", " ", ""])
@pytest.mark.django_db
def test__api__housing_company__list__paging__invalid(api_client: HitasAPIClient, page_number):
    response = api_client.get(reverse("hitas:housing-company-list"), {"page": page_number})
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == exceptions.InvalidPage().data


@pytest.mark.django_db
def test__api__housing_company__list__paging__too_high(api_client: HitasAPIClient):
    response = api_client.get(reverse("hitas:housing-company-list"), {"page": 2})
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == []
    assert response.json()["page"] == {
        "size": 0,
        "current_page": 1,
        "total_items": 0,
        "total_pages": 1,
        "links": {
            "next": None,
            "previous": None,
        },
    }


# Retrieve tests


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
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": hc1.uuid.hex,
        "business_id": hc1.business_id,
        "name": {"display": hc1.display_name, "official": hc1.official_name},
        "state": hc1.state.value,
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
                        "completion_date": str(hc1_re1_bu1.completion_date),
                    },
                    {
                        "id": hc1_re1_bu2.uuid.hex,
                        "address": {
                            "city": "Helsinki",
                            "postal_code": hc1_re1_bu2.postal_code.value,
                            "street": hc1_re1_bu2.street_address,
                        },
                        "building_identifier": hc1_re1_bu2.building_identifier,
                        "completion_date": str(hc1_re1_bu2.completion_date),
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
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == exceptions.HitasModelNotFound(model=HousingCompany).data


# Create tests


def get_housing_company_create_data() -> dict[str, Any]:
    developer: Developer = DeveloperFactory.create()
    financing_method: FinancingMethod = FinancingMethodFactory.create()
    building_type: BuildingType = BuildingTypeFactory.create()
    postal_code: PostalCode = PostalCodeFactory.create()
    property_manager: PropertyManager = PropertyManagerFactory.create(postal_code=postal_code)

    data = {
        "acquisition_price": {"initial": 10.00, "realized": 10.00},
        "address": {
            "postal_code": postal_code.value,
            "street": "test-street-address-1",
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
def test__api__housing_company__create(api_client: HitasAPIClient, minimal_data):
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
    assert response.status_code == status.HTTP_201_CREATED, response.json()

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
def test__api__housing_company__create__invalid_data(api_client: HitasAPIClient, invalid_data):
    data = get_housing_company_create_data()
    data.update(invalid_data)

    response = api_client.post(reverse("hitas:housing-company-list"), data=data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()


@pytest.mark.django_db
def test__api__housing_company__create__invalid_foreign_key(api_client: HitasAPIClient):
    data = get_housing_company_create_data()
    data.update({"property_manager": {"id": "foo"}})

    response = api_client.post(reverse("hitas:housing-company-list"), data=data, format="json")
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


# Update tests


@pytest.mark.django_db
def test__api__housing_company__update(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    BuildingFactory.create(real_estate__housing_company=hc)
    postal_code: PostalCode = PostalCodeFactory.create(value="99999")
    financing_method: FinancingMethod = FinancingMethodFactory.create()
    property_manager: PropertyManager = PropertyManagerFactory.create()

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
        "state": HousingCompanyState.LESS_THAN_30_YEARS.value,
        "sales_price_catalogue_confirmation_date": "2022-01-01",
    }

    response = api_client.put(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]), data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()

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


# Delete tests


@pytest.mark.django_db
def test__api__housing_company__delete(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()

    url = reverse("hitas:housing-company-detail", kwargs={"uuid": hc.uuid.hex})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()

    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


@pytest.mark.django_db
def test__api__housing_company__delete__invalid(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    RealEstateFactory.create(housing_company=hc)

    url = reverse("hitas:housing-company-detail", kwargs={"uuid": hc.uuid.hex})
    with pytest.raises(ProtectedError):  # TODO: Return better error message from the API?
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()


# Filter tests


@pytest.mark.parametrize(
    "selected_filter",
    [
        {"display_name": "TestDisplayName"},
        {"official_name": "TestOfficialName OY"},
        {"display_name": "Test", "official_name": "Test"},
        {"state": HousingCompanyState.GREATER_THAN_30_YEARS_PLOT_DEPARTMENT_NOTIFICATION.value},
        {"business_id": "1234567-8"},
        {"street_address": "test_street"},
        {"property_manager": "TestPropertyManager"},
        {"building_type": "TestBuildingType"},
        {"financing_method": "TestFinancingMethod"},
        {"developer": "TestDeveloper"},
        {"postal_code": "99999"},
        {"property_identifier": "1-1234-321-56"},
        {"property_identifier": "1111"},
    ],
)
@pytest.mark.django_db
def test__api__housing_company__filter(api_client: HitasAPIClient, selected_filter):
    hc: HousingCompany = HousingCompanyFactory.create(display_name="TestDisplayName")
    HousingCompanyFactory.create(official_name="TestOfficialName OY")
    HousingCompanyFactory.create(state=HousingCompanyState.GREATER_THAN_30_YEARS_PLOT_DEPARTMENT_NOTIFICATION)
    HousingCompanyFactory.create(business_id="1234567-8")
    HousingCompanyFactory.create(street_address="test_street")
    HousingCompanyFactory.create(property_manager__name="TestPropertyManager")
    HousingCompanyFactory.create(building_type__value="TestBuildingType")
    HousingCompanyFactory.create(financing_method__value="TestFinancingMethod")
    HousingCompanyFactory.create(developer__value="TestDeveloper")
    HousingCompanyFactory.create(postal_code__value="99999")
    RealEstateFactory.create(property_identifier="1-1234-321-56", housing_company=hc)
    RealEstateFactory.create(property_identifier="1111-1111-1111-1111", housing_company=hc)

    url = reverse("hitas:housing-company-list") + "?" + urlencode(selected_filter)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == 1, response.json()


@pytest.mark.parametrize(
    "selected_filter",
    [
        {"area": 1},
        {"area": 2},
        {"area": 3},
        {"area": 4},
    ],
)
@pytest.mark.django_db
def test__api__housing_company__area_filter(api_client: HitasAPIClient, selected_filter):
    return  # FIXME

    HousingCompanyFactory.create(postal_code__value="00100")  # Area 1
    HousingCompanyFactory.create(postal_code__value="00200")  # Area 2
    HousingCompanyFactory.create(postal_code__value="00240")  # Area 3
    HousingCompanyFactory.create(postal_code__value="99999")  # Not in areas 1-3 => Area 4

    url = reverse("hitas:housing-company-list") + "?" + urlencode(selected_filter)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == 1, response.json()


@pytest.mark.parametrize(
    "selected_filter",
    [
        {"state": 1},
        {"state": "123"},
        {"state": "foo"},
    ],
)
@pytest.mark.django_db
def test__api__housing_company__filter_invalid_state(api_client: HitasAPIClient, selected_filter):
    for state in list(HousingCompanyState):
        HousingCompanyFactory.create(state=state)

    url = reverse("hitas:housing-company-list") + "?" + urlencode(selected_filter)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
