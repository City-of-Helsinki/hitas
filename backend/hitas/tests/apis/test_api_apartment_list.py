from datetime import date
from uuid import UUID

import pytest
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status

from hitas.models.apartment import Apartment, ApartmentSale, HousingCompany
from hitas.models.condition_of_sale import ConditionOfSale, GracePeriod
from hitas.models.housing_company import RegulationStatus
from hitas.models.owner import Owner
from hitas.models.ownership import Ownership
from hitas.tests.apis.helpers import HitasAPIClient, count_queries
from hitas.tests.factories import (
    ApartmentFactory,
    ApartmentSaleFactory,
    ConditionOfSaleFactory,
    HousingCompanyFactory,
    OwnerFactory,
    OwnershipFactory,
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
    ap1: Apartment = ApartmentFactory.create(apartment_number=1, sales=[])
    ap2: Apartment = ApartmentFactory.create(apartment_number=2, sales=[])
    hc1: HousingCompany = ap1.housing_company
    hc2: HousingCompany = ap2.housing_company
    sale: ApartmentSale = ApartmentSaleFactory.create(apartment=ap1, ownerships=[])
    o1: Ownership = OwnershipFactory.create(sale=sale, percentage=50)
    o2: Ownership = OwnershipFactory.create(sale=sale, percentage=50)

    # Database queries performed:
    # 1. Pagination count query
    # 2. Fetch apartment
    # 3. Join first sale
    # 4. Join ownerships on first sale
    # 5. Join conditions of sale where one of the ownerships is a "new ownership"
    # 6. Join conditions of sale where one of the ownerships is an "old ownership"
    with count_queries(6):
        response = api_client.get(reverse("hitas:apartment-list"))

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "id": ap1.uuid.hex,
            "is_sold": True,
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
            "rooms": ap1.rooms,
            "completion_date": str(ap1.completion_date),
            "ownerships": [
                {
                    "owner": {
                        "id": o1.owner.uuid.hex,
                        "name": o1.owner.name,
                        "identifier": o1.owner.identifier,
                        "email": o1.owner.email,
                        "non_disclosure": o1.owner.non_disclosure,
                    },
                    "percentage": float(o1.percentage),
                },
                {
                    "owner": {
                        "id": o2.owner.uuid.hex,
                        "name": o2.owner.name,
                        "identifier": o2.owner.identifier,
                        "email": o2.owner.email,
                        "non_disclosure": o2.owner.non_disclosure,
                    },
                    "percentage": float(o2.percentage),
                },
            ],
            "links": {
                "housing_company": {
                    "id": hc1.uuid.hex,
                    "display_name": hc1.display_name,
                    "official_name": hc1.official_name,
                    "regulation_status": hc1.regulation_status.value,
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
            "has_conditions_of_sale": False,
            "has_grace_period": False,
            "sell_by_date": None,
        },
        {
            "id": ap2.uuid.hex,
            "is_sold": False,
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
            "rooms": ap2.rooms,
            "links": {
                "housing_company": {
                    "id": hc2.uuid.hex,
                    "display_name": hc2.display_name,
                    "official_name": hc2.official_name,
                    "regulation_status": hc2.regulation_status.value,
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
            "has_conditions_of_sale": False,
            "has_grace_period": False,
            "sell_by_date": None,
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
def test__api__apartment__list__condition_of_sale(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    ap1: Apartment = ApartmentFactory.create(apartment_number=1, completion_date=date(2022, 1, 1), sales=[])
    ap2: Apartment = ApartmentFactory.create(apartment_number=2, completion_date=date(2023, 1, 1), sales=[])

    sale_1: ApartmentSale = ApartmentSaleFactory.create(apartment=ap1, purchase_date=date(2022, 1, 1), ownerships=[])
    o1: Ownership = OwnershipFactory.create(owner=owner, sale=sale_1, percentage=50)
    OwnershipFactory.create(sale=sale_1, percentage=50)

    sale_2: ApartmentSale = ApartmentSaleFactory.create(apartment=ap2, purchase_date=date(2022, 1, 1), ownerships=[])
    o2: Ownership = OwnershipFactory.create(owner=owner, sale=sale_2)
    ConditionOfSaleFactory.create(new_ownership=o2, old_ownership=o1, grace_period=GracePeriod.THREE_MONTHS)

    # Database queries performed:
    # 1. Pagination count query
    # 2. Fetch apartment
    # 3. Join first sale
    # 4. Join ownerships on first sale
    # 5. Join conditions of sale where one of the ownerships is a "new ownership"
    # 6. Join conditions of sale where one of the ownerships is an "old ownership"
    with count_queries(6):
        response = api_client.get(reverse("hitas:apartment-list"))

    assert response.status_code == status.HTTP_200_OK, response.json()
    contents = response.json()["contents"]
    assert len(contents) == 2
    assert contents[0]["sell_by_date"] == str(date(2023, 4, 1))
    assert contents[0]["has_grace_period"] is True
    assert contents[1]["sell_by_date"] == str(date(2023, 4, 1))
    assert contents[1]["has_grace_period"] is True


# Filter tests


@pytest.mark.parametrize(
    ["selected_filter", "number_of_apartments"],
    [
        [{"housing_company_name": "testdisplay"}, 1],
        [{"address": "est-stree"}, 3],
        [{"address": "test-street A"}, 2],
        [{"address": "test-street B 1"}, 1],
        [{"postal_code": "99999"}, 1],
        [{"owner_name": "megatr"}, 1],
        [{"owner_name": "etimus pri"}, 1],
        [{"owner_identifier": "010199-123A"}, 1],
        [{"owner_identifier": "010199-123a"}, 1],
        [{"has_conditions_of_sale": "True"}, 2],
        [{"has_conditions_of_sale": "true"}, 2],
        [{"has_conditions_of_sale": "1"}, 2],
    ],
)
@pytest.mark.django_db
def test__api__apartment__filter(api_client: HitasAPIClient, selected_filter, number_of_apartments):
    ApartmentFactory.create(
        building__real_estate__housing_company__uuid=UUID("38432c23-3a91-4dfb-9c2f-54d9f5ad9063"),
    )

    ApartmentFactory.create(
        building__real_estate__housing_company__display_name="TestDisplayName",
    )
    ApartmentFactory.create(street_address="test-street", stair="A", apartment_number=1)
    ApartmentFactory.create(street_address="test-street", stair="A", apartment_number=2)
    ApartmentFactory.create(street_address="test-street", stair="B", apartment_number=1)
    OwnershipFactory.create(owner__name="Megatron Opetimus Prime")
    OwnershipFactory.create(owner__identifier="010199-123A")
    hc = HousingCompanyFactory.create(postal_code__value="99999")
    ApartmentFactory.create(building__real_estate__housing_company=hc)

    old_apartment_1: Apartment = ApartmentFactory.create()
    new_apartment_1: Apartment = ApartmentFactory.create(completion_date=None)
    ConditionOfSaleFactory(
        new_ownership=new_apartment_1.first_sale().ownerships.first(),
        old_ownership=old_apartment_1.first_sale().ownerships.first(),
    )

    old_apartment_2: Apartment = ApartmentFactory.create()
    new_apartment_2: Apartment = ApartmentFactory.create(completion_date=None)
    cos: ConditionOfSale = ConditionOfSaleFactory(
        new_ownership=new_apartment_2.first_sale().ownerships.first(),
        old_ownership=old_apartment_2.first_sale().ownerships.first(),
    )
    cos.delete()  # fulfill condition of sale

    url = reverse("hitas:apartment-list") + "?" + urlencode(selected_filter)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == number_of_apartments, response.json()


@pytest.mark.django_db
def test__api__apartment__filter__regulation_status(api_client: HitasAPIClient):
    ApartmentFactory.create(building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED)
    ApartmentFactory.create(
        building__real_estate__housing_company__regulation_status=RegulationStatus.RELEASED_BY_PLOT_DEPARTMENT
    )
    ApartmentFactory.create(
        building__real_estate__housing_company__regulation_status=RegulationStatus.RELEASED_BY_PLOT_DEPARTMENT
    )
    ApartmentFactory.create(
        building__real_estate__housing_company__regulation_status=RegulationStatus.RELEASED_BY_HITAS
    )

    url = reverse("hitas:apartment-list") + "?is_regulated=true"
    response_json = api_client.get(url).json()["contents"]
    assert len(response_json) == 1, response_json

    url = reverse("hitas:apartment-list") + "?is_regulated=false"
    response_json = api_client.get(url).json()["contents"]
    assert len(response_json) == 3, response_json


@pytest.mark.parametrize(
    "selected_filter,fields",
    [
        (
            {"housing_company_name": "a"},
            [{"field": "housing_company_name", "message": "Ensure this value has at least 2 characters (it has 1)."}],
        ),
        (
            {"address": "a"},
            [{"field": "address", "message": "Ensure this value has at least 2 characters (it has 1)."}],
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
