from decimal import Decimal
from typing import Any
from uuid import UUID

import pytest
from django.db.models import ProtectedError
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status

from hitas import exceptions
from hitas.models import Apartment, ApartmentType, Building, HitasPostalCode, HousingCompany, Owner, Person
from hitas.models.apartment import ApartmentState
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import (
    ApartmentFactory,
    ApartmentTypeFactory,
    BuildingFactory,
    HitasPostalCodeFactory,
    OwnerFactory,
    PersonFactory,
)
from hitas.views.apartment import ApartmentDetailSerializer

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
            "address": {
                "street_address": ap1.street_address,
                "postal_code": ap1.postal_code.value,
                "city": ap1.postal_code.city,
            },
            "apartment_number": ap1.apartment_number,
            "stair": ap1.stair,
            "housing_company": {
                "id": hc1.uuid.hex,
                "name": hc1.display_name,
            },
            "date": str(ap1.building.completion_date),
            "owners": [
                {
                    "person": {
                        "id": o1.person.uuid.hex,
                        "first_name": o1.person.first_name,
                        "last_name": o1.person.last_name,
                        "social_security_number": o1.person.social_security_number,
                        "email": o1.person.email,
                        "address": {
                            "street_address": o1.person.street_address,
                            "postal_code": o1.person.postal_code,
                            "city": o1.person.city,
                        },
                    },
                    "ownership_percentage": float(o1.ownership_percentage),
                    "ownership_start_date": str(o1.ownership_start_date),
                    "ownership_end_date": None,
                },
                {
                    "person": {
                        "id": o2.person.uuid.hex,
                        "first_name": o2.person.first_name,
                        "last_name": o2.person.last_name,
                        "social_security_number": o2.person.social_security_number,
                        "email": o2.person.email,
                        "address": {
                            "street_address": o2.person.street_address,
                            "postal_code": o2.person.postal_code,
                            "city": o2.person.city,
                        },
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
            "address": {"street_address": ap2.street_address, "postal_code": ap2.postal_code.value, "city": "Helsinki"},
            "apartment_number": ap2.apartment_number,
            "stair": ap2.stair,
            "housing_company": {
                "id": hc2.uuid.hex,
                "name": hc2.display_name,
            },
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
    owner: Owner = OwnerFactory.create(apartment=ap)

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
        "address": {
            "street_address": ap.street_address,
            "postal_code": ap.postal_code.value,
            "city": ap.postal_code.city,
        },
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
        },
        "owners": [
            {
                "person": {
                    "id": owner.person.uuid.hex,
                    "first_name": owner.person.first_name,
                    "last_name": owner.person.last_name,
                    "social_security_number": owner.person.social_security_number,
                    "email": owner.person.email,
                    "address": {
                        "street_address": owner.person.street_address,
                        "postal_code": owner.person.postal_code,
                        "city": owner.person.city,
                    },
                },
                "ownership_percentage": float(owner.ownership_percentage),
                "ownership_start_date": str(owner.ownership_start_date),
                "ownership_end_date": None,
            },
        ],
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
    person1: Person = PersonFactory.create()
    person2: Person = PersonFactory.create()

    data = {
        "state": ApartmentState.SOLD.value,
        "apartment_type": {"id": apartment_type.uuid.hex},
        "surface_area": 69,
        "share_number_start": 50,
        "share_number_end": 100,
        "address": {"street_address": "TestStreet 3", "postal_code": building.postal_code.value},
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
        "owners": [
            {
                "person": {"id": person1.uuid.hex},
                "ownership_percentage": 50,
                "ownership_start_date": "2020-01-01",
                "ownership_end_date": None,
            },
            {
                "person": {"id": person2.uuid.hex},
                "ownership_percentage": 50,
                "ownership_start_date": "2020-01-01",
                "ownership_end_date": None,
            },
        ],
    }
    return data


@pytest.mark.parametrize("minimal_data", [False, True])
@pytest.mark.django_db
def test__api__apartment__create(api_client: HitasAPIClient, minimal_data: bool):
    data = get_apartment_create_data()
    if minimal_data:
        data.update(
            {
                "notes": "",
                "owners": [],
            }
        )
        del data["share_number_start"]
        del data["share_number_end"]
        del data["debt_free_purchase_price"]
        del data["purchase_price"]
        del data["acquisition_price"]
        del data["primary_loan_amount"]
        del data["loans_during_construction"]
        del data["interest_during_construction"]

    response = api_client.post(reverse("hitas:apartment-list"), data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()

    ap = Apartment.objects.first()
    assert response.json()["id"] == ap.uuid.hex
    assert len(response.json()["owners"]) == 0 if minimal_data else 2

    get_response = api_client.get(reverse("hitas:apartment-detail", args=[ap.uuid.hex]))
    assert response.json() == get_response.json()


@pytest.mark.parametrize(
    "invalid_data,fields",
    [
        ({"state": None}, [{"field": "state", "message": "This field is mandatory and cannot be blank."}]),
        ({"state": "invalid_state"}, [{"field": "state", "message": "Unsupported ApartmentState 'invalid_state'."}]),
        (
            {"apartment_type": None},
            [{"field": "apartment_type", "message": "This field is mandatory and cannot be blank."}],
        ),
        (
            {"surface_area": None},
            [{"field": "surface_area", "message": "This field is mandatory and cannot be blank."}],
        ),
        ({"surface_area": "foo"}, [{"field": "surface_area", "message": "A valid number is required."}]),
        (
            {"surface_area": -1},
            [{"field": "surface_area", "message": "Ensure this value is greater than or equal to 0."}],
        ),
        ({"share_number_start": "foo"}, [{"field": "share_number_start", "message": "A valid integer is required."}]),
        (
            {"share_number_start": 100, "share_number_end": None},
            [
                {
                    "field": "non_field_errors",
                    "message": "You must enter both: share_number_start and share_number_end or neither.",
                }
            ],
        ),
        (
            {"share_number_start": None, "share_number_end": 100},
            [
                {
                    "field": "non_field_errors",
                    "message": "You must enter both: share_number_start and share_number_end or neither.",
                }
            ],
        ),
        (
            {"share_number_start": 100, "share_number_end": 50},
            [{"field": "non_field_errors", "message": "share_number_start must not be greater than share_number_end"}],
        ),
        ({"address": None}, [{"field": "address", "message": "This field is mandatory and cannot be blank."}]),
        (
            {"apartment_number": None},
            [{"field": "apartment_number", "message": "This field is mandatory and cannot be blank."}],
        ),
        ({"apartment_number": "foo"}, [{"field": "apartment_number", "message": "A valid integer is required."}]),
        (
            {"apartment_number": -1},
            [{"field": "apartment_number", "message": "Ensure this value is greater than or equal to 0."}],
        ),
        ({"floor": None}, [{"field": "floor", "message": "This field is mandatory and cannot be blank."}]),
        ({"floor": "foo"}, [{"field": "floor", "message": "A valid integer is required."}]),
        ({"floor": 10.1}, [{"field": "floor", "message": "A valid integer is required."}]),
        ({"floor": -1}, [{"field": "floor", "message": "Ensure this value is greater than or equal to 0."}]),
        ({"stair": None}, [{"field": "stair", "message": "This field is mandatory and cannot be blank."}]),
        (
            {"debt_free_purchase_price": -1},
            [{"field": "debt_free_purchase_price", "message": "Ensure this value is greater than or equal to 0."}],
        ),
        (
            {"purchase_price": -1},
            [{"field": "purchase_price", "message": "Ensure this value is greater than or equal to 0."}],
        ),
        (
            {"acquisition_price": -1},
            [{"field": "acquisition_price", "message": "Ensure this value is greater than or equal to 0."}],
        ),
        (
            {"primary_loan_amount": -1},
            [{"field": "primary_loan_amount", "message": "Ensure this value is greater than or equal to 0."}],
        ),
        (
            {"loans_during_construction": -1},
            [{"field": "loans_during_construction", "message": "Ensure this value is greater than or equal to 0."}],
        ),
        (
            {"interest_during_construction": -1},
            [{"field": "interest_during_construction", "message": "Ensure this value is greater than or equal to 0."}],
        ),
        ({"building": None}, [{"field": "building", "message": "This field is mandatory and cannot be blank."}]),
        ({"notes": None}, [{"field": "notes", "message": "This field is mandatory and cannot be blank."}]),
        ({"owners": None}, [{"field": "owners", "message": "This field is mandatory and cannot be blank."}]),
        (
            {
                "owners": [
                    {
                        "person": {"id": "2fe3789b72f24456950e39d06ee9977a"},
                        "ownership_percentage": 100,
                        "ownership_start_date": "2020-01-01",
                        "ownership_end_date": None,
                    },
                    {
                        "person": {"id": "0001e769ae2d40b9ae56ebd615e919d3"},
                        "ownership_percentage": 50,
                        "ownership_start_date": "2020-01-01",
                        "ownership_end_date": None,
                    },
                ]
            },
            [
                {
                    "field": "owners.ownership_percentage",
                    "message": "Ownership percentage of all owners combined must"
                    " be equal to 100. (Given sum was 150.00)",
                }
            ],
        ),
        (
            {
                "owners": [
                    {
                        "person": {"id": "2fe3789b72f24456950e39d06ee9977a"},
                        "ownership_percentage": 10,
                        "ownership_start_date": "2020-01-01",
                        "ownership_end_date": None,
                    },
                    {
                        "person": {"id": "0001e769ae2d40b9ae56ebd615e919d3"},
                        "ownership_percentage": 10,
                        "ownership_start_date": "2020-01-01",
                        "ownership_end_date": None,
                    },
                ]
            },
            [
                {
                    "field": "owners.ownership_percentage",
                    "message": "Ownership percentage of all owners combined must"
                    " be equal to 100. (Given sum was 20.00)",
                }
            ],
        ),
        (
            {
                "owners": [
                    {
                        "person": {"id": "2fe3789b72f24456950e39d06ee9977a"},
                        "ownership_percentage": 100,
                        "ownership_start_date": "2020-01-01",
                        "ownership_end_date": None,
                    },
                    {
                        "person": {"id": "0001e769ae2d40b9ae56ebd615e919d3"},
                        "ownership_percentage": 0,
                        "ownership_start_date": "2020-01-01",
                        "ownership_end_date": None,
                    },
                ]
            },
            [
                {
                    "field": "owners.ownership_percentage",
                    "message": "Ownership percentage greater than 0 and less than"
                    " or equal to 100. (Given value was 0.00)",
                }
            ],
        ),
        (
            {
                "owners": [
                    {
                        "person": {"id": "2fe3789b72f24456950e39d06ee9977a"},
                        "ownership_percentage": 200,
                        "ownership_start_date": "2020-01-01",
                        "ownership_end_date": None,
                    },
                    {
                        "person": {"id": "0001e769ae2d40b9ae56ebd615e919d3"},
                        "ownership_percentage": -100,
                        "ownership_start_date": "2020-01-01",
                        "ownership_end_date": None,
                    },
                ]
            },
            [{"field": "owners.ownership_percentage", "message": "Ensure this value is greater than or equal to 0."}],
        ),
        (
            {
                "owners": [
                    {
                        "person": {"id": "2fe3789b72f24456950e39d06ee9977a"},
                        "ownership_percentage": "foo",
                        "ownership_start_date": "2020-01-01",
                        "ownership_end_date": None,
                    },
                    {
                        "person": {"id": "0001e769ae2d40b9ae56ebd615e919d3"},
                        "ownership_percentage": "baz",
                        "ownership_start_date": "2020-01-01",
                        "ownership_end_date": None,
                    },
                ]
            },
            [
                {"field": "owners.ownership_percentage", "message": "A valid number is required."},
                {"field": "owners.ownership_percentage", "message": "A valid number is required."},
            ],
        ),
    ],
)
@pytest.mark.django_db
def test__api__apartment__create__invalid_data(api_client: HitasAPIClient, invalid_data, fields):
    PersonFactory.create(uuid=UUID("2fe3789b-72f2-4456-950e-39d06ee9977a"))
    PersonFactory.create(uuid=UUID("0001e769-ae2d-40b9-ae56-ebd615e919d3"))

    data = get_apartment_create_data()
    data.update(invalid_data)

    response = api_client.post(reverse("hitas:apartment-list"), data=data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": fields,
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


# Update tests


@pytest.mark.django_db
def test__api__apartment__update__clear_owners(api_client: HitasAPIClient):
    ap: Apartment = ApartmentFactory.create()
    apartment_type: ApartmentType = ApartmentTypeFactory.create()
    building: Building = BuildingFactory.create()
    postal_code: HitasPostalCode = HitasPostalCodeFactory.create(value="99999")
    OwnerFactory.create(apartment=ap)

    data = {
        "state": ApartmentState.SOLD.value,
        "apartment_type": {"id": apartment_type.uuid.hex},
        "surface_area": 100,
        "share_number_start": 101,
        "share_number_end": 200,
        "address": {"street_address": "TestStreet 3", "postal_code": postal_code.value, "city": "Helsinki"},
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
        "owners": [],
    }

    response = api_client.put(reverse("hitas:apartment-detail", args=[ap.uuid.hex]), data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()

    ap.refresh_from_db()
    assert ap.state.value == data["state"]
    assert ap.apartment_type == apartment_type
    assert ap.surface_area == data["surface_area"]
    assert ap.share_number_start == data["share_number_start"]
    assert ap.share_number_end == data["share_number_end"]
    assert ap.street_address == data["address"]["street_address"]
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
    assert ap.owners.all().count() == 0

    get_response = api_client.get(reverse("hitas:apartment-detail", args=[ap.uuid.hex]))
    assert response.json() == get_response.json()


@pytest.mark.parametrize(
    "owner_data",
    [
        [
            {
                "person": {"id": "2fe3789b72f24456950e39d06ee9977a"},
                "ownership_percentage": 100,
                "ownership_start_date": "2020-01-01",
                "ownership_end_date": None,
            }
        ],
        [
            {
                "person": {"id": "2fe3789b72f24456950e39d06ee9977a"},
                "ownership_percentage": 50,
                "ownership_start_date": "2020-01-01",
                "ownership_end_date": None,
            },
            {
                "person": {"id": "697d6ef6fb8f4fc386a42aa9fd57eac3"},
                "ownership_percentage": 50,
                "ownership_start_date": "2020-01-01",
                "ownership_end_date": None,
            },
        ],
        [
            {
                "person": {"id": "2fe3789b72f24456950e39d06ee9977a"},
                "ownership_percentage": 33.33,
                "ownership_start_date": "2020-01-01",
                "ownership_end_date": None,
            },
            {
                "person": {"id": "697d6ef6fb8f4fc386a42aa9fd57eac3"},
                "ownership_percentage": 33.33,
                "ownership_start_date": "2020-01-01",
                "ownership_end_date": None,
            },
            {
                "person": {"id": "2b44c90e8e0448a3b75399e66a220a1d"},
                "ownership_percentage": 33.34,
                "ownership_start_date": "2020-01-01",
                "ownership_end_date": None,
            },
        ],
    ],
)
@pytest.mark.django_db
def test__api__apartment__update__update_owner(api_client: HitasAPIClient, owner_data: list):
    ap: Apartment = ApartmentFactory.create()
    OwnerFactory.create(apartment=ap)
    PersonFactory.create(uuid=UUID("2fe3789b-72f2-4456-950e-39d06ee9977a"))
    PersonFactory.create(uuid=UUID("697d6ef6-fb8f-4fc3-86a4-2aa9fd57eac3"))
    PersonFactory.create(uuid=UUID("2b44c90e-8e04-48a3-b753-99e66a220a1d"))

    data = ApartmentDetailSerializer(ap).data
    data["owners"] = owner_data

    response = api_client.put(reverse("hitas:apartment-detail", args=[ap.uuid.hex]), data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()

    ap.refresh_from_db()
    assert ap.owners.all().count() == len(owner_data)

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
        {"housing_company_name": "testdisplay"},
        {"street_address": "test-str"},
        {"postal_code": "99999"},
        {"owner_name": "megatr"},
        {"owner_name": "etimus pri"},
        {"owner_social_security_number": "010199-123A"},
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
    ApartmentFactory.create(state=ApartmentState.FREE, postal_code__value="99999")
    OwnerFactory.create(apartment__state=ApartmentState.FREE, person__first_name="Megatron")
    OwnerFactory.create(apartment__state=ApartmentState.FREE, person__last_name="Opetimus Prime")
    OwnerFactory.create(apartment__state=ApartmentState.FREE, person__social_security_number="010199-123A")

    url = reverse("hitas:apartment-list") + "?" + urlencode(selected_filter)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == 1, response.json()
