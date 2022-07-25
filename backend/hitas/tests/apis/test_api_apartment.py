from decimal import Decimal
from typing import Any
from uuid import UUID

import pytest
from django.db.models import ProtectedError
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status

from hitas import exceptions
from hitas.models import Apartment, ApartmentType, Building, HousingCompany, Owner, PostalCode
from hitas.models.apartment import ApartmentState
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import (
    ApartmentFactory,
    ApartmentTypeFactory,
    BuildingFactory,
    OwnerFactory,
    PostalCodeFactory,
)

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
    o1: Owner = OwnerFactory.create(apartment=ap1, ownership_percentage=50)
    o2: Owner = OwnerFactory.create(apartment=ap1, ownership_percentage=50)

    response = api_client.get(reverse("hitas:apartment-list"))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "id": ap1.uuid.hex,
            "state": ap1.state.value,
            "apartment_type": ap1.apartment_type.value,
            "surface_area": float(ap1.surface_area),
            "address": {"street": ap1.street_address, "postal_code": ap1.postal_code.value},
            "apartment_number": ap1.apartment_number,
            "housing_company": hc1.display_name,
            "date": str(ap1.building.completion_date),
            "owners": [
                {
                    "apartment_id": ap1.uuid.hex,
                    "person": {
                        "id": o1.person.uuid.hex,
                        "first_name": o1.person.first_name,
                        "last_name": o1.person.last_name,
                        "social_security_number": o1.person.social_security_number,
                        "email": o1.person.email,
                        "address": {"street": o1.person.street_address, "postal_code": o1.person.postal_code.value},
                    },
                    "ownership_percentage": float(o1.ownership_percentage),
                    "ownership_start_date": str(o1.ownership_start_date),
                    "ownership_end_date": None,
                },
                {
                    "apartment_id": ap1.uuid.hex,
                    "person": {
                        "id": o2.person.uuid.hex,
                        "first_name": o2.person.first_name,
                        "last_name": o2.person.last_name,
                        "social_security_number": o2.person.social_security_number,
                        "email": o2.person.email,
                        "address": {"street": o2.person.street_address, "postal_code": o2.person.postal_code.value},
                    },
                    "ownership_percentage": float(o2.ownership_percentage),
                    "ownership_start_date": str(o2.ownership_start_date),
                    "ownership_end_date": None,
                },
            ],
        },
        {
            "id": ap2.uuid.hex,
            "state": ap2.state.value,
            "apartment_type": ap2.apartment_type.value,
            "surface_area": float(ap2.surface_area),
            "address": {"street": ap2.street_address, "postal_code": ap2.postal_code.value},
            "apartment_number": ap2.apartment_number,
            "housing_company": hc2.display_name,
            "date": str(ap2.building.completion_date),
            "owners": [],
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


# Retrieve tests


@pytest.mark.django_db
def test__api__apartment__retrieve(api_client: HitasAPIClient):
    ap: Apartment = ApartmentFactory.create()
    hc: HousingCompany = ap.building.real_estate.housing_company

    response = api_client.get(reverse("hitas:apartment-detail", args=[ap.uuid.hex]))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": ap.uuid.hex,
        "state": ap.state.value,
        "apartment_type": {
            "id": ap.apartment_type.uuid.hex,
            "value": ap.apartment_type.value,
            "description": ap.apartment_type.description,
            "code": ap.apartment_type.legacy_code_number,
        },
        "surface_area": float(ap.surface_area),
        "share_number_start": ap.share_number_start,
        "share_number_end": ap.share_number_end,
        "address": {"street": ap.street_address, "postal_code": ap.postal_code.value},
        "apartment_number": ap.apartment_number,
        "floor": ap.floor,
        "stair": ap.stair,
        "date": str(ap.building.completion_date),
        "debt_free_purchase_price": float(ap.debt_free_purchase_price),
        "purchase_price": float(ap.purchase_price),
        "acquisition_price": float(ap.acquisition_price),
        "primary_loan_amount": float(ap.primary_loan_amount),
        "loans_during_construction": float(ap.loans_during_construction),
        "interest_during_construction": float(ap.interest_during_construction),
        "building": ap.building.uuid.hex,
        "real_estate": ap.building.real_estate.uuid.hex,
        "housing_company": {
            "id": hc.uuid.hex,
            "name": hc.display_name,
            "state": hc.state.value,
            "address": {"street": hc.street_address, "postal_code": hc.postal_code.value, "city": "Helsinki"},
            "area": {"name": hc.postal_code.description, "cost_area": hc.area},
            "date": str(ap.building.completion_date),
        },
        "owners": [],
        "notes": ap.notes,
    }


@pytest.mark.parametrize("invalid_id", ["foo", "38432c233a914dfb9c2f54d9f5ad9063"])
@pytest.mark.django_db
def test__api__apartment__read__fail(api_client: HitasAPIClient, invalid_id):
    ApartmentFactory.create()

    response = api_client.get(reverse("hitas:apartment-detail", args=[invalid_id]))
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == exceptions.HitasModelNotFound(model=Apartment).data


# Create tests


def get_apartment_create_data() -> dict[str, Any]:
    apartment_type: ApartmentType = ApartmentTypeFactory.create()
    building: Building = BuildingFactory.create()

    data = {
        "state": ApartmentState.SOLD.value,
        "apartment_type": {"id": apartment_type.uuid.hex},
        "surface_area": 69,
        "share_number_start": 50,
        "share_number_end": 100,
        "address": {"street": "TestStreet 3", "postal_code": building.postal_code.value},
        "apartment_number": 58,
        "floor": 1,
        "stair": "A",
        "debt_free_purchase_price": 12345,
        "purchase_price": 12345.6,
        "acquisition_price": Decimal("12345"),
        "primary_loan_amount": 12345,
        "loans_during_construction": 12345,
        "interest_during_construction": 12345,
        "building": building.uuid.hex,
        "notes": "Lorem ipsum",
    }
    return data


