import datetime

import pytest
from dateutil import relativedelta
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.http import urlencode
from rest_framework import status

from hitas.models import Apartment, HousingCompany, Ownership
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import (
    ApartmentFactory,
    HousingCompanyConstructionPriceImprovementFactory,
    HousingCompanyMarketPriceImprovementFactory,
    OwnershipFactory,
)
from hitas.tests.factories.indices import (
    ConstructionPriceIndex2005Equal100Factory,
    MarketPriceIndex2005Equal100Factory,
    SurfaceAreaPriceCeilingFactory,
)


@pytest.mark.django_db
def test__api__apartment_max_price__construction_price_index(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        debt_free_purchase_price=80350,
        primary_loan_amount=119150,
        additional_work_during_construction=0,
        completion_date=datetime.date(2019, 11, 27),
        surface_area=30.0,
        share_number_start=18402,
        share_number_end=20784,
    )
    hc: HousingCompany = a.building.real_estate.housing_company
    # Create another apartment with rest of the surface area
    ApartmentFactory.create(building__real_estate__housing_company=hc, surface_area=4302)

    HousingCompanyConstructionPriceImprovementFactory.create(
        housing_company=hc, value=150000, completion_date=datetime.date(2020, 5, 21)
    )
    HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=hc, value=150000, completion_date=datetime.date(2020, 5, 21)
    )
    o1: Ownership = OwnershipFactory.create(apartment=a, percentage=75.2)
    o2: Ownership = OwnershipFactory.create(apartment=a, percentage=24.8)

    # Create necessary apartment's completion date indices
    ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2019, 11, 1), value=129.29)
    MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2019, 11, 1), value=167.9)

    # Create necessary calculation date indices
    ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2022, 7, 1), value=146.4)
    MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2022, 7, 1), value=189.1)
    SurfaceAreaPriceCeilingFactory.create(month=datetime.date(2022, 7, 1), value=4869)

    # Create necessary improvement's completion date indices
    ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2020, 5, 1), value=129.20)
    MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2020, 5, 1), value=171.0)

    query = {
        "calculation_date": "2022-07-05",
        "apartment_share_housing_company_loans": 2500,
    }

    response = api_client.get(reverse("hitas:max-price-list", args=[hc.uuid, a.uuid]) + "?" + urlencode(query))
    assert response.status_code == status.HTTP_200_OK, response.json()

    response_json = response.json()
    assert_created(response_json.pop("created"))

    assert response_json == {
        "max_price": 223558,
        "valid_until": "2022-10-05",
        "index": "construction_price_index",
        "calculations": {
            "construction_price_index": {
                "max_price": 223558,
                "valid_until": "2022-10-05",
                "maximum": True,
                "calculation_variables": {
                    "acquisition_price": 199500,
                    "additional_work_during_construction": 0,
                    "basic_price": 199500,
                    "index_adjustment": 26401,
                    "apartment_improvements": 0,
                    "housing_company_improvements": 157,
                    "debt_free_price": 226058,
                    "debt_free_price_m2": 7535,
                    "apartment_share_of_housing_company_loans": 2500,
                    "completion_date": "2019-11-27",
                    "completion_date_index": 129.29,
                    "calculation_date": "2022-07-05",
                    "calculation_date_index": 146.4,
                },
            },
            "market_price_index": {
                "max_price": 222343,
                "valid_until": "2022-10-05",
                "maximum": False,
                "calculation_variables": {
                    "acquisition_price": 199500,
                    "additional_work_during_construction": 0,
                    "basic_price": 199500,
                    "index_adjustment": 25190,
                    "apartment_improvements": 0,
                    "housing_company_improvements": 153,
                    "debt_free_price": 224843,
                    "debt_free_price_m2": 7495,
                    "apartment_share_of_housing_company_loans": 2500,
                    "completion_date": "2019-11-27",
                    "completion_date_index": 167.9,
                    "calculation_date": "2022-07-05",
                    "calculation_date_index": 189.1,
                },
            },
            "surface_area_price_ceiling": {
                "max_price": 146070,
                "valid_until": "2022-08-31",
                "maximum": False,
            },
        },
        "apartment": {
            "address": {
                "apartment_number": a.apartment_number,
                "city": a.city,
                "floor": a.floor,
                "postal_code": a.postal_code.value,
                "stair": a.stair,
                "street_address": a.street_address,
            },
            "apartment_type": a.apartment_type.value,
            "ownership": [
                {
                    "name": o1.owner.name,
                    "percentage": o1.percentage,
                },
                {
                    "name": o2.owner.name,
                    "percentage": o2.percentage,
                },
            ],
            "rooms": a.rooms,
            "shares": {
                "start": a.share_number_start,
                "end": a.share_number_end,
                "total": 2383,
            },
            "surface_area": a.surface_area,
        },
        "housing_company": {
            "archive_id": hc.id,
            "official_name": hc.official_name,
            "property_manager": {
                "name": hc.property_manager.name,
                "street_address": hc.property_manager.street_address,
            },
        },
    }


