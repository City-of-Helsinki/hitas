from uuid import UUID

import pytest
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status

from hitas.models import Apartment, HousingCompany, Ownership
from hitas.models.apartment import ApartmentState
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import ApartmentFactory, HousingCompanyFactory, OwnershipFactory

# List tests


@pytest.mark.django_db
def test__api__apartment__list__empty(api_client: HitasAPIClient):
    response = api_client.get(reverse("hitas:apartment-list"))
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
def test__api__apartment__list(api_client: HitasAPIClient):
    ap1: Apartment = ApartmentFactory.create()
    ap2: Apartment = ApartmentFactory.create()
    hc1: HousingCompany = ap1.building.real_estate.housing_company
    hc2: HousingCompany = ap2.building.real_estate.housing_company
    o1: Ownership = OwnershipFactory.create(apartment=ap1, percentage=50)
    o2: Ownership = OwnershipFactory.create(apartment=ap1, percentage=50)

    response = api_client.get(reverse("hitas:apartment-list"))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "id": ap1.uuid.hex,
            "state": ap1.state.value,
            "type": ap1.apartment_type.value,
            "surface_area": float(ap1.surface_area),
            "address": {
                "street_address": ap1.street_address,
                "postal_code": hc1.postal_code.value,
                "city": hc1.postal_code.city,
                "apartment_number": ap1.apartment_number,
                "stair": ap1.stair,
                "floor": ap1.floor,
            },
            "completion_date": str(ap1.completion_date),
            "ownerships": [
                {
                    "owner": {
                        "id": o1.owner.uuid.hex,
                        "name": o1.owner.name,
                        "identifier": o1.owner.identifier,
                        "email": o1.owner.email,
                    },
                    "percentage": float(o1.percentage),
                    "start_date": str(o1.start_date) if o1.start_date else None,
                    "end_date": None,
                },
                {
                    "owner": {
                        "id": o2.owner.uuid.hex,
                        "name": o2.owner.name,
                        "identifier": o2.owner.identifier,
                        "email": o2.owner.email,
                    },
                    "percentage": float(o2.percentage),
                    "start_date": str(o2.start_date) if o2.start_date else None,
                    "end_date": None,
                },
            ],
            "links": {
                "housing_company": {
                    "id": hc1.uuid.hex,
                    "display_name": hc1.display_name,
                    "link": f"/api/v1/housing-companies/{hc1.uuid.hex}",
                },
                "real_estate": {
                    "id": ap1.building.real_estate.uuid.hex,
                    "link": (
                        f"/api/v1/housing-companies/{hc1.uuid.hex}/real-estates/{ap1.building.real_estate.uuid.hex}"
                    ),
                },
                "building": {
                    "id": ap1.building.uuid.hex,
                    "street_address": ap1.building.street_address,
                    "link": (
                        f"/api/v1/housing-companies/{hc1.uuid.hex}"
                        f"/real-estates/{ap1.building.real_estate.uuid.hex}"
                        f"/buildings/{ap1.building.uuid.hex}"
                    ),
                },
                "apartment": {
                    "id": ap1.uuid.hex,
                    "link": f"/api/v1/housing-companies/{hc1.uuid.hex}/apartments/{ap1.uuid.hex}",
                },
            },
        },
        {
            "id": ap2.uuid.hex,
            "state": ap2.state.value,
            "type": ap2.apartment_type.value,
            "surface_area": float(ap2.surface_area),
            "address": {
                "street_address": ap2.street_address,
                "postal_code": hc2.postal_code.value,
                "city": hc2.postal_code.city,
                "apartment_number": ap2.apartment_number,
                "stair": ap2.stair,
                "floor": ap2.floor,
            },
            "links": {
                "housing_company": {
                    "id": hc2.uuid.hex,
                    "display_name": hc2.display_name,
                    "link": f"/api/v1/housing-companies/{hc2.uuid.hex}",
                },
                "real_estate": {
                    "id": ap2.building.real_estate.uuid.hex,
                    "link": (
                        f"/api/v1/housing-companies/{hc2.uuid.hex}/real-estates/{ap2.building.real_estate.uuid.hex}"
                    ),
                },
                "building": {
                    "id": ap2.building.uuid.hex,
                    "street_address": ap2.building.street_address,
                    "link": (
                        f"/api/v1/housing-companies/{hc2.uuid.hex}"
                        f"/real-estates/{ap2.building.real_estate.uuid.hex}"
                        f"/buildings/{ap2.building.uuid.hex}"
                    ),
                },
                "apartment": {
                    "id": ap2.uuid.hex,
                    "link": f"/api/v1/housing-companies/{hc2.uuid.hex}/apartments/{ap2.uuid.hex}",
                },
            },
            "completion_date": str(ap2.completion_date),
            "ownerships": [],
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


# Filter tests


@pytest.mark.parametrize(
    "selected_filter",
    [
        {"housing_company_name": "testdisplay"},
        {"street_address": "test-str"},
        {"postal_code": "99999"},
        {"owner_name": "megatr"},
        {"owner_name": "etimus pri"},
        {"owner_identifier": "010199-123A"},
        {"owner_identifier": "010199-123a"},
    ],
)
@pytest.mark.django_db
def test__api__apartment__filter(api_client: HitasAPIClient, selected_filter):
    ApartmentFactory.create(
        state=ApartmentState.FREE,
        building__real_estate__housing_company__uuid=UUID("38432c23-3a91-4dfb-9c2f-54d9f5ad9063"),
    )

    ApartmentFactory.create(
        state=ApartmentState.FREE, building__real_estate__housing_company__display_name="TestDisplayName"
    )
    ApartmentFactory.create(state=ApartmentState.FREE, street_address="test-street")
    OwnershipFactory.create(apartment__state=ApartmentState.FREE, owner__name="Megatron Opetimus Prime")
    OwnershipFactory.create(apartment__state=ApartmentState.FREE, owner__identifier="010199-123A")
    hc = HousingCompanyFactory.create(postal_code__value="99999")
    ApartmentFactory.create(building__real_estate__housing_company=hc)

    url = reverse("hitas:apartment-list") + "?" + urlencode(selected_filter)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == 1, response.json()


@pytest.mark.parametrize(
    "selected_filter,fields",
    [
        (
            {"housing_company_name": "a"},
            [{"field": "housing_company_name", "message": "Ensure this value has at least 2 characters (it has 1)."}],
        ),
        (
            {"street_address": "a"},
            [{"field": "street_address", "message": "Ensure this value has at least 2 characters (it has 1)."}],
        ),
        (
            {"postal_code": "abcde"},
            [{"field": "postal_code", "message": "Enter a valid value."}],
        ),
        (
            {"postal_code": "1234"},
            [{"field": "postal_code", "message": "Enter a valid value."}],
        ),
        (
            {"postal_code": "123456"},
            [{"field": "postal_code", "message": "Enter a valid value."}],
        ),
        (
            {"owner_name": "a"},
            [{"field": "owner_name", "message": "Ensure this value has at least 2 characters (it has 1)."}],
        ),
        (
            {"owner_identifier": "1"},
            [
                {
                    "field": "owner_identifier",
                    "message": "Ensure this value has at least 2 characters (it has 1).",
                }
            ],
        ),
        (
            {"owner_identifier": "123456789012"},
            [
                {
                    "field": "owner_identifier",
                    "message": "Ensure this value has at most 11 characters (it has 12).",
                }
            ],
        ),
    ],
)
@pytest.mark.django_db
def test__api__apartment__filter__invalid_data(api_client: HitasAPIClient, selected_filter, fields):
    url = reverse("hitas:apartment-list") + "?" + urlencode(selected_filter)
    response = api_client.get(url, openapi_validate_request=False)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": fields,
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }
