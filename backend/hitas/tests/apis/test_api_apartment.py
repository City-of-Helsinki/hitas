import uuid
from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status

from hitas.models import (
    Apartment,
    ApartmentMarketPriceImprovement,
    ApartmentType,
    Building,
    HousingCompany,
    Owner,
    Ownership,
    RealEstate,
)
from hitas.models.apartment import ApartmentConstructionPriceImprovement, ApartmentState
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import (
    ApartmentConstructionPriceImprovementFactory,
    ApartmentFactory,
    ApartmentMarketPriceImprovementFactory,
    ApartmentTypeFactory,
    BuildingFactory,
    HousingCompanyFactory,
    OwnerFactory,
    OwnershipFactory,
    RealEstateFactory,
)
from hitas.views.apartment import ApartmentDetailSerializer

# List tests


@pytest.mark.django_db
def test__api__apartment__list__empty(api_client: HitasAPIClient):
    building = BuildingFactory.create()

    response = api_client.get(reverse("hitas:apartment-list", args=[building.real_estate.housing_company.uuid.hex]))

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "contents": [],
        "page": {
            "size": 0,
            "current_page": 1,
            "total_items": 0,
            "total_pages": 1,
            "links": {
                "next": None,
                "previous": None,
            },
        },
    }


@pytest.mark.django_db
def test__api__apartment__list(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    re: RealEstate = RealEstateFactory.create(housing_company=hc)
    b: Building = BuildingFactory.create(real_estate=re)
    ap1: Apartment = ApartmentFactory.create(building=b)
    ap2: Apartment = ApartmentFactory.create(building=b)
    o1: Ownership = OwnershipFactory.create(apartment=ap1, percentage=50)
    o2: Ownership = OwnershipFactory.create(apartment=ap1, percentage=50)

    response = api_client.get(reverse("hitas:apartment-list", args=[hc.uuid.hex]))

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "contents": [
            {
                "id": ap1.uuid.hex,
                "state": ap1.state.value,
                "type": ap1.apartment_type.value,
                "surface_area": float(ap1.surface_area),
                "address": {
                    "street_address": ap1.street_address,
                    "postal_code": hc.postal_code.value,
                    "city": hc.postal_code.city,
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
                        "id": hc.uuid.hex,
                        "display_name": hc.display_name,
                        "link": f"/api/v1/housing-companies/{hc.uuid.hex}",
                    },
                    "real_estate": {
                        "id": ap1.building.real_estate.uuid.hex,
                        "link": (
                            f"/api/v1/housing-companies/{hc.uuid.hex}"
                            f"/real-estates/{ap1.building.real_estate.uuid.hex}"
                        ),
                    },
                    "building": {
                        "id": ap1.building.uuid.hex,
                        "street_address": ap1.building.street_address,
                        "link": (
                            f"/api/v1/housing-companies/{hc.uuid.hex}"
                            f"/real-estates/{ap1.building.real_estate.uuid.hex}"
                            f"/buildings/{ap1.building.uuid.hex}"
                        ),
                    },
                    "apartment": {
                        "id": ap1.uuid.hex,
                        "link": f"/api/v1/housing-companies/{hc.uuid.hex}/apartments/{ap1.uuid.hex}",
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
                    "postal_code": hc.postal_code.value,
                    "city": hc.postal_code.city,
                    "apartment_number": ap2.apartment_number,
                    "stair": ap2.stair,
                    "floor": ap2.floor,
                },
                "completion_date": str(ap2.completion_date),
                "ownerships": [],
                "links": {
                    "housing_company": {
                        "id": hc.uuid.hex,
                        "display_name": hc.display_name,
                        "link": f"/api/v1/housing-companies/{hc.uuid.hex}",
                    },
                    "real_estate": {
                        "id": ap2.building.real_estate.uuid.hex,
                        "link": (
                            f"/api/v1/housing-companies/{hc.uuid.hex}"
                            f"/real-estates/{ap2.building.real_estate.uuid.hex}"
                        ),
                    },
                    "building": {
                        "id": ap2.building.uuid.hex,
                        "street_address": ap2.building.street_address,
                        "link": (
                            f"/api/v1/housing-companies/{hc.uuid.hex}"
                            f"/real-estates/{ap2.building.real_estate.uuid.hex}"
                            f"/buildings/{ap2.building.uuid.hex}"
                        ),
                    },
                    "apartment": {
                        "id": ap2.uuid.hex,
                        "link": f"/api/v1/housing-companies/{hc.uuid.hex}/apartments/{ap2.uuid.hex}",
                    },
                },
            },
        ],
        "page": {
            "size": 2,
            "current_page": 1,
            "total_items": 2,
            "total_pages": 1,
            "links": {
                "next": None,
                "previous": None,
            },
        },
    }


