import datetime
from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from hitas.models import (
    Apartment,
    ApartmentConstructionPriceImprovement,
    HousingCompanyConstructionPriceImprovement,
    HousingCompanyMarketPriceImprovement,
    Ownership,
)
from hitas.tests.apis.apartment_max_price.utils import assert_created, assert_id
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import (
    ApartmentConstructionPriceImprovementFactory,
    ApartmentFactory,
    HousingCompanyConstructionPriceImprovementFactory,
    HousingCompanyMarketPriceImprovementFactory,
    OldHitasFinancingMethodFactory,
    OwnershipFactory,
)
from hitas.tests.factories.indices import (
    ConstructionPriceIndex2005Equal100Factory,
    ConstructionPriceIndexFactory,
    MarketPriceIndex2005Equal100Factory,
    MarketPriceIndexFactory,
    SurfaceAreaPriceCeilingFactory,
)


@pytest.mark.django_db
def test__api__apartment_max_price__construction_price_index__2011_onwards(api_client: HitasAPIClient):
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

    cpi_improvement: HousingCompanyConstructionPriceImprovement = (
        HousingCompanyConstructionPriceImprovementFactory.create(
            housing_company=a.housing_company, value=150000, completion_date=datetime.date(2020, 5, 21)
        )
    )
    mpi_improvement: HousingCompanyMarketPriceImprovement = HousingCompanyMarketPriceImprovementFactory.create(
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
        "additional_info": "Example",
    }

    response = api_client.post(
        reverse("hitas:maximum-price-list", args=[a.housing_company.uuid.hex, a.uuid.hex]),
        data=data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    response_json = response.json()
    mpc_id = assert_id(response_json.pop("id"))
    assert_created(response_json.pop("created_at"))

    expected_response = {
        "confirmed_at": None,
        "maximum_price": 223558.72,
        "calculation_date": "2022-07-05",
        "valid_until": "2022-10-05",
        "index": "construction_price_index",
        "new_hitas": True,
        "calculations": {
            "construction_price_index": {
                "maximum_price": 223558.72,
                "valid_until": "2022-10-05",
                "maximum": True,
                "calculation_variables": {
                    "acquisition_price": 199500.0,
                    "additional_work_during_construction": 0.0,
                    "basic_price": 199500.0,
                    "index_adjustment": 26401.46,
                    "housing_company_improvements": {
                        "items": [
                            {
                                "name": cpi_improvement.name,
                                "value": 150_000.0,
                                "completion_date": "2020-05-21",
                                "value_added": 20040.0,
                                "value_for_housing_company": 22707.86,
                                "value_for_apartment": 157.26,
                            }
                        ],
                        "summary": {
                            "value": 150_000.0,
                            "value_added": 20040.0,
                            "excess": {
                                "surface_area": 4332.0,
                                "value_per_square_meter": 30.0,
                                "total": 129960.0,
                            },
                            "value_for_housing_company": 22707.86,
                            "value_for_apartment": 157.26,
                        },
                    },
                    "debt_free_price": 226058.72,
                    "debt_free_price_m2": 7535.29,
                    "apartment_share_of_housing_company_loans": 2500,
                    "apartment_share_of_housing_company_loans_date": "2022-07-28",
                    "completion_date": "2019-11-27",
                    "completion_date_index": 129.29,
                    "calculation_date": "2022-07-05",
                    "calculation_date_index": 146.4,
                },
            },
            "market_price_index": {
                "maximum_price": 222343.46,
                "valid_until": "2022-10-05",
                "maximum": False,
                "calculation_variables": {
                    "acquisition_price": 199500.0,
                    "additional_work_during_construction": 0.0,
                    "basic_price": 199500.0,
                    "index_adjustment": 25189.99,
                    "housing_company_improvements": {
                        "items": [
                            {
                                "name": mpi_improvement.name,
                                "value": 150_000.0,
                                "completion_date": "2020-05-21",
                                "value_added": 20040.0,
                                "value_for_housing_company": 22161.19,
                                "value_for_apartment": 153.47,
                            }
                        ],
                        "summary": {
                            "value": 150_000.0,
                            "value_added": 20040.0,
                            "excess": {
                                "surface_area": 4332.0,
                                "value_per_square_meter": 30.0,
                                "total": 129960.0,
                            },
                            "value_for_housing_company": 22161.19,
                            "value_for_apartment": 153.47,
                        },
                    },
                    "debt_free_price": 224843.46,
                    "debt_free_price_m2": 7494.78,
                    "apartment_share_of_housing_company_loans": 2500,
                    "apartment_share_of_housing_company_loans_date": "2022-07-28",
                    "completion_date": "2019-11-27",
                    "completion_date_index": 167.9,
                    "calculation_date": "2022-07-05",
                    "calculation_date_index": 189.1,
                },
            },
            "surface_area_price_ceiling": {
                "maximum_price": 143570.0,
                "valid_until": "2022-08-31",
                "maximum": False,
                "calculation_variables": {
                    "calculation_date": "2022-07-05",
                    "calculation_date_value": 4869.0,
                    "debt_free_price": 146070.0,
                    "surface_area": 30.0,
                    "apartment_share_of_housing_company_loans": 2500,
                    "apartment_share_of_housing_company_loans_date": "2022-07-28",
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
        "additional_info": "Example",
    }
    assert expected_response == response_json

    response = api_client.get(
        reverse("hitas:maximum-price-detail", args=[a.housing_company.uuid.hex, a.uuid.hex, mpc_id]),
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    response_json = response.json()
    assert_id(response_json.pop("id"))
    assert_created(response_json.pop("created_at"))
    assert expected_response == response_json


@pytest.mark.django_db
def test__api__apartment_max_price__market_price_index__2011_onwards(api_client: HitasAPIClient):
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

    cpi_improvement: HousingCompanyConstructionPriceImprovement = (
        HousingCompanyConstructionPriceImprovementFactory.create(
            housing_company=a.housing_company, value=150000, completion_date=datetime.date(2020, 5, 21)
        )
    )
    mpi_improvement: HousingCompanyMarketPriceImprovement = HousingCompanyMarketPriceImprovementFactory.create(
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
        "additional_info": "Example",
    }

    response = api_client.post(
        reverse("hitas:maximum-price-list", args=[a.housing_company.uuid.hex, a.uuid.hex]),
        data=data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    response_json = response.json()
    assert_id(response_json.pop("id"))
    assert_created(response_json.pop("created_at"))

    assert response_json == {
        "confirmed_at": None,
        "calculation_date": "2022-07-05",
        "maximum_price": 275924.91,
        "valid_until": "2022-10-05",
        "index": "market_price_index",
        "new_hitas": True,
        "calculations": {
            "construction_price_index": {
                "calculation_variables": {
                    "acquisition_price": 220661.0,
                    "additional_work_during_construction": 0.0,
                    "basic_price": 220661.0,
                    "index_adjustment": 40916.09,
                    "housing_company_improvements": {
                        "items": [
                            {
                                "name": cpi_improvement.name,
                                "value": 150_000.0,
                                "completion_date": "2020-05-21",
                                "value_added": 68910.0,
                                "value_for_housing_company": 78083.78,
                                "value_for_apartment": 1386.62,
                            }
                        ],
                        "summary": {
                            "value": 150_000.0,
                            "value_added": 68910.0,
                            "excess": {
                                "surface_area": 2703.0,
                                "value_per_square_meter": 30.0,
                                "total": 81090.0,
                            },
                            "value_for_housing_company": 78083.78,
                            "value_for_apartment": 1386.62,
                        },
                    },
                    "debt_free_price": 262963.7,
                    "debt_free_price_m2": 5478.41,
                    "apartment_share_of_housing_company_loans": 2500,
                    "apartment_share_of_housing_company_loans_date": "2022-07-28",
                    "completion_date": "2014-08-27",
                    "completion_date_index": 123.5,
                    "calculation_date": "2022-07-05",
                    "calculation_date_index": 146.4,
                },
                "maximum_price": 260463.7,
                "valid_until": "2022-10-05",
                "maximum": False,
            },
            "market_price_index": {
                "calculation_variables": {
                    "acquisition_price": 220661.0,
                    "additional_work_during_construction": 0.0,
                    "basic_price": 220661.0,
                    "index_adjustment": 56410.68,
                    "housing_company_improvements": {
                        "items": [
                            {
                                "name": mpi_improvement.name,
                                "value": 150_000.0,
                                "completion_date": "2020-05-21",
                                "value_added": 68910.0,
                                "value_for_housing_company": 76203.98,
                                "value_for_apartment": 1353.23,
                            }
                        ],
                        "summary": {
                            "value": 150_000.0,
                            "value_added": 68910.0,
                            "excess": {
                                "surface_area": 2703.0,
                                "value_per_square_meter": 30.0,
                                "total": 81090.0,
                            },
                            "value_for_housing_company": 76203.98,
                            "value_for_apartment": 1353.23,
                        },
                    },
                    "debt_free_price": 278424.91,
                    "debt_free_price_m2": 5800.52,
                    "apartment_share_of_housing_company_loans": 2500,
                    "apartment_share_of_housing_company_loans_date": "2022-07-28",
                    "completion_date": "2014-08-27",
                    "completion_date_index": 150.6,
                    "calculation_date": "2022-07-05",
                    "calculation_date_index": 189.1,
                },
                "maximum_price": 275924.91,
                "valid_until": "2022-10-05",
                "maximum": True,
            },
            "surface_area_price_ceiling": {
                "maximum_price": 231_212.0,
                "valid_until": "2022-08-31",
                "maximum": False,
                "calculation_variables": {
                    "calculation_date": "2022-07-05",
                    "calculation_date_value": 4869.0,
                    "debt_free_price": 233712,
                    "surface_area": 48.0,
                    "apartment_share_of_housing_company_loans": 2500,
                    "apartment_share_of_housing_company_loans_date": "2022-07-28",
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
        "additional_info": "Example",
    }


@pytest.mark.django_db
def test__api__apartment_max_price__market_price_index__pre_2011(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        debt_free_purchase_price=104693.0,
        primary_loan_amount=18480.0,
        interest_during_construction_6=3455.0,
        interest_during_construction_14=4000.0,
        additional_work_during_construction=4307.0,
        completion_date=datetime.date(2003, 5, 9),
        surface_area=54.5,
        share_number_start=1729,
        share_number_end=1888,
        building__real_estate__housing_company__financing_method=OldHitasFinancingMethodFactory(),
    )
    # Create another apartment with rest of the surface area
    ApartmentFactory.create(
        building__real_estate__housing_company=a.housing_company,
        surface_area=3336,
        debt_free_purchase_price=0.0,
        primary_loan_amount=0.0,
    )

    mpi_hc_improvement: HousingCompanyMarketPriceImprovement = HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=a.housing_company, value=0, completion_date=datetime.date(2003, 5, 1)
    )
    mpi_hc_improvement2: HousingCompanyMarketPriceImprovement = HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=a.housing_company, value=1587, completion_date=datetime.date(2004, 10, 1)
    )
    o1: Ownership = OwnershipFactory.create(apartment=a, percentage=50.0)
    o2: Ownership = OwnershipFactory.create(apartment=a, percentage=50.0)

    # Create necessary apartment's completion date indices
    ConstructionPriceIndexFactory.create(month=datetime.date(2003, 5, 1), value=244.9)
    MarketPriceIndexFactory.create(month=datetime.date(2003, 5, 1), value=263.60)

    # Create necessary calculation date indices
    ConstructionPriceIndexFactory.create(month=datetime.date(2022, 9, 1), value=364.40)
    MarketPriceIndexFactory.create(month=datetime.date(2022, 9, 1), value=583.3)
    SurfaceAreaPriceCeilingFactory.create(month=datetime.date(2022, 9, 1), value=4872)

    # Create necessary improvement's completion date indices
    ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2004, 10, 1), value=238.5)
    MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2004, 10, 1), value=291.1)

    data = {
        "calculation_date": "2022-09-07",
        "apartment_share_of_housing_company_loans": 0,
        "apartment_share_of_housing_company_loans_date": "2022-09-05",
        "additional_info": "Example",
    }

    response = api_client.post(
        reverse("hitas:maximum-price-list", args=[a.housing_company.uuid.hex, a.uuid.hex]),
        data=data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    response_json = response.json()
    assert_id(response_json.pop("id"))
    assert_created(response_json.pop("created_at"))

    assert response_json == {
        "confirmed_at": None,
        "calculation_date": "2022-09-07",
        "maximum_price": 289735.91,
        "valid_until": "2022-12-07",
        "index": "market_price_index",
        "new_hitas": False,
        "calculations": {
            "construction_price_index": {
                "calculation_variables": {
                    "housing_company_acquisition_price": 170_886.35,
                    "housing_company_assets": 170_886.35,
                    "apartment_share_of_housing_company_assets": 170886.35,
                    "interest_during_construction": 4000.0,
                    "interest_during_construction_percentage": 14,
                    "apartment_improvements": {
                        "items": [
                            {
                                "name": "Rakennusaikaiset muutos- ja lisätyöt",
                                "value": 4307.0,
                                "calculation_date_index": 364.4,
                                "completion_date": "2003-05-09",
                                "completion_date_index": 244.9,
                                "index_adjusted": 6408.62,
                                "depreciation": {
                                    "amount": 0.0,
                                    "percentage": 0.0,
                                    "time": {
                                        "years": 0,
                                        "months": 0,
                                    },
                                },
                                "value_for_apartment": 6408.62,
                            }
                        ],
                        "summary": {
                            "value": 4307.0,
                            "index_adjusted": 6408.62,
                            "depreciation": 0.0,
                            "value_for_apartment": 6408.62,
                        },
                    },
                    "housing_company_improvements": {
                        "items": [],
                        "summary": {
                            "value": 0.0,
                            "value_for_apartment": 0.0,
                        },
                    },
                    "debt_free_price": 181294.97,
                    "debt_free_price_m2": 3326.51,
                    "apartment_share_of_housing_company_loans": 0,
                    "apartment_share_of_housing_company_loans_date": "2022-09-05",
                    "completion_date": "2003-05-09",
                    "completion_date_index": 244.9,
                    "calculation_date": "2022-09-07",
                    "calculation_date_index": 364.4,
                },
                "maximum_price": 181294.97,
                "valid_until": "2022-12-07",
                "maximum": False,
            },
            "market_price_index": {
                "calculation_variables": {
                    "acquisition_price": 123173.0,
                    "interest_during_construction": 3455.0,
                    "interest_during_construction_percentage": 6,
                    "basic_price": 126628.0,
                    "index_adjustment": 153577.28,
                    "apartment_improvements": {
                        "items": [
                            {
                                "name": "Rakennusaikaiset muutos- ja lisätyöt",
                                "value": 4307.0,
                                "completion_date": "2003-05-09",
                                "value_without_excess": 4307.0,
                                "depreciation": {
                                    "amount": 0.0,
                                    "time": {
                                        "years": 0,
                                        "months": 0,
                                    },
                                },
                                "accepted_value": 9530.63,
                            }
                        ],
                        "summary": {
                            "value": 4307.0,
                            "value_without_excess": 4307.0,
                            "depreciation": 0.0,
                            "excess": {
                                "surface_area": 54.5,
                                "total": 5450.0,
                                "value_per_square_meter": 100.0,
                            },
                            "accepted_value": 9530.63,
                        },
                    },
                    "housing_company_improvements": {
                        "items": [
                            {
                                "name": mpi_hc_improvement.name,
                                "value": 0.0,
                                "completion_date": "2003-05-01",
                                "value_without_excess": 0.0,
                                "depreciation": {
                                    "amount": 0.0,
                                    "time": {
                                        "years": 0,
                                        "months": 0,
                                    },
                                },
                                "accepted_value_for_housing_company": 0.0,
                                "accepted_value": 0.0,
                            },
                            {
                                "name": mpi_hc_improvement2.name,
                                "value": 1587.0,
                                "completion_date": "2004-10-01",
                                "value_without_excess": 0.0,
                                "depreciation": {
                                    "amount": 0.0,
                                    "time": {
                                        "years": 0,
                                        "months": 0,
                                    },
                                },
                                "accepted_value_for_housing_company": 0.0,
                                "accepted_value": 0.0,
                            },
                        ],
                        "summary": {
                            "value": 1587.0,
                            "value_without_excess": 0.0,
                            "excess": {
                                "surface_area": 3390.5,
                                "value_per_square_meter_before_2010": 150.0,
                                "value_per_square_meter_after_2010": None,
                                "total_before_2010": 508575.0,
                                "total_after_2010": None,
                            },
                            "depreciation": 0.0,
                            "accepted_value_for_housing_company": 0.0,
                            "accepted_value": 0.0,
                        },
                    },
                    "debt_free_price": 289735.91,
                    "debt_free_price_m2": 5316.26,
                    "apartment_share_of_housing_company_loans": 0,
                    "apartment_share_of_housing_company_loans_date": "2022-09-05",
                    "completion_date": "2003-05-09",
                    "completion_date_index": 263.6,
                    "calculation_date": "2022-09-07",
                    "calculation_date_index": 583.3,
                },
                "maximum_price": 289735.91,
                "valid_until": "2022-12-07",
                "maximum": True,
            },
            "surface_area_price_ceiling": {
                "maximum_price": 265524.0,
                "valid_until": "2022-11-30",
                "maximum": False,
                "calculation_variables": {
                    "calculation_date": "2022-09-07",
                    "calculation_date_value": 4872.0,
                    "debt_free_price": 265524.0,
                    "surface_area": 54.5,
                    "apartment_share_of_housing_company_loans": 0,
                    "apartment_share_of_housing_company_loans_date": "2022-09-05",
                },
            },
        },
        "apartment": {
            "shares": {"start": 1729, "end": 1888, "total": 160},
            "rooms": a.rooms,
            "type": a.apartment_type.value,
            "surface_area": 54.5,
            "address": {
                "street_address": a.street_address,
                "floor": a.floor,
                "stair": a.stair,
                "apartment_number": a.apartment_number,
                "postal_code": a.postal_code.value,
                "city": a.postal_code.city,
            },
            "ownerships": [
                {"percentage": 50.0, "name": o1.owner.name},
                {"percentage": 50.0, "name": o2.owner.name},
            ],
        },
        "housing_company": {
            "official_name": a.housing_company.official_name,
            "archive_id": a.housing_company.id,
            "property_manager": {
                "name": a.housing_company.property_manager.name,
                "street_address": a.housing_company.property_manager.street_address,
            },
        },
        "additional_info": "Example",
    }


@pytest.mark.django_db
def test__api__apartment_max_price__construction_price_index__pre_2011(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        debt_free_purchase_price=52738.0,
        primary_loan_amount=123192.0,
        interest_during_construction_6=2703.0,
        interest_during_construction_14=3233.0,
        additional_work_during_construction=2500.0,
        completion_date=datetime.date(2012, 6, 28),
        surface_area=45.5,
        share_number_start=19717,
        share_number_end=20188,
        building__real_estate__housing_company__financing_method=OldHitasFinancingMethodFactory(),
    )
    # Create another apartment with rest of the surface area
    ApartmentFactory.create(
        building__real_estate__housing_company=a.housing_company,
        completion_date=datetime.date(2010, 1, 1),
        debt_free_purchase_price=0.0,
        primary_loan_amount=0.0,
        surface_area=10915.0,
    )
    # Create another apartment with same completion date and rest of the acquisition price
    ApartmentFactory.create(
        building__real_estate__housing_company=a.housing_company,
        completion_date=a.completion_date,
        surface_area=0,
        debt_free_purchase_price=16551639.5,
        primary_loan_amount=0.5,
    )
    # Create another apartment with different completion date and rest of the acquisition price
    ApartmentFactory.create(
        building__real_estate__housing_company=a.housing_company,
        completion_date=datetime.date(2011, 12, 30),
        surface_area=0.0,
        debt_free_purchase_price=20545029.0,
        primary_loan_amount=1.0,
    )

    cpi_hc_improvement: HousingCompanyConstructionPriceImprovement = (
        HousingCompanyConstructionPriceImprovementFactory.create(
            housing_company=a.housing_company, value=1_000_000, completion_date=datetime.date(2018, 2, 1)
        )
    )
    cpi_improvement: ApartmentConstructionPriceImprovement = ApartmentConstructionPriceImprovementFactory.create(
        apartment=a,
        value=15_000,
        completion_date=datetime.date(2020, 6, 1),
        depreciation_percentage=Decimal("10.0"),
    )

    o1: Ownership = OwnershipFactory.create(apartment=a, percentage=100.0)

    # Create necessary apartment's completion date indices
    ConstructionPriceIndexFactory.create(month=datetime.date(2012, 6, 1), value=296.10)
    MarketPriceIndexFactory.create(month=datetime.date(2012, 6, 1), value=263.60)

    # Create necessary calculation date indices
    ConstructionPriceIndexFactory.create(month=datetime.date(2022, 11, 1), value=364.60)
    MarketPriceIndexFactory.create(month=datetime.date(2022, 11, 1), value=567.1)
    SurfaceAreaPriceCeilingFactory.create(month=datetime.date(2022, 11, 1), value=4733)

    # Create necessary improvement's completion date indices
    ConstructionPriceIndexFactory.create(month=datetime.date(2018, 2, 1), value=238.5)
    MarketPriceIndexFactory.create(month=datetime.date(2018, 2, 1), value=490.0)
    ConstructionPriceIndexFactory.create(month=datetime.date(2020, 6, 1), value=316.33)
    MarketPriceIndexFactory.create(month=datetime.date(2020, 6, 1), value=527.4)

    data = {
        "calculation_date": "2022-11-21",
        "apartment_share_of_housing_company_loans": 3000,
        "apartment_share_of_housing_company_loans_date": "2022-11-20",
        "additional_info": "Example",
    }

    response = api_client.post(
        reverse("hitas:maximum-price-list", args=[a.housing_company.uuid.hex, a.uuid.hex]),
        data=data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    response_json = response.json()
    assert_id(response_json.pop("id"))
    assert_created(response_json.pop("created_at"))

    assert response_json == {
        "confirmed_at": None,
        "calculation_date": "2022-11-21",
        "maximum_price": 386683.32,
        "valid_until": "2023-02-21",
        "index": "market_price_index",
        "new_hitas": False,
        "calculations": {
            "construction_price_index": {
                "calculation_variables": {
                    "housing_company_acquisition_price": 20_374_887.55,
                    "housing_company_assets": 20_823_677.55,
                    "apartment_share_of_housing_company_assets": 219010.27,
                    "interest_during_construction": 2703.0,
                    "interest_during_construction_percentage": 6,
                    "apartment_improvements": {
                        "items": [
                            {
                                "name": cpi_improvement.name,
                                "value": 15_000.0,
                                "completion_date": "2020-06-01",
                                "calculation_date_index": 364.6,
                                "completion_date_index": 316.33,
                                "index_adjusted": 17_288.91,
                                "depreciation": {
                                    "amount": 4178.15,
                                    "percentage": 10.0,
                                    "time": {
                                        "years": 2,
                                        "months": 5,
                                    },
                                },
                                "value_for_apartment": 13_110.75,
                            },
                            {
                                "name": "Rakennusaikaiset muutos- ja lisätyöt",
                                "value": 2500.00,
                                "calculation_date_index": 364.6,
                                "completion_date": "2012-06-28",
                                "completion_date_index": 296.1,
                                "index_adjusted": 3078.35,
                                "depreciation": {
                                    "amount": 0.0,
                                    "percentage": 0.0,
                                    "time": {
                                        "years": 0,
                                        "months": 0,
                                    },
                                },
                                "value_for_apartment": 3078.35,
                            },
                        ],
                        "summary": {
                            "value": 17500.0,
                            "index_adjusted": 20367.26,
                            "depreciation": 4178.15,
                            "value_for_apartment": 16189.11,
                        },
                    },
                    "housing_company_improvements": {
                        "items": [
                            {
                                "name": cpi_hc_improvement.name,
                                "value": 1_000_000.00,
                                "value_for_apartment": 448_790.0,
                                "completion_date": "2018-02-01",
                            },
                        ],
                        "summary": {
                            "value": 1_000_000.00,
                            "value_for_apartment": 448_790.0,
                        },
                    },
                    "debt_free_price": 237902.37,
                    "debt_free_price_m2": 5228.62,
                    "apartment_share_of_housing_company_loans": 3000,
                    "apartment_share_of_housing_company_loans_date": "2022-11-20",
                    "completion_date": "2012-06-28",
                    "completion_date_index": 296.10,
                    "calculation_date": "2022-11-21",
                    "calculation_date_index": 364.6,
                },
                "maximum_price": 234902.37,
                "valid_until": "2023-02-21",
                "maximum": False,
            },
            "market_price_index": {
                "calculation_variables": {
                    "acquisition_price": 175_930.0,
                    "interest_during_construction": 2703.0,
                    "interest_during_construction_percentage": 6,
                    "basic_price": 178_633.0,
                    "index_adjustment": 205_671.91,
                    "apartment_improvements": {
                        "items": [
                            {
                                "name": "Rakennusaikaiset muutos- ja lisätyöt",
                                "value": 2500.00,
                                "completion_date": "2012-06-28",
                                "value_without_excess": 2500.0,
                                "depreciation": {
                                    "amount": 0.0,
                                    "time": {
                                        "years": 0,
                                        "months": 0,
                                    },
                                },
                                "accepted_value": 5378.41,
                            }
                        ],
                        "summary": {
                            "value": 2500.0,
                            "value_without_excess": 2500.0,
                            "excess": {
                                "surface_area": 45.5,
                                "total": 4550.0,
                                "value_per_square_meter": 100.0,
                            },
                            "depreciation": 0.0,
                            "accepted_value": 5378.41,
                        },
                    },
                    "housing_company_improvements": {
                        "items": [],
                        "summary": {
                            "value": 0.0,
                            "value_without_excess": 0.0,
                            "excess": {
                                "surface_area": 10960.5,
                                "value_per_square_meter_before_2010": None,
                                "value_per_square_meter_after_2010": None,
                                "total_before_2010": None,
                                "total_after_2010": None,
                            },
                            "depreciation": 0.0,
                            "accepted_value_for_housing_company": 0.0,
                            "accepted_value": 0.0,
                        },
                    },
                    "debt_free_price": 389683.32,
                    "debt_free_price_m2": 8564.47,
                    "apartment_share_of_housing_company_loans": 3000,
                    "apartment_share_of_housing_company_loans_date": "2022-11-20",
                    "completion_date": "2012-06-28",
                    "completion_date_index": 263.6,
                    "calculation_date": "2022-11-21",
                    "calculation_date_index": 567.1,
                },
                "maximum_price": 386683.32,
                "valid_until": "2023-02-21",
                "maximum": True,
            },
            "surface_area_price_ceiling": {
                "maximum_price": 212352.0,
                "valid_until": "2023-02-28",
                "maximum": False,
                "calculation_variables": {
                    "calculation_date": "2022-11-21",
                    "calculation_date_value": 4733.0,
                    "debt_free_price": 215352.0,
                    "surface_area": 45.5,
                    "apartment_share_of_housing_company_loans": 3000,
                    "apartment_share_of_housing_company_loans_date": "2022-11-20",
                },
            },
        },
        "apartment": {
            "shares": {"start": 19717, "end": 20188, "total": 472},
            "rooms": a.rooms,
            "type": a.apartment_type.value,
            "surface_area": 45.5,
            "address": {
                "street_address": a.street_address,
                "floor": a.floor,
                "stair": a.stair,
                "apartment_number": a.apartment_number,
                "postal_code": a.postal_code.value,
                "city": a.postal_code.city,
            },
            "ownerships": [
                {"percentage": 100.0, "name": o1.owner.name},
            ],
        },
        "housing_company": {
            "official_name": a.housing_company.official_name,
            "archive_id": a.housing_company.id,
            "property_manager": {
                "name": a.housing_company.property_manager.name,
                "street_address": a.housing_company.property_manager.street_address,
            },
        },
        "additional_info": "Example",
    }


@pytest.mark.parametrize("interest_during_construction", [0, None])
@pytest.mark.django_db
def test__api__apartment_max_price__pre_2011__no_improvements(api_client: HitasAPIClient, interest_during_construction):
    a: Apartment = ApartmentFactory.create(
        debt_free_purchase_price=100000,
        primary_loan_amount=0,
        interest_during_construction_6=interest_during_construction,
        interest_during_construction_14=interest_during_construction,
        additional_work_during_construction=0,
        completion_date=datetime.date(2003, 5, 9),
        surface_area=10,
        share_number_start=100,
        share_number_end=200,
        building__real_estate__housing_company__financing_method=OldHitasFinancingMethodFactory(),
    )
    # Create necessary apartment's completion date indices
    ConstructionPriceIndexFactory.create(month=datetime.date(2003, 5, 1), value=100)
    MarketPriceIndexFactory.create(month=datetime.date(2003, 5, 1), value=100)

    # Create necessary calculation date indices
    ConstructionPriceIndexFactory.create(month=datetime.date(2003, 6, 1), value=200)
    MarketPriceIndexFactory.create(month=datetime.date(2003, 6, 1), value=200)
    SurfaceAreaPriceCeilingFactory.create(month=datetime.date(2003, 6, 1), value=200)

    data = {
        "calculation_date": "2003-06-01",
        "apartment_share_of_housing_company_loans": 0,
        "apartment_share_of_housing_company_loans_date": "2003-06-01",
        "additional_info": "Example",
    }

    response = api_client.post(
        reverse("hitas:maximum-price-list", args=[a.housing_company.uuid.hex, a.uuid.hex]),
        data=data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    response_json = response.json()
    assert_id(response_json.pop("id"))
    assert_created(response_json.pop("created_at"))

    assert response_json["calculations"]["construction_price_index"] == {
        "calculation_variables": {
            "housing_company_acquisition_price": 200000.0,
            "housing_company_assets": 200000.0,
            "apartment_share_of_housing_company_assets": 200000.0,
            "interest_during_construction": 0,
            "interest_during_construction_percentage": 14,
            "apartment_improvements": {
                "items": [],
                "summary": {
                    "value": 0.0,
                    "index_adjusted": 0.0,
                    "depreciation": 0.0,
                    "value_for_apartment": 0.0,
                },
            },
            "housing_company_improvements": {
                "items": [],
                "summary": {
                    "value": 0.0,
                    "value_for_apartment": 0.0,
                },
            },
            "debt_free_price": 200000.0,
            "debt_free_price_m2": 20000.0,
            "apartment_share_of_housing_company_loans": 0,
            "apartment_share_of_housing_company_loans_date": "2003-06-01",
            "completion_date": "2003-05-09",
            "completion_date_index": 100.0,
            "calculation_date": "2003-06-01",
            "calculation_date_index": 200.0,
        },
        "maximum_price": 200000.0,
        "valid_until": "2003-09-01",
        "maximum": True,
    }

    assert response_json["calculations"]["market_price_index"] == {
        "calculation_variables": {
            "acquisition_price": 100000.0,
            "interest_during_construction": 0,
            "interest_during_construction_percentage": 6,
            "basic_price": 100000.0,
            "index_adjustment": 100000.0,
            "apartment_improvements": {
                "items": [],
                "summary": {
                    "value": 0.0,
                    "value_without_excess": 0.0,
                    "depreciation": 0.0,
                    "excess": {
                        "surface_area": 10.0,
                        "total": 1000.0,
                        "value_per_square_meter": 100.0,
                    },
                    "accepted_value": 0.0,
                },
            },
            "housing_company_improvements": {
                "items": [],
                "summary": {
                    "value": 0.0,
                    "value_without_excess": 0.0,
                    "excess": {
                        "surface_area": 10.0,
                        "value_per_square_meter_before_2010": None,
                        "value_per_square_meter_after_2010": None,
                        "total_before_2010": None,
                        "total_after_2010": None,
                    },
                    "depreciation": 0.0,
                    "accepted_value_for_housing_company": 0.0,
                    "accepted_value": 0.0,
                },
            },
            "debt_free_price": 200000.0,
            "debt_free_price_m2": 20000.0,
            "apartment_share_of_housing_company_loans": 0,
            "apartment_share_of_housing_company_loans_date": "2003-06-01",
            "completion_date": "2003-05-09",
            "completion_date_index": 100.0,
            "calculation_date": "2003-06-01",
            "calculation_date_index": 200.0,
        },
        "maximum_price": 200000.0,
        "valid_until": "2003-09-01",
        "maximum": True,
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
        "apartment_share_of_housing_company_loans_date": "2099-10-01",  # Date in the future
        "additional_info": "Example",
    }

    response = api_client.post(
        reverse("hitas:maximum-price-list", args=[a.housing_company.uuid.hex, a.uuid.hex]),
        data=data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    response_json = response.json()
    assert_id(response_json.pop("id"))
    assert_created(response_json.pop("created_at"))

    assert response_json == {
        "confirmed_at": None,
        "calculation_date": "2022-09-29",
        "maximum_price": 236292.0,
        "valid_until": "2022-11-30",
        "index": "surface_area_price_ceiling",
        "new_hitas": True,
        "calculations": {
            "construction_price_index": {
                "calculation_variables": {
                    "acquisition_price": 169583.0,
                    "additional_work_during_construction": 0.0,
                    "basic_price": 169583.0,
                    "index_adjustment": 48577.7,
                    "housing_company_improvements": {
                        "items": [],
                        "summary": {
                            "value": 0.0,
                            "value_added": 0.0,
                            "excess": {
                                "surface_area": 2703.5,
                                "value_per_square_meter": 30.0,
                                "total": 81105.0,
                            },
                            "value_for_housing_company": 0.0,
                            "value_for_apartment": 0.00,
                        },
                    },
                    "debt_free_price": 218160.7,
                    "debt_free_price_m2": 4498.16,
                    "apartment_share_of_housing_company_loans": 0,
                    "apartment_share_of_housing_company_loans_date": "2099-10-01",
                    "completion_date": "2012-01-13",
                    "completion_date_index": 115.9,
                    "calculation_date": "2022-09-29",
                    "calculation_date_index": 149.1,
                },
                "maximum_price": 218160.7,
                "valid_until": "2022-12-29",
                "maximum": False,
            },
            "market_price_index": {
                "calculation_variables": {
                    "acquisition_price": 169583.0,
                    "additional_work_during_construction": 0.0,
                    "basic_price": 169583.0,
                    "index_adjustment": 62626.6,
                    "housing_company_improvements": {
                        "items": [],
                        "summary": {
                            "value": 0.0,
                            "value_added": 0.0,
                            "excess": {
                                "surface_area": 2703.5,
                                "value_per_square_meter": 30.0,
                                "total": 81105.0,
                            },
                            "value_for_housing_company": 0.0,
                            "value_for_apartment": 0.0,
                        },
                    },
                    "debt_free_price": 232209.6,
                    "debt_free_price_m2": 4787.83,
                    "apartment_share_of_housing_company_loans": 0,
                    "apartment_share_of_housing_company_loans_date": "2099-10-01",
                    "completion_date": "2012-01-13",
                    "completion_date_index": 138.1,
                    "calculation_date": "2022-09-29",
                    "calculation_date_index": 189.1,
                },
                "maximum_price": 232209.6,
                "valid_until": "2022-12-29",
                "maximum": False,
            },
            "surface_area_price_ceiling": {
                "maximum_price": 236292.0,
                "valid_until": "2022-11-30",
                "maximum": True,
                "calculation_variables": {
                    "calculation_date": "2022-09-29",
                    "calculation_date_value": 4872.0,
                    "debt_free_price": 236292,
                    "surface_area": 48.5,
                    "apartment_share_of_housing_company_loans": 0,
                    "apartment_share_of_housing_company_loans_date": "2099-10-01",
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
        "additional_info": "Example",
    }
