import datetime

import pytest
from django.urls import reverse
from rest_framework import status

from hitas.models import Apartment, Ownership
from hitas.tests.apis.apartment_max_price.utils import assert_created, assert_id
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
    # Create another apartment with rest of the surface area
    ApartmentFactory.create(building__real_estate__housing_company=a.housing_company, surface_area=4302)

    HousingCompanyConstructionPriceImprovementFactory.create(
        housing_company=a.housing_company, value=150000, completion_date=datetime.date(2020, 5, 21)
    )
    HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=a.housing_company, value=150000, completion_date=datetime.date(2020, 5, 21)
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

    data = {
        "calculation_date": "2022-07-05",
        "apartment_share_of_housing_company_loans": 2500,
        "apartment_share_of_housing_company_loans_date": "2022-07-28",
    }

    response = api_client.post(
        reverse("hitas:maximum-price-list", args=[a.housing_company.uuid.hex, a.uuid.hex]), data=data, format="json"
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    response_json = response.json()
    mpc_id = assert_id(response_json.pop("id"))
    assert_created(response_json.pop("created_at"))

    expected_response = {
        "confirmed_at": None,
        "maximum_price": 223558,
        "calculation_date": "2022-07-05",
        "valid_until": "2022-10-05",
        "index": "construction_price_index",
        "calculations": {
            "construction_price_index": {
                "maximum_price": 223558,
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
                    "apartment_share_of_housing_company_loans_date": "2022-07-28",
                    "completion_date": "2019-11-27",
                    "completion_date_index": 129.29,
                    "calculation_date": "2022-07-05",
                    "calculation_date_index": 146.4,
                },
            },
            "market_price_index": {
                "maximum_price": 222343,
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
                    "apartment_share_of_housing_company_loans_date": "2022-07-28",
                    "completion_date": "2019-11-27",
                    "completion_date_index": 167.9,
                    "calculation_date": "2022-07-05",
                    "calculation_date_index": 189.1,
                },
            },
            "surface_area_price_ceiling": {
                "maximum_price": 146070,
                "valid_until": "2022-08-31",
                "maximum": False,
                "calculation_variables": {
                    "calculation_date": "2022-07-05",
                    "calculation_date_value": 4869.0,
                    "surface_area": 30.0,
                },
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
            "type": a.apartment_type.value,
            "ownerships": [
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
            "surface_area": 30.0,
        },
        "housing_company": {
            "archive_id": a.housing_company.id,
            "official_name": a.housing_company.official_name,
            "property_manager": {
                "name": a.housing_company.property_manager.name,
                "street_address": a.housing_company.property_manager.street_address,
            },
        },
    }
    assert expected_response == response_json

    response = api_client.get(
        reverse("hitas:maximum-price-detail", args=[a.housing_company.uuid.hex, a.uuid.hex, mpc_id])
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    response_json = response.json()
    assert_id(response_json.pop("id"))
    assert_created(response_json.pop("created_at"))
    assert expected_response == response_json


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
    # Create another apartment with rest of the surface area
    ApartmentFactory.create(building__real_estate__housing_company=a.housing_company, surface_area=2655)

    HousingCompanyConstructionPriceImprovementFactory.create(
        housing_company=a.housing_company, value=150000, completion_date=datetime.date(2020, 5, 21)
    )
    HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=a.housing_company, value=150000, completion_date=datetime.date(2020, 5, 21)
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

    data = {
        "calculation_date": "2022-07-05",
        "apartment_share_of_housing_company_loans": 2500,
        "apartment_share_of_housing_company_loans_date": "2022-07-28",
    }

    response = api_client.post(
        reverse("hitas:maximum-price-list", args=[a.housing_company.uuid.hex, a.uuid.hex]), data=data, format="json"
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    response_json = response.json()
    assert_id(response_json.pop("id"))
    assert_created(response_json.pop("created_at"))

    assert response_json == {
        "confirmed_at": None,
        "calculation_date": "2022-07-05",
        "maximum_price": 275925,
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
                    "apartment_share_of_housing_company_loans_date": "2022-07-28",
                    "completion_date": "2014-08-27",
                    "completion_date_index": 123.5,
                    "calculation_date": "2022-07-05",
                    "calculation_date_index": 146.4,
                },
                "maximum_price": 260464,
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
                    "apartment_share_of_housing_company_loans_date": "2022-07-28",
                    "completion_date": "2014-08-27",
                    "completion_date_index": 150.6,
                    "calculation_date": "2022-07-05",
                    "calculation_date_index": 189.1,
                },
                "maximum_price": 275925,
                "valid_until": "2022-10-05",
                "maximum": True,
            },
            "surface_area_price_ceiling": {
                "maximum_price": 233712,
                "valid_until": "2022-08-31",
                "maximum": False,
                "calculation_variables": {
                    "calculation_date": "2022-07-05",
                    "calculation_date_value": 4869.0,
                    "surface_area": 48.0,
                },
            },
        },
        "apartment": {
            "shares": {"start": 1, "end": 142, "total": 142},
            "rooms": a.rooms,
            "type": a.apartment_type.value,
            "surface_area": 48.0,
            "address": {
                "street_address": a.street_address,
                "floor": a.floor,
                "stair": a.stair,
                "apartment_number": a.apartment_number,
                "postal_code": a.postal_code.value,
                "city": a.postal_code.city,
            },
            "ownerships": [{"percentage": 100.0, "name": o1.owner.name}],
        },
        "housing_company": {
            "official_name": a.housing_company.official_name,
            "archive_id": a.housing_company.id,
            "property_manager": {
                "name": a.housing_company.property_manager.name,
                "street_address": a.housing_company.property_manager.street_address,
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
    # Create another apartment with rest of the surface area
    ApartmentFactory.create(building__real_estate__housing_company=a.housing_company, surface_area=2655)
    o1: Ownership = OwnershipFactory.create(apartment=a, percentage=100.0)

    # Create necessary apartment's completion date indices
    ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2012, 1, 1), value=115.9)
    MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2012, 1, 1), value=138.1)

    # Create necessary calculation date indices
    ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2022, 9, 1), value=149.1)
    MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2022, 9, 1), value=189.1)
    SurfaceAreaPriceCeilingFactory.create(month=datetime.date(2022, 9, 1), value=4872)

    data = {
        "calculation_date": "2022-09-29",
        "apartment_share_of_housing_company_loans": 0,
        "apartment_share_of_housing_company_loans_date": "2022-10-01",
    }

    response = api_client.post(
        reverse("hitas:maximum-price-list", args=[a.housing_company.uuid.hex, a.uuid.hex]), data=data, format="json"
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    response_json = response.json()
    assert_id(response_json.pop("id"))
    assert_created(response_json.pop("created_at"))

    assert response_json == {
        "confirmed_at": None,
        "calculation_date": "2022-09-29",
        "maximum_price": 236292,
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
                    "apartment_share_of_housing_company_loans_date": "2022-10-01",
                    "completion_date": "2012-01-13",
                    "completion_date_index": 115.9,
                    "calculation_date": "2022-09-29",
                    "calculation_date_index": 149.1,
                },
                "maximum_price": 218161,
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
                    "apartment_share_of_housing_company_loans_date": "2022-10-01",
                    "completion_date": "2012-01-13",
                    "completion_date_index": 138.1,
                    "calculation_date": "2022-09-29",
                    "calculation_date_index": 189.1,
                },
                "maximum_price": 232210,
                "valid_until": "2022-12-29",
                "maximum": False,
            },
            "surface_area_price_ceiling": {
                "maximum_price": 236292,
                "valid_until": "2022-11-30",
                "maximum": True,
                "calculation_variables": {
                    "calculation_date": "2022-09-29",
                    "calculation_date_value": 4872.0,
                    "surface_area": 48.5,
                },
            },
        },
        "apartment": {
            "shares": {"start": 504, "end": 601, "total": 98},
            "rooms": a.rooms,
            "type": a.apartment_type.value,
            "surface_area": 48.5,
            "address": {
                "street_address": a.street_address,
                "floor": a.floor,
                "stair": a.stair,
                "apartment_number": a.apartment_number,
                "postal_code": a.postal_code.value,
                "city": a.postal_code.city,
            },
            "ownerships": [{"percentage": 100.0, "name": o1.owner.name}],
        },
        "housing_company": {
            "official_name": a.housing_company.official_name,
            "archive_id": a.housing_company.id,
            "property_manager": {
                "name": a.housing_company.property_manager.name,
                "street_address": a.housing_company.property_manager.street_address,
            },
        },
    }