@pytest.mark.parametrize("minimal_data", [False, True])
@pytest.mark.django_db
def test__api__apartment__create(api_client: HitasAPIClient, minimal_data):
    data = get_apartment_create_data()
    if minimal_data:
        data.update(
            {
                "share_number_start": None,
                "share_number_end": None,
                "debt_free_purchase_price": None,
                "purchase_price": None,
                "acquisition_price": None,
                "primary_loan_amount": None,
                "loans_during_construction": None,
                "interest_during_construction": None,
                "notes": "",
            }
        )

    response = api_client.post(reverse("hitas:apartment-list"), data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()

    ap = Apartment.objects.first()
    assert response.json()["id"] == ap.uuid.hex

    get_response = api_client.get(reverse("hitas:apartment-detail", args=[ap.uuid.hex]))
    assert response.json() == get_response.json()


@pytest.mark.parametrize(
    "invalid_data",
    [
        {"state": None},
        {"state": "foo"},
        {"apartment_type": None},
        {"surface_area": None},
        {"surface_area": "foo"},
        {"surface_area": -1},
        {"share_number_start": "foo"},
        {"share_number_end": "foo"},
        {"share_number_start": 100, "share_number_end": None},
        {"share_number_start": None, "share_number_end": 100},
        {"share_number_start": 100, "share_number_end": 50},
        {"address": None},
        {"apartment_number": None},
        {"apartment_number": "foo"},
        {"apartment_number": -1},
        {"floor": None},
        {"floor": "foo"},
        {"floor": -1},
        {"stair": None},
        {"debt_free_purchase_price": -1},
        {"purchase_price": -1},
        {"acquisition_price": -1},
        {"primary_loan_amount": -1},
        {"loans_during_construction": -1},
        {"interest_during_construction": -1},
        {"building": None},
        {"notes": None},  # None is not allowed, but blank is fine
    ],
)
@pytest.mark.django_db
def test__api__apartment__create__invalid_data(api_client: HitasAPIClient, invalid_data):
    data = get_apartment_create_data()
    data.update(invalid_data)

    response = api_client.post(reverse("hitas:apartment-list"), data=data, format="json")
    print(response.json())
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()


# Update tests


@pytest.mark.django_db
def test__api__apartment__update(api_client: HitasAPIClient):
    ap: Apartment = ApartmentFactory.create()
    apartment_type: ApartmentType = ApartmentTypeFactory.create()
    building: Building = BuildingFactory.create()
    postal_code: PostalCode = PostalCodeFactory.create(value="99999")

    data = {
        "state": ApartmentState.SOLD.value,
        "apartment_type": {"id": apartment_type.uuid.hex},
        "surface_area": 100,
        "share_number_start": 101,
        "share_number_end": 200,
        "address": {"street": "TestStreet 3", "postal_code": postal_code.value},
        "apartment_number": 9,
        "floor": 5,
        "stair": "X",
        "debt_free_purchase_price": 22222,
        "purchase_price": 22222,
        "acquisition_price": 22222,
        "primary_loan_amount": 22222,
        "loans_during_construction": 22222,
        "interest_during_construction": 22222,
        "building": building.uuid.hex,
        "notes": "Test Notes",
    }

    response = api_client.put(reverse("hitas:apartment-detail", args=[ap.uuid.hex]), data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()
    print(response.json())

    ap.refresh_from_db()
    assert ap.state.value == data["state"]
    assert ap.apartment_type == apartment_type
    assert ap.surface_area == data["surface_area"]
    assert ap.share_number_start == data["share_number_start"]
    assert ap.share_number_end == data["share_number_end"]
    assert ap.street_address == data["address"]["street"]
    assert ap.postal_code == postal_code
    assert ap.apartment_number == data["apartment_number"]
    assert ap.floor == data["floor"]
    assert ap.stair == data["stair"]
    assert ap.debt_free_purchase_price == data["debt_free_purchase_price"]
    assert ap.purchase_price == data["purchase_price"]
    assert ap.acquisition_price == data["acquisition_price"]
    assert ap.primary_loan_amount == data["primary_loan_amount"]
    assert ap.loans_during_construction == data["loans_during_construction"]
    assert ap.interest_during_construction == data["interest_during_construction"]
    assert ap.building == building
    assert ap.notes == data["notes"]

    get_response = api_client.get(reverse("hitas:apartment-detail", args=[ap.uuid.hex]))
    assert response.json() == get_response.json()


# Delete tests


@pytest.mark.django_db
def test__api__apartment__delete(api_client: HitasAPIClient):
    hc: Apartment = ApartmentFactory.create()

    url = reverse("hitas:apartment-detail", kwargs={"uuid": hc.uuid.hex})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()

    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


@pytest.mark.django_db
def test__api__apartment__delete__invalid(api_client: HitasAPIClient):
    ap: Apartment = ApartmentFactory.create()
    OwnerFactory.create(apartment=ap)

    url = reverse("hitas:apartment-detail", kwargs={"uuid": ap.uuid.hex})
    with pytest.raises(ProtectedError):  # TODO: Return better error message from the API?
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()


# Filter tests


@pytest.mark.parametrize(
    "selected_filter",
    [
        {"housing_company": "38432c233a914dfb9c2f54d9f5ad9063"},
        {"housing_company_name": "TestDisplayName"},
        {"property_identifier": "1-1234-321-56"},
        {"state": ApartmentState.SOLD.value},
        {"apartment_type": "1h+sauna+takkahuone+uima-allas"},
        {"street_address": "test_street"},
        {"apartment_number": 69},
        {"floor": 22},
        {"stair": "Ö"},
        {"building": "4a5c66cdcd554784a9047bd45c2362ba"},
    ],
)
@pytest.mark.django_db
def test__api__apartment__filter(api_client: HitasAPIClient, selected_filter):
    ApartmentFactory.create(state=ApartmentState.SOLD)
    ApartmentFactory.create(
        state=ApartmentState.FREE,
        building__real_estate__housing_company__uuid=UUID("38432c23-3a91-4dfb-9c2f-54d9f5ad9063"),
    )
    ApartmentFactory.create(
        state=ApartmentState.FREE, building__real_estate__housing_company__display_name="TestDisplayName"
    )
    ApartmentFactory.create(state=ApartmentState.FREE, building__real_estate__property_identifier="1-1234-321-56")
    ApartmentFactory.create(state=ApartmentState.FREE, apartment_type__value="1h+sauna+takkahuone+uima-allas")
    ApartmentFactory.create(state=ApartmentState.FREE, street_address="test_street")
    ApartmentFactory.create(state=ApartmentState.FREE, apartment_number=69)
    ApartmentFactory.create(state=ApartmentState.FREE, floor=22)
    ApartmentFactory.create(state=ApartmentState.FREE, stair="Ö")
    ApartmentFactory.create(state=ApartmentState.FREE, building__uuid=UUID("4a5c66cd-cd55-4784-a904-7bd45c2362ba"))

    url = reverse("hitas:apartment-list") + "?" + urlencode(selected_filter)
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
def test__api__apartment__area_filter(api_client: HitasAPIClient, selected_filter):
    return  # FIXME

    ApartmentFactory.create(postal_code__value="00100")  # Area 1
    ApartmentFactory.create(postal_code__value="00200")  # Area 2
    ApartmentFactory.create(postal_code__value="00240")  # Area 3
    ApartmentFactory.create(postal_code__value="99999")  # Not in areas 1-3 => Area 4

    url = reverse("hitas:apartment-list") + "?" + urlencode(selected_filter)
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
def test__api__apartment__filter_invalid(api_client: HitasAPIClient, selected_filter):
    for state in list(ApartmentState):
        ApartmentFactory.create(state=state)

    url = reverse("hitas:apartment-list") + "?" + urlencode(selected_filter)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
