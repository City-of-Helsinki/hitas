import datetime
from datetime import date
from decimal import Decimal
from typing import Any

import pytest
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status

from hitas import exceptions
from hitas.models import (
    Apartment,
    Building,
    BuildingType,
    Developer,
    FinancingMethod,
    HitasPostalCode,
    HousingCompany,
    HousingCompanyConstructionPriceImprovement,
    HousingCompanyMarketPriceImprovement,
    HousingCompanyState,
    PropertyManager,
    RealEstate,
)
from hitas.tests.apis.helpers import HitasAPIClient, parametrize_invalid_foreign_key
from hitas.tests.factories import (
    ApartmentFactory,
    BuildingFactory,
    BuildingTypeFactory,
    DeveloperFactory,
    HitasPostalCodeFactory,
    HousingCompanyConstructionPriceImprovementFactory,
    HousingCompanyFactory,
    HousingCompanyMarketPriceImprovementFactory,
    OldHitasFinancingMethodFactory,
    OwnershipFactory,
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
    ApartmentFactory.create(building__real_estate__housing_company=hc1, completion_date=date(2020, 1, 1))
    ap2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=hc1, completion_date=date(2000, 1, 1)
    )

    response = api_client.get(reverse("hitas:housing-company-list"))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "id": hc1.uuid.hex,
            "name": hc1.display_name,
            "state": hc1.state.value,
            "address": {
                "street_address": hc1.street_address,
                "postal_code": hc1.postal_code.value,
                "city": hc1.postal_code.city,
            },
            "area": {"name": hc1.postal_code.city, "cost_area": hc1.postal_code.cost_area},
            "date": str(ap2.completion_date),
        },
        {
            "id": hc2.uuid.hex,
            "name": hc2.display_name,
            "state": hc2.state.value,
            "address": {
                "street_address": hc2.street_address,
                "postal_code": hc2.postal_code.value,
                "city": hc2.postal_code.city,
            },
            "area": {"name": hc2.postal_code.city, "cost_area": hc2.postal_code.cost_area},
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
    response = api_client.get(
        reverse("hitas:housing-company-list"), {"page": page_number}, openapi_validate_request=False
    )
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


@pytest.mark.parametrize("apt_with_null_prices", [False, True])
@pytest.mark.django_db
def test__api__housing_company__retrieve(api_client: HitasAPIClient, apt_with_null_prices: bool):
    hc1: HousingCompany = HousingCompanyFactory.create()
    hc1_re1: RealEstate = RealEstateFactory.create(housing_company=hc1)
    hc1_re1_bu1: Building = BuildingFactory.create(real_estate=hc1_re1)
    ApartmentFactory.create(
        building=hc1_re1_bu1,
        completion_date=date(2022, 1, 1),
        debt_free_purchase_price=100.5,
        primary_loan_amount=200.0,
        surface_area=10.5,
        share_number_end=100,
        share_number_start=1,
    )
    hc1_re1_bu1_ap2: Apartment = ApartmentFactory.create(
        building=hc1_re1_bu1,
        completion_date=date(2020, 1, 1),
        debt_free_purchase_price=300.5,
        primary_loan_amount=400.0,
        surface_area=20.5,
        share_number_end=200,
        share_number_start=101,
    )
    hc1_re1_bu2: Building = BuildingFactory.create(real_estate=hc1_re1)
    ApartmentFactory.create(
        building=hc1_re1_bu2,
        completion_date=date(2021, 1, 1),
        debt_free_purchase_price=500.0,
        primary_loan_amount=600.5,
        surface_area=20.0,
        share_number_end=450,
        share_number_start=201,
    )
    hc1_re2: RealEstate = RealEstateFactory.create(housing_company=hc1)
    hc1_re2_bu1: Building = BuildingFactory.create(real_estate=hc1_re2)
    if apt_with_null_prices:
        # Make sure an Apartment with null prices doesn't affect Housing Company's summary values
        ApartmentFactory.create(
            surface_area=50,
            first_purchase_date=None,
            latest_purchase_date=None,
            debt_free_purchase_price=None,
            purchase_price=None,
            primary_loan_amount=None,
            additional_work_during_construction=None,
            loans_during_construction=None,
            interest_during_construction_6=None,
            interest_during_construction_14=None,
            debt_free_purchase_price_during_construction=None,
        )

    mpi: HousingCompanyConstructionPriceImprovement = HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=hc1
    )
    cpi: HousingCompanyConstructionPriceImprovement = HousingCompanyConstructionPriceImprovementFactory.create(
        housing_company=hc1
    )

    # Second HousingCompany with a building
    BuildingFactory.create()

    response = api_client.get(reverse("hitas:housing-company-detail", args=[hc1.uuid.hex]))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": hc1.uuid.hex,
        "business_id": hc1.business_id,
        "name": {"display": hc1.display_name, "official": hc1.official_name},
        "state": hc1.state.value,
        "address": {"city": "Helsinki", "postal_code": hc1.postal_code.value, "street_address": hc1.street_address},
        "area": {"name": hc1.postal_code.city, "cost_area": hc1.postal_code.cost_area},
        "date": str(hc1_re1_bu1_ap2.completion_date),
        "summary": {
            "realized_acquisition_price": 2101.5,  # (100.5+200+300.5+400+500+600.5) = 2101.5
            "average_price_per_square_meter": 41.0,  # (100+200+300+400+500+600) / (10.5+20.5+20.5) = 2101.5 / 51.0 = 41
            "total_shares": 450,  # (100 - 1 + 1) + (200 - 101 + 1) + (450 - 201 + 1) = 100 + 100 + 250 = 450
            "total_surface_area": 51.0,  # 10.5+20.5+20
        },
        "real_estates": [
            {
                "id": hc1_re1.uuid.hex,
                "address": {
                    "city": "Helsinki",
                    "postal_code": hc1_re1.postal_code.value,
                    "street_address": hc1_re1.street_address,
                },
                "property_identifier": hc1_re1.property_identifier,
                "buildings": [
                    {
                        "id": hc1_re1_bu1.uuid.hex,
                        "address": {
                            "city": "Helsinki",
                            "postal_code": hc1_re1_bu1.postal_code.value,
                            "street_address": hc1_re1_bu1.street_address,
                        },
                        "building_identifier": hc1_re1_bu1.building_identifier,
                        "apartment_count": 2,
                    },
                    {
                        "id": hc1_re1_bu2.uuid.hex,
                        "address": {
                            "city": "Helsinki",
                            "postal_code": hc1_re1_bu2.postal_code.value,
                            "street_address": hc1_re1_bu2.street_address,
                        },
                        "building_identifier": hc1_re1_bu2.building_identifier,
                        "apartment_count": 1,
                    },
                ],
            },
            {
                "id": hc1_re2.uuid.hex,
                "address": {
                    "city": "Helsinki",
                    "postal_code": hc1_re2.postal_code.value,
                    "street_address": hc1_re2.street_address,
                },
                "property_identifier": hc1_re2.property_identifier,
                "buildings": [
                    {
                        "id": hc1_re2_bu1.uuid.hex,
                        "address": {
                            "city": "Helsinki",
                            "postal_code": hc1_re2_bu1.postal_code.value,
                            "street_address": hc1_re2_bu1.street_address,
                        },
                        "building_identifier": hc1_re2_bu1.building_identifier,
                        "apartment_count": 0,
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
                "street_address": hc1.property_manager.street_address,
                "postal_code": hc1.property_manager.postal_code,
                "city": hc1.property_manager.city,
            },
            "name": hc1.property_manager.name,
            "email": hc1.property_manager.email,
        },
        "acquisition_price": float(hc1.acquisition_price),
        "primary_loan": float(hc1.primary_loan),
        "sales_price_catalogue_confirmation_date": str(hc1.sales_price_catalogue_confirmation_date),
        "notes": hc1.notes,
        "archive_id": hc1.id,
        "notification_date": str(hc1.notification_date),
        "last_modified": {
            "datetime": hc1.last_modified_datetime.isoformat().replace("+00:00", "Z"),
            "user": {
                "username": hc1.last_modified_by.username,
                "first_name": hc1.last_modified_by.first_name,
                "last_name": hc1.last_modified_by.last_name,
            },
        },
        "improvements": {
            "construction_price_index": [
                {
                    "name": cpi.name,
                    "value": float(cpi.value),
                    "completion_date": cpi.completion_date.strftime("%Y-%m"),
                },
            ],
            "market_price_index": [
                {
                    "name": mpi.name,
                    "value": float(mpi.value),
                    "completion_date": mpi.completion_date.strftime("%Y-%m"),
                },
            ],
        },
    }


@pytest.mark.django_db
def test__api__housing_company__retrieve_rounding(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    ApartmentFactory.create(
        building__real_estate__housing_company=hc, debt_free_purchase_price=1, primary_loan_amount=2, surface_area=1
    )
    ApartmentFactory.create(
        building__real_estate__housing_company=hc, debt_free_purchase_price=1, primary_loan_amount=1, surface_area=1
    )

    response = api_client.get(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["summary"]["average_price_per_square_meter"] == 3


@pytest.mark.parametrize("invalid_id", ["foo", "38432c233a914dfb9c2f54d9f5ad9063"])
@pytest.mark.django_db
def test__api__housing_company__read__not_found(api_client: HitasAPIClient, invalid_id):
    HousingCompanyFactory.create()

    response = api_client.get(reverse("hitas:housing-company-detail", args=[invalid_id]))
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "housing_company_not_found",
        "message": "Housing company not found",
        "reason": "Not Found",
        "status": 404,
    }


# Create tests


def get_housing_company_create_data() -> dict[str, Any]:
    developer: Developer = DeveloperFactory.create()
    financing_method: FinancingMethod = OldHitasFinancingMethodFactory.create()
    building_type: BuildingType = BuildingTypeFactory.create()
    postal_code: HitasPostalCode = HitasPostalCodeFactory.create()
    property_manager: PropertyManager = PropertyManagerFactory.create()

    data = {
        "acquisition_price": 10.00,
        "address": {
            "postal_code": postal_code.value,
            "street_address": "test-street-address-1",
        },
        "building_type": {"id": building_type.uuid.hex},
        "business_id": "1234567-1",
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
        "improvements": {
            "construction_price_index": [
                {
                    "value": 1234,
                    "name": "construction-price-index-improvement-1",
                    "completion_date": "2017-01",
                },
                {
                    "value": 2345,
                    "name": "construction-price-index-improvement-2",
                    "completion_date": "2018-12",
                },
            ],
            "market_price_index": [
                {
                    "value": 3456,
                    "name": "market-price-index-improvement",
                    "completion_date": "2022-05",
                }
            ],
        },
    }
    return data


@pytest.mark.parametrize("minimal_data", [False, True])
@pytest.mark.django_db
def test__api__housing_company__create(api_client: HitasAPIClient, minimal_data: bool):
    data = get_housing_company_create_data()
    if minimal_data:
        data.update(
            {
                "business_id": None,
                "primary_loan": None,
                "property_manager": None,
                "notes": "",
                "sales_price_catalogue_confirmation_date": None,
                "improvements": {
                    "market_price_index": [],
                    "construction_price_index": [],
                },
            }
        )

    response = api_client.post(reverse("hitas:housing-company-list"), data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()

    hc = HousingCompany.objects.get(uuid=response.json()["id"])
    assert response.json()["address"]["postal_code"] == HitasPostalCode.objects.first().value

    get_response = api_client.get(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]))
    assert response.json() == get_response.json()


@pytest.mark.django_db
def test__api__housing_company__create__duplicate_official_name(api_client: HitasAPIClient):
    existing_hc: HousingCompany = HousingCompanyFactory.create(official_name="test-official-name")
    data = get_housing_company_create_data()
    data["name"]["official"] = existing_hc.official_name

    response = api_client.post(reverse("hitas:housing-company-list"), data=data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "name.official",
                "message": "Official name provided is already in use. Conflicting official name: 'test-official-name'.",
            }
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__housing_company__create__duplicate_display_name(api_client: HitasAPIClient):
    existing_hc: HousingCompany = HousingCompanyFactory.create(display_name="test-display-name")
    data = get_housing_company_create_data()
    data["name"]["display"] = existing_hc.display_name

    response = api_client.post(reverse("hitas:housing-company-list"), data=data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "name.display",
                "message": "Display name provided is already in use. Conflicting display name: 'test-display-name'.",
            }
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__housing_company__create__empty(api_client: HitasAPIClient):
    response = api_client.post(
        reverse("hitas:housing-company-list"), data={}, format="json", openapi_validate_request=False
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {"field": "name", "message": "This field is mandatory and cannot be null."},
            {"field": "state", "message": "This field is mandatory and cannot be null."},
            {"field": "address", "message": "This field is mandatory and cannot be null."},
            {"field": "financing_method", "message": "This field is mandatory and cannot be null."},
            {"field": "building_type", "message": "This field is mandatory and cannot be null."},
            {"field": "developer", "message": "This field is mandatory and cannot be null."},
            {"field": "acquisition_price", "message": "This field is mandatory and cannot be null."},
            {"field": "improvements", "message": "This field is mandatory and cannot be null."},
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.parametrize(
    "invalid_data,fields",
    [
        *parametrize_invalid_foreign_key("financing_method"),
        *parametrize_invalid_foreign_key("building_type"),
        *parametrize_invalid_foreign_key("developer"),
        *parametrize_invalid_foreign_key("property_manager", nullable=True),
        ({"business_id": "#"}, [{"field": "business_id", "message": "'#' is not a valid business id."}]),
        ({"business_id": "123"}, [{"field": "business_id", "message": "'123' is not a valid business id."}]),
        ({"name": None}, [{"field": "name", "message": "This field is mandatory and cannot be null."}]),
        ({"name": 0}, [{"field": "name", "message": "Invalid data. Expected a dictionary, but got int."}]),
        ({"state": None}, [{"field": "state", "message": "This field is mandatory and cannot be null."}]),
        (
            {"state": "invalid_state"},
            [
                {
                    "field": "state",
                    "message": (
                        "Unsupported value 'invalid_state'. Supported values are:"
                        " ['not_ready', 'lt_30_years', 'gt_30_years_not_free', 'gt_30_years_free', "
                        "'gt_30_years_plot_department_notification', 'half_hitas', 'ready_no_statistics']."
                    ),
                }
            ],
        ),
        ({"address": None}, [{"field": "address", "message": "This field is mandatory and cannot be null."}]),
        ({"address": 123}, [{"field": "address", "message": "Invalid data. Expected a dictionary, but got int."}]),
        (
            {"acquisition_price": None},
            [{"field": "acquisition_price", "message": "This field is mandatory and cannot be null."}],
        ),
        ({"primary_loan": "foo"}, [{"field": "primary_loan", "message": "A valid number is required."}]),
        ({"improvements": None}, [{"field": "improvements", "message": "This field is mandatory and cannot be null."}]),
        (
            {"improvements": {"market_price_index": None, "construction_price_index": []}},
            [{"field": "improvements.market_price_index", "message": "This field is mandatory and cannot be null."}],
        ),
        (
            {"improvements": {"market_price_index": [], "construction_price_index": None}},
            [
                {
                    "field": "improvements.construction_price_index",
                    "message": "This field is mandatory and cannot be null.",
                }
            ],
        ),
        (
            {
                "improvements": {
                    "market_price_index": [
                        {
                            "name": "foo",
                            "value": 10,
                            "completion_date": "2022-01-01",
                        }
                    ],
                    "construction_price_index": [],
                }
            },
            [
                {
                    "field": "improvements.market_price_index.completion_date",
                    "message": "Date has wrong format. Use one of these formats instead: YYYY-MM.",
                }
            ],
        ),
        (
            {
                "improvements": {
                    "market_price_index": [
                        {
                            "name": "foo",
                            "value": -1,
                            "completion_date": "2022-01",
                        }
                    ],
                    "construction_price_index": [],
                }
            },
            [
                {
                    "field": "improvements.market_price_index.value",
                    "message": "Ensure this value is greater than or equal to 0.",
                }
            ],
        ),
        (
            {
                "improvements": {
                    "market_price_index": [],
                    "construction_price_index": [
                        {
                            "name": "foo",
                            "value": 10,
                            "completion_date": "2022-01-01",
                        }
                    ],
                }
            },
            [
                {
                    "field": "improvements.construction_price_index.completion_date",
                    "message": "Date has wrong format. Use one of these formats instead: YYYY-MM.",
                }
            ],
        ),
        (
            {
                "improvements": {
                    "market_price_index": [],
                    "construction_price_index": [
                        {
                            "name": "foo",
                            "value": -1,
                            "completion_date": "2022-01",
                        }
                    ],
                }
            },
            [
                {
                    "field": "improvements.construction_price_index.value",
                    "message": "Ensure this value is greater than or equal to 0.",
                }
            ],
        ),
        (
            {"notes": None},
            [{"field": "notes", "message": "This field is mandatory and cannot be null."}],
        ),
    ],
)
@pytest.mark.django_db
def test__api__housing_company__create__invalid_data(api_client: HitasAPIClient, invalid_data, fields):
    data = get_housing_company_create_data()
    data.update(invalid_data)

    response = api_client.post(
        reverse("hitas:housing-company-list"), data=data, format="json", openapi_validate_request=False
    )
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
def test__api__housing_company__update(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    ApartmentFactory.create(building__real_estate__housing_company=hc)
    postal_code: HitasPostalCode = HitasPostalCodeFactory.create(value="99999")
    financing_method: FinancingMethod = OldHitasFinancingMethodFactory.create()
    property_manager: PropertyManager = PropertyManagerFactory.create()

    data = {
        "acquisition_price": 10.01,
        "address": {
            "street_address": "changed-street-address",
            "postal_code": postal_code.value,
        },
        "building_type": {"id": hc.building_type.uuid.hex},
        "business_id": "",
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
        "improvements": {
            "construction_price_index": [
                {
                    "value": 1234,
                    "name": "new-name",
                    "completion_date": "2017-01",
                }
            ],
            "market_price_index": [],
        },
    }

    response = api_client.put(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]), data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()

    hc.refresh_from_db()
    assert hc.postal_code == postal_code
    assert hc.financing_method == financing_method
    assert hc.property_manager == property_manager
    assert hc.business_id is None
    assert hc.street_address == "changed-street-address"
    assert hc.state == HousingCompanyState.LESS_THAN_30_YEARS
    assert hc.acquisition_price == Decimal("10.01")
    assert hc.notes == ""
    assert response.json()["date"]

    get_response = api_client.get(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]))
    assert response.json() == get_response.json()