@pytest.mark.django_db
def test__api__apartment_max_price__market_price_index(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        debt_free_purchase_price=139706,
        primary_loan_amount=80955,
        additional_work_during_construction=0,
        completion_date=datetime.date(2014, 8, 27),
        surface_area=48.0,
        share_number_start=1,
        share_number_end=142,
    )
    hc: HousingCompany = a.building.real_estate.housing_company
    # Create another apartment with rest of the surface area
    ApartmentFactory.create(building__real_estate__housing_company=hc, surface_area=2655)

    HousingCompanyConstructionPriceImprovementFactory.create(
        housing_company=hc, value=150000, completion_date=datetime.date(2020, 5, 21)
    )
    HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=hc, value=150000, completion_date=datetime.date(2020, 5, 21)
    )
    o1: Ownership = OwnershipFactory.create(apartment=a, percentage=100.0)

    # Create necessary apartment's completion date indices
    ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2014, 8, 1), value=123.5)
    MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2014, 8, 1), value=150.6)

    # Create necessary calculation date indices
    ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2022, 7, 1), value=146.4)
    MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2022, 7, 1), value=189.1)
    SurfaceAreaPriceCeilingFactory.create(month=datetime.date(2022, 7, 1), value=4869)

    # Create necessary improvement's completion date indices
    ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2020, 5, 1), value=129.20)
    MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2020, 5, 1), value=171.0)

    query = {
        "calculation_date": "2022-07-05",
        "apartment_share_housing_company_loans": 2500,
    }

    response = api_client.get(reverse("hitas:max-price-list", args=[hc.uuid, a.uuid]) + "?" + urlencode(query))
    assert response.status_code == status.HTTP_200_OK, response.json()

    response_json = response.json()
    assert_created(response_json.pop("created"))

    assert response_json == {
        "max_price": 275925,
        "valid_until": "2022-10-05",
        "index": "market_price_index",
        "calculations": {
            "construction_price_index": {
                "calculation_variables": {
                    "acquisition_price": 220661,
                    "additional_work_during_construction": 0,
                    "basic_price": 220661,
                    "index_adjustment": 40916,
                    "apartment_improvements": 0,
                    "housing_company_improvements": 1387,
                    "debt_free_price": 262964,
                    "debt_free_price_m2": 5478,
                    "apartment_share_of_housing_company_loans": 2500,
                    "completion_date": "2014-08-27",
                    "completion_date_index": 123.5,
                    "calculation_date": "2022-07-05",
                    "calculation_date_index": 146.4,
                },
                "max_price": 260464,
                "valid_until": "2022-10-05",
                "maximum": False,
            },
            "market_price_index": {
                "calculation_variables": {
                    "acquisition_price": 220661,
                    "additional_work_during_construction": 0,
                    "basic_price": 220661,
                    "index_adjustment": 56411,
                    "apartment_improvements": 0,
                    "housing_company_improvements": 1353,
                    "debt_free_price": 278425,
                    "debt_free_price_m2": 5801,
                    "apartment_share_of_housing_company_loans": 2500,
                    "completion_date": "2014-08-27",
                    "completion_date_index": 150.6,
                    "calculation_date": "2022-07-05",
                    "calculation_date_index": 189.1,
                },
                "max_price": 275925,
                "valid_until": "2022-10-05",
                "maximum": True,
            },
            "surface_area_price_ceiling": {
                "max_price": 233712,
                "valid_until": "2022-08-31",
                "maximum": False,
            },
        },
        "apartment": {
            "shares": {"start": 1, "end": 142, "total": 142},
            "rooms": a.rooms,
            "apartment_type": a.apartment_type.value,
            "surface_area": 48.0,
            "address": {
                "street_address": a.street_address,
                "floor": a.floor,
                "stair": a.stair,
                "apartment_number": a.apartment_number,
                "postal_code": a.postal_code.value,
                "city": a.postal_code.city,
            },
            "ownership": [{"percentage": 100.0, "name": o1.owner.name}],
        },
        "housing_company": {
            "official_name": hc.official_name,
            "archive_id": hc.id,
            "property_manager": {
                "name": hc.property_manager.name,
                "street_address": hc.property_manager.street_address,
            },
        },
    }


