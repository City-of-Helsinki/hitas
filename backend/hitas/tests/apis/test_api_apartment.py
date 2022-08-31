from typing import Any
from uuid import UUID

import pytest
from django.db.models import ProtectedError
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status

from hitas import exceptions
from hitas.models import Apartment, ApartmentType, Building, HousingCompany, Ownership, Person
from hitas.models.apartment import ApartmentState
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import (
    ApartmentFactory,
    ApartmentTypeFactory,
    BuildingFactory,
    HousingCompanyFactory,
    OwnershipFactory,
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
    o1: Ownership = OwnershipFactory.create(apartment=ap1, percentage=50)
    o2: Ownership = OwnershipFactory.create(apartment=ap1, percentage=50)

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
                "postal_code": hc1.postal_code.value,
                "city": hc1.postal_code.city,
            },
            "apartment_number": ap1.apartment_number,
            "stair": ap1.stair,
            "housing_company": {
                "id": hc1.uuid.hex,
                "name": hc1.display_name,
            },
            "completion_date": str(ap1.completion_date),
            "ownerships": [
                {
                    "owner": {
                        "id": o1.owner.uuid.hex,
                        "first_name": o1.owner.first_name,
                        "last_name": o1.owner.last_name,
                        "social_security_number": o1.owner.social_security_number,
                        "email": o1.owner.email,
                    },
                    "percentage": float(o1.percentage),
                    "start_date": str(o1.start_date) if o1.start_date else None,
                    "end_date": None,
                },
                {
                    "owner": {
                        "id": o2.owner.uuid.hex,
                        "first_name": o2.owner.first_name,
                        "last_name": o2.owner.last_name,
                        "social_security_number": o2.owner.social_security_number,
                        "email": o2.owner.email,
                    },
                    "percentage": float(o2.percentage),
                    "start_date": str(o2.start_date) if o2.start_date else None,
                    "end_date": None,
                },
            ],
        },
        {
            "id": ap2.uuid.hex,
            "state": ap2.state.value,
            "apartment_type": ap2.apartment_type.value,
            "surface_area": float(ap2.surface_area),
            "address": {
                "street_address": ap2.street_address,
                "postal_code": hc2.postal_code.value,
                "city": hc2.postal_code.city,
            },
            "apartment_number": ap2.apartment_number,
            "stair": ap2.stair,
            "housing_company": {
                "id": hc2.uuid.hex,
                "name": hc2.display_name,
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


# Retrieve tests


@pytest.mark.django_db
def test__api__apartment__retrieve(api_client: HitasAPIClient):
    ap: Apartment = ApartmentFactory.create()
    hc: HousingCompany = ap.building.real_estate.housing_company
    owner: Ownership = OwnershipFactory.create(apartment=ap)

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
        "shares": {
            "start": ap.share_number_start,
            "end": ap.share_number_end,
            "total": ap.share_number_end - ap.share_number_start + 1,
        },
        "address": {
            "street_address": ap.street_address,
            "postal_code": hc.postal_code.value,
            "city": hc.postal_code.city,
        },
        "apartment_number": ap.apartment_number,
        "floor": ap.floor,
        "stair": ap.stair,
        "completion_date": str(ap.completion_date),
        "prices": {
            "debt_free_purchase_price": ap.debt_free_purchase_price,
            "primary_loan_amount": ap.primary_loan_amount,
            "acquisition_price": ap.debt_free_purchase_price + ap.primary_loan_amount,
            "purchase_price": ap.purchase_price,
            "first_purchase_date": ap.first_purchase_date,
            "second_purchase_date": ap.second_purchase_date,
            "construction": {
                "loans": ap.loans_during_construction,
                "interest": ap.interest_during_construction,
                "debt_free_purchase_price": ap.debt_free_purchase_price_during_construction,
                "additional_work": ap.additional_work_during_construction,
            },
        },
        "building": ap.building.uuid.hex,
        "real_estate": ap.building.real_estate.uuid.hex,
        "housing_company": {
            "id": hc.uuid.hex,
            "name": hc.display_name,
        },
        "ownerships": [
            {
                "owner": {
                    "id": owner.owner.uuid.hex,
                    "first_name": owner.owner.first_name,
                    "last_name": owner.owner.last_name,
                    "social_security_number": owner.owner.social_security_number,
                    "email": owner.owner.email,
                },
                "percentage": float(owner.percentage),
                "start_date": str(owner.start_date) if owner.start_date else None,
                "end_date": None,
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
        "shares": {
            "start": 20,
            "end": 100,
        },
        "address": {
            "street_address": "TestStreet 3",
            "postal_code": building.real_estate.housing_company.postal_code.value,
        },
        "apartment_number": 58,
        "floor": "1",
        "stair": "A",
        "completion_date": "2022-08-26",
        "prices": {
            "debt_free_purchase_price": 12345,
            "purchase_price": 23456,
            "primary_loan_amount": 34567,
            "first_purchase_date": "2000-01-01",
            "second_purchase_date": "2020-05-05",
            "construction": {
                "loans": 123,
                "interest": 234,
                "debt_free_purchase_price": 345,
                "additional_work": 456,
            },
        },
        "building": building.uuid.hex,
        "notes": "Lorem ipsum",
        "ownerships": [
            {
                "owner": {"id": person1.uuid.hex},
                "percentage": 50,
                "start_date": "2020-01-01",
                "end_date": None,
            },
            {
                "owner": {"id": person2.uuid.hex},
                "percentage": 50,
                "start_date": "2020-01-01",
                "end_date": None,
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
                "ownerships": [],
            }
        )
        del data["shares"]
        del data["prices"]

    response = api_client.post(reverse("hitas:apartment-list"), data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()

    ap = Apartment.objects.first()
    assert response.json()["id"] == ap.uuid.hex
    assert len(response.json()["ownerships"]) == 0 if minimal_data else 2

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
        (
            {"shares": {"start": "foo"}},
            [
                {"field": "shares.start", "message": "A valid integer is required."},
                {"field": "shares.end", "message": "This field is mandatory and cannot be blank."},
            ],
        ),
        (
            {"shares": {"end": "foo"}},
            [
                {"field": "shares.start", "message": "This field is mandatory and cannot be blank."},
                {"field": "shares.end", "message": "A valid integer is required."},
            ],
        ),
        (
            {"shares": {"start": 100}},
            [{"field": "shares.end", "message": "This field is mandatory and cannot be blank."}],
        ),
        (
            {"shares": {"start": None, "end": 100}},
            [{"field": "shares.start", "message": "This field is mandatory and cannot be blank."}],
        ),
        (
            {"shares": {"start": 100, "end": 50}},
            [{"field": "non_field_errors", "message": "share_number_start must not be greater than share_number_end"}],
        ),
        (
            {"shares": {"start": 0, "end": 0}},
            [
                {"field": "shares.start", "message": "Ensure this value is greater than or equal to 1."},
                {"field": "shares.end", "message": "Ensure this value is greater than or equal to 1."},
            ],
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
        ({"stair": None}, [{"field": "stair", "message": "This field is mandatory and cannot be blank."}]),
        (
            {"prices": {"debt_free_purchase_price": -1}},
            [
                {
                    "field": "prices.debt_free_purchase_price",
                    "message": "Ensure this value is greater than or equal to 0.",
                }
            ],
        ),
        (
            {"prices": {"purchase_price": -1}},
            [{"field": "prices.purchase_price", "message": "Ensure this value is greater than or equal to 0."}],
        ),
        (
            {"prices": {"primary_loan_amount": -1}},
            [{"field": "prices.primary_loan_amount", "message": "Ensure this value is greater than or equal to 0."}],
        ),
        (
            {"prices": {"construction": {"loans": -1}}},
            [{"field": "prices.construction.loans", "message": "Ensure this value is greater than or equal to 0."}],
        ),
        (
            {"prices": {"construction": {"interest": -1}}},
            [{"field": "prices.construction.interest", "message": "Ensure this value is greater than or equal to 0."}],
        ),
        (
            {"prices": {"construction": {"debt_free_purchase_price": -1}}},
            [
                {
                    "field": "prices.construction.debt_free_purchase_price",
                    "message": "Ensure this value is greater than or equal to 0.",
                }
            ],
        ),
        (
            {"prices": {"construction": {"additional_work": -1}}},
            [
                {
                    "field": "prices.construction.additional_work",
                    "message": "Ensure this value is greater than or equal to 0.",
                }
            ],
        ),
        ({"building": None}, [{"field": "building", "message": "This field is mandatory and cannot be blank."}]),
        ({"notes": None}, [{"field": "notes", "message": "This field is mandatory and cannot be blank."}]),
        ({"ownerships": None}, [{"field": "ownerships", "message": "This field is mandatory and cannot be blank."}]),
        (
            {
                "ownerships": [
                    {
                        "owner": {"id": "2fe3789b72f24456950e39d06ee9977a"},
                        "percentage": 100,
                        "start_date": "2020-01-01",
                        "end_date": None,
                    },
                    {
                        "owner": {"id": "0001e769ae2d40b9ae56ebd615e919d3"},
                        "percentage": 50,
                        "start_date": "2020-01-01",
                        "end_date": None,
                    },
                ]
            },
            [
                {
                    "field": "ownerships.percentage",
                    "message": "Ownership percentage of all ownerships combined must"
                    " be equal to 100. (Given sum was 150.00)",
                }
            ],
        ),
        (
            {
                "ownerships": [
                    {
                        "owner": {"id": "2fe3789b72f24456950e39d06ee9977a"},
                        "percentage": 10,
                        "start_date": "2020-01-01",
                        "end_date": None,
                    },
                    {
                        "owner": {"id": "0001e769ae2d40b9ae56ebd615e919d3"},
                        "percentage": 10,
                        "start_date": "2020-01-01",
                        "end_date": None,
                    },
                ]
            },
            [
                {
                    "field": "ownerships.percentage",
                    "message": "Ownership percentage of all ownerships combined must"
                    " be equal to 100. (Given sum was 20.00)",
                }
            ],
        ),
        (
            {
                "ownerships": [
                    {
                        "owner": {"id": "2fe3789b72f24456950e39d06ee9977a"},
                        "percentage": 100,
                        "start_date": "2020-01-01",
                        "end_date": None,
                    },
                    {
                        "owner": {"id": "0001e769ae2d40b9ae56ebd615e919d3"},
                        "percentage": 0,
                        "start_date": "2020-01-01",
                        "end_date": None,
                    },
                ]
            },
            [
                {
                    "field": "ownerships.percentage",
                    "message": "Ownership percentage greater than 0 and less than"
                    " or equal to 100. (Given value was 0.00)",
                }
            ],
        ),
        (
            {
                "ownerships": [
                    {
                        "owner": {"id": "2fe3789b72f24456950e39d06ee9977a"},
                        "percentage": 200,
                        "start_date": "2020-01-01",
                        "end_date": None,
                    },
                    {
                        "owner": {"id": "0001e769ae2d40b9ae56ebd615e919d3"},
                        "percentage": -100,
                        "start_date": "2020-01-01",
                        "end_date": None,
                    },
                ]
            },
            [{"field": "ownerships.percentage", "message": "Ensure this value is greater than or equal to 0."}],
        ),
        (
            {
                "ownerships": [
                    {
                        "owner": {"id": "2fe3789b72f24456950e39d06ee9977a"},
                        "percentage": "foo",
                        "start_date": "2020-01-01",
                        "end_date": None,
                    },
                    {
                        "owner": {"id": "0001e769ae2d40b9ae56ebd615e919d3"},
                        "percentage": "baz",
                        "start_date": "2020-01-01",
                        "end_date": None,
                    },
                ]
            },
            [
                {"field": "ownerships.percentage", "message": "A valid number is required."},
                {"field": "ownerships.percentage", "message": "A valid number is required."},
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
def test__api__apartment__update__clear_ownerships(api_client: HitasAPIClient):
    ap: Apartment = ApartmentFactory.create()
    apartment_type: ApartmentType = ApartmentTypeFactory.create()
    building: Building = BuildingFactory.create()
    OwnershipFactory.create(apartment=ap)

    data = {
        "state": ApartmentState.SOLD.value,
        "apartment_type": {"id": apartment_type.uuid.hex},
        "surface_area": 100,
        "shares": {
            "start": 101,
            "end": 200,
        },
        "address": {
            "street_address": "TestStreet 3",
            "postal_code": building.real_estate.housing_company.postal_code.value,
            "city": "Helsinki",
        },
        "apartment_number": 9,
        "floor": "5",
        "stair": "X",
        "prices": {
            "debt_free_purchase_price": 11111,
            "purchase_price": 22222,
            "primary_loan_amount": 33333,
            "first_purchase_date": "1999-01-01",
            "second_purchase_date": "2010-08-01",
            "construction": {
                "loans": 44444,
                "interest": 55555,
                "debt_free_purchase_price": 66666,
                "additional_work": 77777,
            },
        },
        "building": building.uuid.hex,
        "notes": "Test Notes",
        "ownerships": [],
    }

    response = api_client.put(reverse("hitas:apartment-detail", args=[ap.uuid.hex]), data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()

    ap.refresh_from_db()
    assert ap.state.value == data["state"]
    assert ap.apartment_type == apartment_type
    assert ap.surface_area == data["surface_area"]
    assert ap.share_number_start == data["shares"]["start"]
    assert ap.share_number_end == data["shares"]["end"]
    assert ap.street_address == data["address"]["street_address"]
    assert ap.building.real_estate.housing_company.postal_code.value == data["address"]["postal_code"]
    assert ap.building.real_estate.housing_company.city == data["address"]["city"]
    assert ap.apartment_number == data["apartment_number"]
    assert ap.floor == data["floor"]
    assert ap.stair == data["stair"]
    assert ap.debt_free_purchase_price == data["prices"]["debt_free_purchase_price"]
    assert ap.purchase_price == data["prices"]["purchase_price"]
    assert ap.primary_loan_amount == data["prices"]["primary_loan_amount"]
    assert str(ap.first_purchase_date) == data["prices"]["first_purchase_date"]
    assert str(ap.second_purchase_date) == data["prices"]["second_purchase_date"]
    assert ap.loans_during_construction == data["prices"]["construction"]["loans"]
    assert ap.interest_during_construction == data["prices"]["construction"]["interest"]
    assert ap.debt_free_purchase_price_during_construction == data["prices"]["construction"]["debt_free_purchase_price"]
    assert ap.additional_work_during_construction == data["prices"]["construction"]["additional_work"]
    assert ap.building == building
    assert ap.notes == data["notes"]
    assert ap.ownerships.all().count() == 0

    get_response = api_client.get(reverse("hitas:apartment-detail", args=[ap.uuid.hex]))
    assert response.json() == get_response.json()


@pytest.mark.parametrize(
    "owner_data",
    [
        [
            {
                "owner": {"id": "2fe3789b72f24456950e39d06ee9977a"},
                "percentage": 100,
                "start_date": "2020-01-01",
                "end_date": None,
            }
        ],
        [
            {
                "owner": {"id": "2fe3789b72f24456950e39d06ee9977a"},
                "percentage": 50,
                "start_date": "2020-01-01",
                "end_date": None,
            },
            {
                "owner": {"id": "697d6ef6fb8f4fc386a42aa9fd57eac3"},
                "percentage": 50,
                "start_date": "2020-01-01",
                "end_date": None,
            },
        ],
        [
            {
                "owner": {"id": "2fe3789b72f24456950e39d06ee9977a"},
                "percentage": 33.33,
                "start_date": "2020-01-01",
                "end_date": None,
            },
            {
                "owner": {"id": "697d6ef6fb8f4fc386a42aa9fd57eac3"},
                "percentage": 33.33,
                "start_date": "2020-01-01",
                "end_date": None,
            },
            {
                "owner": {"id": "2b44c90e8e0448a3b75399e66a220a1d"},
                "percentage": 33.34,
                "start_date": "2020-01-01",
                "end_date": None,
            },
        ],
    ],
)
@pytest.mark.django_db
def test__api__apartment__update__update_owner(api_client: HitasAPIClient, owner_data: list):
    ap: Apartment = ApartmentFactory.create()
    OwnershipFactory.create(apartment=ap)
    PersonFactory.create(uuid=UUID("2fe3789b-72f2-4456-950e-39d06ee9977a"))
    PersonFactory.create(uuid=UUID("697d6ef6-fb8f-4fc3-86a4-2aa9fd57eac3"))
    PersonFactory.create(uuid=UUID("2b44c90e-8e04-48a3-b753-99e66a220a1d"))

    data = ApartmentDetailSerializer(ap).data
    data["ownerships"] = owner_data

    response = api_client.put(reverse("hitas:apartment-detail", args=[ap.uuid.hex]), data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()

    ap.refresh_from_db()
    assert ap.ownerships.all().count() == len(owner_data)

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
    OwnershipFactory.create(apartment=ap)

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
    OwnershipFactory.create(apartment__state=ApartmentState.FREE, owner__first_name="Megatron")
    OwnershipFactory.create(apartment__state=ApartmentState.FREE, owner__last_name="Opetimus Prime")
    OwnershipFactory.create(apartment__state=ApartmentState.FREE, owner__social_security_number="010199-123A")
    hc = HousingCompanyFactory.create(postal_code__value="99999")
    ApartmentFactory.create(building__real_estate__housing_company=hc)

    url = reverse("hitas:apartment-list") + "?" + urlencode(selected_filter)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == 1, response.json()