@pytest.mark.django_db
def test__api__housing_company__update__improvements(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    mpi1: HousingCompanyMarketPriceImprovement = HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=hc, completion_date=date(2010, 1, 1)
    )
    HousingCompanyMarketPriceImprovementFactory.create(housing_company=hc, completion_date=date(2015, 5, 1))
    mpi3: HousingCompanyMarketPriceImprovement = HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=hc, completion_date=date(2020, 10, 1)
    )
    HousingCompanyConstructionPriceImprovementFactory.create(housing_company=hc, completion_date=date(2020, 1, 1))
    cpi2: HousingCompanyConstructionPriceImprovement = HousingCompanyConstructionPriceImprovementFactory.create(
        housing_company=hc, completion_date=date(2020, 2, 1)
    )
    cpi3: HousingCompanyConstructionPriceImprovement = HousingCompanyConstructionPriceImprovementFactory.create(
        housing_company=hc, completion_date=date(2020, 3, 1)
    )

    cpi2.value = 999999

    def improvement_to_dict(i):
        return {
            "value": i.value,
            "completion_date": i.completion_date.strftime("%Y-%m"),
            "name": i.name,
        }

    data = {
        "acquisition_price": hc.acquisition_price,
        "address": {
            "street_address": hc.street_address,
            "postal_code": hc.postal_code.value,
        },
        "building_type": {"id": hc.building_type.uuid.hex},
        "business_id": hc.business_id,
        "developer": {"id": hc.developer.uuid.hex},
        "financing_method": {"id": hc.financing_method.uuid.hex},
        "name": {
            "display": hc.display_name,
            "official": hc.official_name,
        },
        "notes": hc.notes,
        "primary_loan": hc.primary_loan,
        "property_manager": {"id": hc.property_manager.uuid.hex},
        "state": hc.state.value,
        "sales_price_catalogue_confirmation_date": hc.sales_price_catalogue_confirmation_date,
        "improvements": {
            "construction_price_index": list(
                map(improvement_to_dict, [cpi3, cpi2])
            ),  # remove cpi1, modify 2, change order
            "market_price_index": list(map(improvement_to_dict, [mpi1, mpi3])),  # remove mpi2
        },
    }

    response = api_client.put(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]), data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()

    get_response = api_client.get(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]))
    assert get_response.json() == get_response.json()