# Retrieve tests


@pytest.mark.django_db
def test__api__apartment__retrieve(api_client: HitasAPIClient):
    ap: Apartment = ApartmentFactory.create()
    hc: HousingCompany = ap.building.real_estate.housing_company
    owner: Ownership = OwnershipFactory.create(apartment=ap)
    cpi: ApartmentConstructionPriceImprovement = ApartmentConstructionPriceImprovementFactory.create(apartment=ap)
    mpi: ApartmentMarketPriceImprovement = ApartmentMarketPriceImprovementFactory.create(apartment=ap)

    response = api_client.get(
        reverse(
            "hitas:apartment-detail",
            args=[hc.uuid.hex, ap.uuid.hex],
        )
    )

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": ap.uuid.hex,
        "state": ap.state.value,
        "type": {
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
            "apartment_number": ap.apartment_number,
            "floor": ap.floor,
            "stair": ap.stair,
        },
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
        "links": {
            "housing_company": {
                "id": hc.uuid.hex,
                "display_name": hc.display_name,
                "link": f"/api/v1/housing-companies/{hc.uuid.hex}",
            },
            "real_estate": {
                "id": ap.building.real_estate.uuid.hex,
                "link": f"/api/v1/housing-companies/{hc.uuid.hex}/real-estates/{ap.building.real_estate.uuid.hex}",
            },
            "building": {
                "id": ap.building.uuid.hex,
                "street_address": ap.building.street_address,
                "link": (
                    f"/api/v1/housing-companies/{hc.uuid.hex}"
                    f"/real-estates/{ap.building.real_estate.uuid.hex}"
                    f"/buildings/{ap.building.uuid.hex}"
                ),
            },
            "apartment": {
                "id": ap.uuid.hex,
                "link": f"/api/v1/housing-companies/{hc.uuid.hex}/apartments/{ap.uuid.hex}",
            },
        },
        "ownerships": [
            {
                "owner": {
                    "id": owner.owner.uuid.hex,
                    "name": owner.owner.name,
                    "identifier": owner.owner.identifier,
                    "email": owner.owner.email,
                },
                "percentage": float(owner.percentage),
                "start_date": str(owner.start_date) if owner.start_date else None,
                "end_date": None,
            },
        ],
        "improvements": {
            "construction_price_index": [
                {
                    "name": cpi.name,
                    "value": cpi.value,
                    "completion_date": cpi.completion_date.strftime("%Y-%m"),
                    "depreciation_percentage": cpi.depreciation_percentage.value,
                },
            ],
            "market_price_index": [
                {
                    "name": mpi.name,
                    "value": mpi.value,
                    "completion_date": mpi.completion_date.strftime("%Y-%m"),
                },
            ],
        },
        "notes": ap.notes,
    }


@pytest.mark.parametrize("invalid_id", ["foo", "38432c233a914dfb9c2f54d9f5ad9063"])
@pytest.mark.django_db
def test__api__apartment__invalid_apartment_id(api_client: HitasAPIClient, invalid_id):
    a: Apartment = ApartmentFactory.create()

    response = api_client.get(
        reverse(
            "hitas:apartment-detail",
            args=[
                a.building.real_estate.housing_company.uuid.hex,
                invalid_id,
            ],
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
def test__api__apartment__incorrect_housing_company_id(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create()
    hc: HousingCompany = HousingCompanyFactory.create()

    response = api_client.get(
        reverse(
            "hitas:apartment-detail",
            args=[hc.uuid.hex, a.uuid.hex],
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
def test__api__apartment__invalid_housing_company_id(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create()

    response = api_client.get(
        reverse(
            "hitas:apartment-detail",
            args=[uuid.uuid4().hex, a.uuid.hex],
        )
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "housing_company_not_found",
        "message": "Housing company not found",
        "reason": "Not Found",
        "status": 404,
    }


# Create tests


def get_apartment_create_data(building: Building) -> dict[str, Any]:
    apartment_type: ApartmentType = ApartmentTypeFactory.create()
    owner1: Owner = OwnerFactory.create()
    owner2: Owner = OwnerFactory.create()

    data = {
        "state": ApartmentState.SOLD.value,
        "type": {"id": apartment_type.uuid.hex},
        "surface_area": 69,
        "shares": {
            "start": 20,
            "end": 100,
        },
        "address": {
            "street_address": "TestStreet 3",
            "apartment_number": 58,
            "floor": "1",
            "stair": "A",
        },
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
        "ownerships": [
            {
                "owner": {"id": owner1.uuid.hex},
                "percentage": 50,
                "start_date": "2020-01-01",
                "end_date": None,
            },
            {
                "owner": {"id": owner2.uuid.hex},
                "percentage": 50,
                "start_date": "2020-01-01",
                "end_date": None,
            },
        ],
        "improvements": {
            "construction_price_index": [
                {
                    "value": 1234,
                    "name": "test-construction-price-1",
                    "completion_date": "2020-01",
                    "depreciation_percentage": 10,
                },
                {
                    "value": 2345,
                    "name": "test-construction-price-2",
                    "completion_date": "2023-12",
                    "depreciation_percentage": 2.5,
                },
            ],
            "market_price_index": [
                {"value": 3456, "name": "test-market-price-1", "completion_date": "1998-05"},
            ],
        },
        "building": building.uuid.hex,
        "notes": "Lorem ipsum",
    }
    return data


@pytest.mark.parametrize("minimal_data", [False, True])
@pytest.mark.django_db
def test__api__apartment__create(api_client: HitasAPIClient, minimal_data: bool):
    b = BuildingFactory.create()

    data = get_apartment_create_data(b)
    if minimal_data:
        data.update(
            {
                "notes": "",
                "ownerships": [],
                "improvements": {
                    "market_price_index": [],
                    "construction_price_index": [],
                },
            }
        )
        data["shares"] = None
        del data["prices"]

    response = api_client.post(
        reverse(
            "hitas:apartment-list",
            args=[b.real_estate.housing_company.uuid.hex],
        ),
        data=data,
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED, response.json()

    ap = Apartment.objects.first()
    assert response.json()["id"] == ap.uuid.hex
    assert len(response.json()["ownerships"]) == 0 if minimal_data else 2

    get_response = api_client.get(
        reverse(
            "hitas:apartment-detail",
            args=[b.real_estate.housing_company.uuid.hex, ap.uuid.hex],
        )
    )
    assert response.json() == get_response.json()


@pytest.mark.parametrize(
    "invalid_data,fields",
    [
        ({"state": None}, [{"field": "state", "message": "This field is mandatory and cannot be null."}]),
        ({"state": ""}, [{"field": "state", "message": "This field is mandatory and cannot be blank."}]),
        (
            {"state": "invalid_state"},
            [
                {
                    "field": "state",
                    "message": "Unsupported value 'invalid_state'. Supported values are: ['free', 'reserved', 'sold'].",
                }
            ],
        ),
        (
            {"type": None},
            [{"field": "type", "message": "This field is mandatory and cannot be null."}],
        ),
        (
            {"type": {}},
            [{"field": "type.id", "message": "This field is mandatory and cannot be null."}],
        ),
        (
            {"type": {"id": None}},
            [{"field": "type.id", "message": "This field is mandatory and cannot be null."}],
        ),
        (
            {"type": {"id": "foo"}},
            [{"field": "type.id", "message": "Object does not exist with given id 'foo'."}],
        ),
        (
            {"surface_area": None},
            [{"field": "surface_area", "message": "This field is mandatory and cannot be null."}],
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
                {"field": "shares.end", "message": "This field is mandatory and cannot be null."},
            ],
        ),
        (
            {"shares": {"end": "foo"}},
            [
                {"field": "shares.start", "message": "This field is mandatory and cannot be null."},
                {"field": "shares.end", "message": "A valid integer is required."},
            ],
        ),
        (
            {"shares": {"start": 100}},
            [{"field": "shares.end", "message": "This field is mandatory and cannot be null."}],
        ),
        (
            {"shares": {"start": None, "end": 100}},
            [{"field": "shares.start", "message": "This field is mandatory and cannot be null."}],
        ),
        (
            {"shares": {"start": 100, "end": 50}},
            [{"field": "shares", "message": "'shares.start' must not be greater than 'shares.end'."}],
        ),
        (
            {"shares": {"start": 0, "end": 0}},
            [
                {"field": "shares.start", "message": "Ensure this value is greater than or equal to 1."},
                {"field": "shares.end", "message": "Ensure this value is greater than or equal to 1."},
            ],
        ),
        ({"address": None}, [{"field": "address", "message": "This field is mandatory and cannot be null."}]),
        (
            {
                "address": {
                    "street_address": None,
                    "apartment_number": None,
                    "stair": None,
                }
            },
            [
                {"field": "address.street_address", "message": "This field is mandatory and cannot be null."},
                {"field": "address.apartment_number", "message": "This field is mandatory and cannot be null."},
                {"field": "address.stair", "message": "This field is mandatory and cannot be null."},
            ],
        ),
        (
            {
                "address": {
                    "street_address": "",
                    "apartment_number": "",
                    "stair": "",
                }
            },
            [
                {"field": "address.street_address", "message": "This field is mandatory and cannot be blank."},
                {"field": "address.apartment_number", "message": "A valid integer is required."},
                {"field": "address.stair", "message": "This field is mandatory and cannot be blank."},
            ],
        ),
        (
            {
                "address": {
                    "street_address": "test",
                    "apartment_number": "foo",
                    "stair": "1",
                }
            },
            [{"field": "address.apartment_number", "message": "A valid integer is required."}],
        ),
        (
            {
                "address": {
                    "street_address": "test",
                    "apartment_number": -1,
                    "stair": "1",
                }
            },
            [{"field": "address.apartment_number", "message": "Ensure this value is greater than or equal to 0."}],
        ),
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
        ({"building": None}, [{"field": "building", "message": "This field is mandatory and cannot be null."}]),
        ({"building": ""}, [{"field": "building", "message": "This field is mandatory and cannot be blank."}]),
        ({"building": "foo"}, [{"field": "building", "message": "Object does not exist with given id 'foo'."}]),
        ({"ownerships": None}, [{"field": "ownerships", "message": "This field is mandatory and cannot be null."}]),
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
                    " be equal to 100. Given sum was 150.00.",
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
                    " be equal to 100. Given sum was 20.00.",
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
                    " or equal to 100. Given value was 0.00.",
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
        (
            {
                "ownerships": [
                    {
                        "owner": {"id": "foo"},
                        "percentage": 50,
                        "start_date": "2020-01-01",
                        "end_date": None,
                    },
                    {
                        "owner": {"id": None},
                        "percentage": 30,
                        "start_date": "2020-01-01",
                        "end_date": None,
                    },
                    {
                        "owner": {"id": "27771d28e27145caa7efbd99d2e40601"},
                        "percentage": 20,
                        "start_date": "2020-01-01",
                        "end_date": None,
                    },
                ]
            },
            [
                {
                    "field": "ownerships.owner.id",
                    "message": "Object does not exist with given id 'foo'.",
                },
                {
                    "field": "ownerships.owner.id",
                    "message": "This field is mandatory and cannot be null.",
                },
                {
                    "field": "ownerships.owner.id",
                    "message": "Object does not exist with given id '27771d28e27145caa7efbd99d2e40601'.",
                },
            ],
        ),
        ({"improvements": None}, [{"field": "improvements", "message": "This field is mandatory and cannot be null."}]),
        (
            {"improvements": {}},
            [
                {"field": "improvements.market_price_index", "message": "This field is mandatory and cannot be null."},
                {
                    "field": "improvements.construction_price_index",
                    "message": "This field is mandatory and cannot be null.",
                },
            ],
        ),
        (
            {
                "improvements": {
                    "market_price_index": [{}],
                    "construction_price_index": [],
                }
            },
            [
                {
                    "field": "improvements.market_price_index.name",
                    "message": "This field is mandatory and cannot be null.",
                },
                {
                    "field": "improvements.market_price_index.completion_date",
                    "message": "This field is mandatory and cannot be null.",
                },
                {
                    "field": "improvements.market_price_index.value",
                    "message": "This field is mandatory and cannot be null.",
                },
            ],
        ),
        (
            {
                "improvements": {
                    "market_price_index": [
                        {
                            "name": "",
                            "completion_date": "2022-01-01",
                            "value": -1,
                        }
                    ],
                    "construction_price_index": [],
                }
            },
            [
                {
                    "field": "improvements.market_price_index.name",
                    "message": "This field is mandatory and cannot be blank.",
                },
                {
                    "field": "improvements.market_price_index.completion_date",
                    "message": "Date has wrong format. Use one of these formats instead: YYYY-MM.",
                },
                {
                    "field": "improvements.market_price_index.value",
                    "message": "Ensure this value is greater than or equal to 0.",
                },
            ],
        ),
        (
            {
                "improvements": {
                    "market_price_index": [],
                    "construction_price_index": [{}],
                }
            },
            [
                {
                    "field": "improvements.construction_price_index.name",
                    "message": "This field is mandatory and cannot be null.",
                },
                {
                    "field": "improvements.construction_price_index.completion_date",
                    "message": "This field is mandatory and cannot be null.",
                },
                {
                    "field": "improvements.construction_price_index.value",
                    "message": "This field is mandatory and cannot be null.",
                },
                {
                    "field": "improvements.construction_price_index.depreciation_percentage",
                    "message": "This field is mandatory and cannot be null.",
                },
            ],
        ),
        (
            {
                "improvements": {
                    "market_price_index": [],
                    "construction_price_index": [
                        {
                            "name": "",
                            "completion_date": "2022-01-01",
                            "value": -1,
                            "depreciation_percentage": 8.0,
                        }
                    ],
                }
            },
            [
                {
                    "field": "improvements.construction_price_index.name",
                    "message": "This field is mandatory and cannot be blank.",
                },
                {
                    "field": "improvements.construction_price_index.completion_date",
                    "message": "Date has wrong format. Use one of these formats instead: YYYY-MM.",
                },
                {
                    "field": "improvements.construction_price_index.value",
                    "message": "Ensure this value is greater than or equal to 0.",
                },
                {
                    "field": "improvements.construction_price_index.depreciation_percentage",
                    "message": "Unsupported value '8.0'. Supported values are: [0.0, 2.5, 10.0].",
                },
            ],
        ),
    ],
)
@pytest.mark.django_db
def test__api__apartment__create__invalid_data(api_client: HitasAPIClient, invalid_data, fields):
    OwnerFactory.create(uuid=uuid.UUID("2fe3789b-72f2-4456-950e-39d06ee9977a"))
    OwnerFactory.create(uuid=uuid.UUID("0001e769-ae2d-40b9-ae56-ebd615e919d3"))
    b: Building = BuildingFactory.create()

    data = get_apartment_create_data(b)
    data.update(invalid_data)

    response = api_client.post(
        reverse(
            "hitas:apartment-list",
            args=[b.real_estate.housing_company.uuid.hex],
        ),
        data=data,
        format="json",
        openapi_validate_request=False,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": fields,
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__apartment__create__incorrect_building_id(api_client: HitasAPIClient):
    b1: Building = BuildingFactory.create()
    b2: Building = BuildingFactory.create()
    data = get_apartment_create_data(b1)
    data["building"] = b2.uuid.hex

    response = api_client.post(
        reverse(
            "hitas:apartment-list",
            args=[b1.real_estate.housing_company.uuid.hex],
        ),
        data=data,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [{"field": "building", "message": f"Object does not exist with given id '{b2.uuid.hex}'."}],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


# Update tests


@pytest.mark.django_db
def test__api__apartment__update__clear_ownerships_and_improvements(api_client: HitasAPIClient):
    ap: Apartment = ApartmentFactory.create()
    OwnershipFactory.create(apartment=ap)
    ApartmentConstructionPriceImprovementFactory.create(apartment=ap)
    ApartmentMarketPriceImprovementFactory.create(apartment=ap)

    data = {
        "state": ApartmentState.SOLD.value,
        "type": {"id": ap.apartment_type.uuid.hex},
        "surface_area": 100,
        "shares": {
            "start": 101,
            "end": 200,
        },
        "address": {
            "street_address": "TestStreet 3",
            "apartment_number": 9,
            "floor": "5",
            "stair": "X",
        },
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
        "notes": "Test Notes",
        "building": ap.building.uuid.hex,
        "ownerships": [],
        "completion_date": None,
        "improvements": {
            "construction_price_index": [],
            "market_price_index": [],
        },
    }

    response = api_client.put(
        reverse(
            "hitas:apartment-detail",
            args=[ap.building.real_estate.housing_company.uuid.hex, ap.uuid.hex],
        ),
        data=data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    ap.refresh_from_db()
    assert ap.state.value == data["state"]
    assert ap.apartment_type.uuid.hex == data["type"]["id"]
    assert ap.surface_area == data["surface_area"]
    assert ap.share_number_start == data["shares"]["start"]
    assert ap.share_number_end == data["shares"]["end"]
    assert ap.street_address == data["address"]["street_address"]
    assert ap.apartment_number == data["address"]["apartment_number"]
    assert ap.floor == data["address"]["floor"]
    assert ap.stair == data["address"]["stair"]
    assert ap.debt_free_purchase_price == data["prices"]["debt_free_purchase_price"]
    assert ap.purchase_price == data["prices"]["purchase_price"]
    assert ap.primary_loan_amount == data["prices"]["primary_loan_amount"]
    assert str(ap.first_purchase_date) == data["prices"]["first_purchase_date"]
    assert str(ap.second_purchase_date) == data["prices"]["second_purchase_date"]
    assert ap.loans_during_construction == data["prices"]["construction"]["loans"]
    assert ap.interest_during_construction == data["prices"]["construction"]["interest"]
    assert ap.debt_free_purchase_price_during_construction == data["prices"]["construction"]["debt_free_purchase_price"]
    assert ap.additional_work_during_construction == data["prices"]["construction"]["additional_work"]
    assert ap.notes == data["notes"]
    assert ap.ownerships.count() == 0
    assert ap.construction_price_improvements.count() == 0
    assert ap.market_price_improvements.count() == 0

    get_response = api_client.get(
        reverse(
            "hitas:apartment-detail",
            args=[ap.building.real_estate.housing_company.uuid.hex, ap.uuid.hex],
        )
    )
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
    b: Building = ap.building
    OwnershipFactory.create(apartment=ap)
    OwnerFactory.create(uuid=uuid.UUID("2fe3789b-72f2-4456-950e-39d06ee9977a"))
    OwnerFactory.create(uuid=uuid.UUID("697d6ef6-fb8f-4fc3-86a4-2aa9fd57eac3"))
    OwnerFactory.create(uuid=uuid.UUID("2b44c90e-8e04-48a3-b753-99e66a220a1d"))

    data = ApartmentDetailSerializer(ap).data
    del data["id"]
    del data["type"]["value"]
    del data["type"]["description"]
    del data["type"]["code"]
    del data["shares"]["total"]
    del data["address"]["postal_code"]
    del data["address"]["city"]
    del data["links"]
    data["ownerships"] = owner_data
    data["building"] = b.uuid.hex

    response = api_client.put(
        reverse(
            "hitas:apartment-detail",
            args=[b.real_estate.housing_company.uuid.hex, ap.uuid.hex],
        ),
        data=data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    ap.refresh_from_db()
    assert ap.ownerships.all().count() == len(owner_data)

    get_response = api_client.get(
        reverse(
            "hitas:apartment-detail",
            args=[b.real_estate.housing_company.uuid.hex, ap.uuid.hex],
        )
    )
    assert response.json() == get_response.json()


# Delete tests


@pytest.mark.django_db
def test__api__apartment__delete(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create()

    url = reverse(
        "hitas:apartment-detail",
        args=[
            a.building.real_estate.housing_company.uuid.hex,
            a.uuid.hex,
        ],
    )
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()

    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


@pytest.mark.django_db
def test__api__apartment__delete__with_references(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create()
    OwnershipFactory.create(apartment=a)

    url = reverse(
        "hitas:apartment-detail",
        args=[
            a.building.real_estate.housing_company.uuid.hex,
            a.uuid.hex,
        ],
    )
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()

    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