@pytest.mark.django_db
def test__api__apartment_max_price__surface_area_price_ceiling(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        debt_free_purchase_price=107753,
        primary_loan_amount=61830,
        additional_work_during_construction=0,
        completion_date=datetime.date(2012, 1, 13),
        surface_area=48.5,
        share_number_start=504,
        share_number_end=601,
    )
    hc: HousingCompany = a.building.real_estate.housing_company
    # Create another apartment with rest of the surface area
    ApartmentFactory.create(building__real_estate__housing_company=hc, surface_area=2655)
    o1: Ownership = OwnershipFactory.create(apartment=a, percentage=100.0)

    # Create necessary apartment's completion date indices
    ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2012, 1, 1), value=115.9)
    MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2012, 1, 1), value=138.1)

    # Create necessary calculation date indices
    ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2022, 9, 1), value=149.1)
    MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2022, 9, 1), value=189.1)
    SurfaceAreaPriceCeilingFactory.create(month=datetime.date(2022, 9, 1), value=4872)

    query = {
        "calculation_date": "2022-09-29",
        "apartment_share_housing_company_loans": 0,
    }

    response = api_client.get(reverse("hitas:max-price-list", args=[hc.uuid, a.uuid]) + "?" + urlencode(query))
    assert response.status_code == status.HTTP_200_OK, response.json()

    response_json = response.json()
    assert_created(response_json.pop("created"))

    assert response_json == {
        "max_price": 236292,
        "valid_until": "2022-11-30",
        "index": "surface_area_price_ceiling",
        "calculations": {
            "construction_price_index": {
                "calculation_variables": {
                    "acquisition_price": 169583,
                    "additional_work_during_construction": 0,
                    "basic_price": 169583,
                    "index_adjustment": 48578,
                    "apartment_improvements": 0,
                    "housing_company_improvements": 0,
                    "debt_free_price": 218161,
                    "debt_free_price_m2": 4498,
                    "apartment_share_of_housing_company_loans": 0,
                    "completion_date": "2012-01-13",
                    "completion_date_index": 115.9,
                    "calculation_date": "2022-09-29",
                    "calculation_date_index": 149.1,
                },
                "max_price": 218161,
                "valid_until": "2022-12-29",
                "maximum": False,
            },
            "market_price_index": {
                "calculation_variables": {
                    "acquisition_price": 169583,
                    "additional_work_during_construction": 0,
                    "basic_price": 169583,
                    "index_adjustment": 62627,
                    "apartment_improvements": 0,
                    "housing_company_improvements": 0,
                    "debt_free_price": 232210,
                    "debt_free_price_m2": 4788,
                    "apartment_share_of_housing_company_loans": 0,
                    "completion_date": "2012-01-13",
                    "completion_date_index": 138.1,
                    "calculation_date": "2022-09-29",
                    "calculation_date_index": 189.1,
                },
                "max_price": 232210,
                "valid_until": "2022-12-29",
                "maximum": False,
            },
            "surface_area_price_ceiling": {
                "max_price": 236292,
                "valid_until": "2022-11-30",
                "maximum": True,
            },
        },
        "apartment": {
            "shares": {"start": 504, "end": 601, "total": 98},
            "rooms": a.rooms,
            "apartment_type": a.apartment_type.value,
            "surface_area": 48.5,
            "address": {
                "street_address": a.street_address,
                "floor": a.floor,
                "stair": a.stair,
                "apartment_number": a.apartment_number,
                "postal_code": a.postal_code.value,
                "city": a.postal_code.city,
            },
            "ownership": [{"percentage": 100.0, "name": o1.owner.name}],
        },
        "housing_company": {
            "official_name": hc.official_name,
            "archive_id": hc.id,
            "property_manager": {
                "name": hc.property_manager.name,
                "street_address": hc.property_manager.street_address,
            },
        },
    }


@pytest.mark.parametrize(
    "query,fields",
    [
        (
            {"calculation_date": "foo"},
            [{"field": "calculation_date", "message": "Field has to be a valid date in format 'yyyy-mm-dd'."}],
        ),
        (
            {"calculation_date": "-1"},
            [{"field": "calculation_date", "message": "Field has to be a valid date in format 'yyyy-mm-dd'."}],
        ),
        (
            {"calculation_date": "2022-7-1"},
            [{"field": "calculation_date", "message": "Field has to be a valid date in format 'yyyy-mm-dd'."}],
        ),
        (
            {"calculation_date": datetime.date.today() + relativedelta.relativedelta(days=1)},
            [{"field": "calculation_date", "message": "Field has to be less than or equal to current date."}],
        ),
        (
            {"apartment_share_housing_company_loans": "foo"},
            [{"field": "apartment_share_housing_company_loans", "message": "A valid number is required."}],
        ),
        (
            {"apartment_share_housing_company_loans": "-1"},
            [
                {
                    "field": "apartment_share_housing_company_loans",
                    "message": "Ensure this value is greater than or equal to 0.",
                }
            ],
        ),
    ],
)
@pytest.mark.django_db
def test__api__apartment_max_price__invalid_params(api_client: HitasAPIClient, query, fields):
    a: Apartment = ApartmentFactory.create()
    hc: HousingCompany = a.building.real_estate.housing_company

    response = api_client.get(
        reverse("hitas:max-price-list", args=[hc.uuid, a.uuid]) + "?" + urlencode(query), openapi_validate_request=False
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": fields,
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.parametrize(
    "missing_index",
    [
        "cpi_completion_date",
        "mpi_completion_date",
        "improvement_cpi",
        "improvement_mpi",
        "cpi_calculation_date",
        "mpi_calculation_date",
        "sapc",
    ],
)
@pytest.mark.django_db
def test__api__apartment_max_price__missing_index(api_client: HitasAPIClient, missing_index: str):
    a: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2014, 8, 27),
    )
    hc: HousingCompany = a.building.real_estate.housing_company
    HousingCompanyConstructionPriceImprovementFactory.create(
        housing_company=hc, value=150000, completion_date=datetime.date(2020, 5, 21)
    )
    HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=hc, value=150000, completion_date=datetime.date(2020, 5, 21)
    )

    # Create necessary apartment's completion date indices
    if missing_index != "cpi_completion_date":
        ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2014, 8, 1), value=129.29)
    if missing_index != "mpi_completion_date":
        MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2014, 8, 1), value=167.9)
    if missing_index != "cpi_calculation_date":
        ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2022, 7, 1), value=146.4)
    if missing_index != "mpi_calculation_date":
        MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2022, 7, 1), value=189.1)
    if missing_index != "sapc":
        SurfaceAreaPriceCeilingFactory.create(month=datetime.date(2022, 7, 1), value=4869)
    if missing_index != "improvement_cpi":
        ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2020, 5, 1), value=129.20)
    if missing_index != "improvement_mpi":
        MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2020, 5, 1), value=171.0)

    query = {
        "calculation_date": "2022-07-05",
    }

    response = api_client.get(reverse("hitas:max-price-list", args=[hc.uuid, a.uuid]) + "?" + urlencode(query))
    assert response.status_code == status.HTTP_409_CONFLICT, response.json()

    assert response.json() == {
        "error": "index_missing",
        "message": "One or more indices required for max price calculation is missing.",
        "reason": "Conflict",
        "status": 409,
    }


def assert_created(created: str):
    created = parse_datetime(created)
    # created timestamp is created 0-10 seconds in the past so effectively "now"
    assert 0 < (timezone.now() - created).total_seconds() < 10