@pytest.mark.django_db
def test__api__housing_company__update__add_improvement(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    mpi1: HousingCompanyMarketPriceImprovement = HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=hc, completion_date=date(2010, 1, 1)
    )
    cpi1: HousingCompanyConstructionPriceImprovement = HousingCompanyConstructionPriceImprovementFactory.create(
        housing_company=hc, completion_date=date(2020, 1, 1)
    )
    cpi2 = HousingCompanyMarketPriceImprovementFactory(
        housing_company=hc, completion_date=date(2011, 1, 1), value=10, name="new-improvement"
    )

    def improvement_to_dict(i):
        return {
            "value": i.value,
            "completion_date": i.completion_date.strftime("%Y-%m"),
            "name": i.name,
        }

    data = {
        "acquisition_price": hc.acquisition_price,
        "address": {
            "street_address": hc.street_address,
            "postal_code": hc.postal_code.value,
        },
        "building_type": {"id": hc.building_type.uuid.hex},
        "business_id": hc.business_id,
        "developer": {"id": hc.developer.uuid.hex},
        "financing_method": {"id": hc.financing_method.uuid.hex},
        "name": {
            "display": hc.display_name,
            "official": hc.official_name,
        },
        "notes": hc.notes,
        "primary_loan": hc.primary_loan,
        "property_manager": {"id": hc.property_manager.uuid.hex},
        "state": hc.state.value,
        "sales_price_catalogue_confirmation_date": hc.sales_price_catalogue_confirmation_date,
        "improvements": {
            "construction_price_index": list(map(improvement_to_dict, [cpi1, cpi2])),
            "market_price_index": list(map(improvement_to_dict, [mpi1])),
        },
    }

    response = api_client.put(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]), data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()

    get_response = api_client.get(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]))
    assert get_response.json() == get_response.json()


@pytest.mark.django_db
def test__api__housing_company__update__no_changes(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()

    data = {
        "acquisition_price": hc.acquisition_price,
        "address": {
            "street_address": hc.street_address,
            "postal_code": hc.postal_code.value,
        },
        "building_type": {"id": hc.building_type.uuid.hex},
        "business_id": hc.business_id,
        "developer": {"id": hc.developer.uuid.hex},
        "financing_method": {"id": hc.financing_method.uuid.hex},
        "name": {
            "display": hc.display_name,
            "official": hc.official_name,
        },
        "notes": hc.notes,
        "primary_loan": hc.primary_loan,
        "property_manager": {"id": hc.property_manager.uuid.hex},
        "state": hc.state.value,
        "improvements": {
            "construction_price_index": [],
            "market_price_index": [],
        },
    }

    response = api_client.put(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]), data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()


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
def test__api__housing_company__delete__with_references(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    re: RealEstate = RealEstateFactory.create(housing_company=hc)
    bu: Building = BuildingFactory.create(real_estate=re)
    a: Apartment = ApartmentFactory.create(building=bu)
    OwnershipFactory.create(apartment=a)

    url = reverse("hitas:housing-company-detail", kwargs={"uuid": hc.uuid.hex})

    response = api_client.delete(url)
    assert response.status_code == status.HTTP_409_CONFLICT, response.json()

    assert response.json() == {
        "error": "real_estates_on_housing_company",
        "message": "Cannot delete a housing company with real estates.",
        "reason": "Conflict",
        "status": 409,
    }


# Filter tests


@pytest.mark.parametrize(
    "selected_filter",
    [
        {"display_name": "TestDisplayName"},
        {"display_name": "xx"},
        {"street_address": "test-street"},
        {"street_address": "xx"},
        {"property_manager": "TestPropertyManager"},
        {"property_manager": "xx"},
        {"developer": "TestDeveloper"},
        {"developer": "xx"},
        {"postal_code": "99999"},
        {"archive_id": 999},
    ],
)
@pytest.mark.django_db
def test__api__housing_company__filter(api_client: HitasAPIClient, selected_filter):
    hc: HousingCompany = HousingCompanyFactory.create(display_name="TestDisplayName")
    HousingCompanyFactory.create(official_name="TestOfficialName OY")
    HousingCompanyFactory.create(display_name="test-XX-display")
    HousingCompanyFactory.create(state=HousingCompanyState.GREATER_THAN_30_YEARS_PLOT_DEPARTMENT_NOTIFICATION)
    HousingCompanyFactory.create(street_address="test-street")
    HousingCompanyFactory.create(street_address="test-XX-street")
    HousingCompanyFactory.create(property_manager__name="TestPropertyManager")
    HousingCompanyFactory.create(property_manager__name="test-XX-property")
    HousingCompanyFactory.create(developer__value="TestDeveloper")
    HousingCompanyFactory.create(developer__value="test-XX-developer")
    HousingCompanyFactory.create(postal_code__value="99999")
    HousingCompanyFactory.create(id=999)
    RealEstateFactory.create(property_identifier="1-1234-321-56", housing_company=hc)
    RealEstateFactory.create(property_identifier="1111-1111-1111-1111", housing_company=hc)

    url = reverse("hitas:housing-company-list") + "?" + urlencode(selected_filter)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == 1, response.json()


@pytest.mark.django_db
def test__api__housing_company__filter__new_hitas__false(api_client: HitasAPIClient):
    ApartmentFactory.create(completion_date=datetime.date(2012, 1, 1))
    ApartmentFactory.create(completion_date=datetime.date(2011, 1, 1))
    apartment_just_before_2011 = ApartmentFactory.create(completion_date=datetime.date(2010, 12, 31))
    apartment_2009 = ApartmentFactory.create(completion_date=datetime.date(2009, 1, 1))

    hc_both_old_and_new = HousingCompanyFactory.create()
    ApartmentFactory.create(
        building__real_estate__housing_company=hc_both_old_and_new,
        completion_date=datetime.date(2010, 12, 31),
    )
    ApartmentFactory.create(
        building__real_estate__housing_company=hc_both_old_and_new,
        completion_date=datetime.date(2011, 1, 1),
    )

    url = reverse("hitas:housing-company-list") + "?new_hitas=false"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == 3, response.json()
    assert response.json()["contents"][0]["id"] == apartment_just_before_2011.housing_company.uuid.hex
    assert response.json()["contents"][1]["id"] == apartment_2009.housing_company.uuid.hex
    assert response.json()["contents"][2]["id"] == hc_both_old_and_new.uuid.hex


@pytest.mark.django_db
def test__api__housing_company__filter__new_hitas__true(api_client: HitasAPIClient):
    apartment_2012 = ApartmentFactory.create(completion_date=datetime.date(2012, 1, 1))
    apartment_2011 = ApartmentFactory.create(completion_date=datetime.date(2011, 1, 1))
    ApartmentFactory.create(completion_date=datetime.date(2010, 12, 31))
    ApartmentFactory.create(completion_date=datetime.date(2009, 1, 1))

    hc_both_old_and_new = HousingCompanyFactory.create()
    ApartmentFactory.create(
        building__real_estate__housing_company=hc_both_old_and_new,
        completion_date=datetime.date(2010, 12, 31),
    )
    ApartmentFactory.create(
        building__real_estate__housing_company=hc_both_old_and_new,
        completion_date=datetime.date(2011, 1, 1),
    )

    url = reverse("hitas:housing-company-list") + "?new_hitas=true"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == 2, response.json()
    assert response.json()["contents"][0]["id"] == apartment_2012.housing_company.uuid.hex
    assert response.json()["contents"][1]["id"] == apartment_2011.housing_company.uuid.hex


@pytest.mark.parametrize(
    "selected_filter,fields",
    [
        (
            {"display_name": "a"},
            [{"field": "display_name", "message": "Ensure this value has at least 2 characters (it has 1)."}],
        ),
        (
            {"street_address": "a"},
            [{"field": "street_address", "message": "Ensure this value has at least 2 characters (it has 1)."}],
        ),
        (
            {"property_manager": "a"},
            [{"field": "property_manager", "message": "Ensure this value has at least 2 characters (it has 1)."}],
        ),
        (
            {"developer": "a"},
            [{"field": "developer", "message": "Ensure this value has at least 2 characters (it has 1)."}],
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
            {"archive_id": "-1"},
            [{"field": "archive_id", "message": "Ensure this value is greater than or equal to 1."}],
        ),
        (
            {"archive_id": "0"},
            [{"field": "archive_id", "message": "Ensure this value is greater than or equal to 1."}],
        ),
    ],
)
@pytest.mark.django_db
def test__api__housing_company__filter__invalid_data(api_client: HitasAPIClient, selected_filter, fields):
    url = reverse("hitas:housing-company-list") + "?" + urlencode(selected_filter)
    response = api_client.get(url, openapi_validate_request=False)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": fields,
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }
