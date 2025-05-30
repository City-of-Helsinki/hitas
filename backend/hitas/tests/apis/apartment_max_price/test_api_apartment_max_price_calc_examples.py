import datetime
from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from hitas.models import (
    Apartment,
    ApartmentConstructionPriceImprovement,
    ApartmentMarketPriceImprovement,
    ApartmentSale,
    HousingCompanyConstructionPriceImprovement,
    HousingCompanyMarketPriceImprovement,
    Ownership,
)
from hitas.models.housing_company import HitasType
from hitas.tests.apis.apartment_max_price.utils import assert_created, assert_id
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import (
    ApartmentConstructionPriceImprovementFactory,
    ApartmentFactory,
    ApartmentMarketPriceImprovementFactory,
    ApartmentSaleFactory,
    HousingCompanyConstructionPriceImprovementFactory,
    HousingCompanyMarketPriceImprovementFactory,
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
        additional_work_during_construction=0,
        completion_date=datetime.date(2018, 11, 27),
        surface_area=30.0,
        share_number_start=18402,
        share_number_end=20784,
        sales=[],
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    # Create another apartment with rest of the surface area and later completion date
    # The latest completed apartment in the company determines which indices are used for the calculation for New Hitas
    ApartmentFactory.create(
        building__real_estate__housing_company=a.housing_company,
        completion_date=datetime.date(2019, 11, 27),
        surface_area=4302,
    )
    # Soft-deleted apartments should not be included in the calculation
    ApartmentFactory.create(
        building__real_estate__housing_company=a.housing_company,
        completion_date=datetime.date(2020, 11, 27),
        surface_area=4302,
    ).delete()

    # Construction price improvement is not used, since this apartment's housing company is using new hitas rules!
    HousingCompanyConstructionPriceImprovementFactory.create(
        housing_company=a.housing_company,
        value=150000,
        completion_date=datetime.date(2020, 5, 21),
    )
    mpi_improvement: HousingCompanyMarketPriceImprovement = HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=a.housing_company,
        value=150000,
        completion_date=datetime.date(2020, 5, 21),
    )
    mpi_improvement2: HousingCompanyMarketPriceImprovement = HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=a.housing_company,
        value=100000,
        completion_date=datetime.date(2020, 5, 21),
        no_deductions=True,
    )

    sale: ApartmentSale = ApartmentSaleFactory.create(
        apartment=a,
        purchase_price=80350,
        apartment_share_of_housing_company_loans=119150,
        ownerships=[],
    )
    o1: Ownership = OwnershipFactory.create(percentage=75.2, sale=sale)
    o2: Ownership = OwnershipFactory.create(percentage=24.8, sale=sale)

    # Create necessary apartment's completion date indices
    ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2019, 11, 1), value=129.29)
    MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2019, 11, 1), value=167.9)

    # Create necessary improvement's completion date indices
    ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2020, 5, 1), value=129.20)
    MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2020, 5, 1), value=171.0)

    # Create necessary calculation date indices
    ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2022, 7, 1), value=146.4)
    MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2022, 7, 1), value=189.1)
    SurfaceAreaPriceCeilingFactory.create(month=datetime.date(2022, 7, 1), value=4869)
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
    calculations = response_json.pop("calculations")

    assert response_json == {
        "confirmed_at": None,
        "maximum_price": 224343.43,
        "maximum_price_per_square": 7478.11,
        "calculation_date": "2022-07-05",
        "valid_until": "2022-10-05",
        "index": "construction_price_index",
        "new_hitas": True,
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
            },
        },
        "additional_info": "Example",
    }

    assert calculations["construction_price_index"] == {
        "maximum_price": 224343.43,
        "valid_until": "2022-10-05",
        "maximum": True,
        "calculation_variables": {
            "first_sale_acquisition_price": 199500.0,
            "additional_work_during_construction": 0,
            "basic_price": 199500.0,
            "index_adjustment": 26401.46,
            "housing_company_improvements": {
                "items": [
                    {
                        "name": mpi_improvement.name,
                        "value": float(mpi_improvement.value),
                        "completion_date": mpi_improvement.completion_date.isoformat(),
                        "value_added": 20040.0,
                        "value_for_apartment": 157.26,
                        "value_for_housing_company": 22707.86,
                    },
                    {
                        "name": mpi_improvement2.name,
                        "value": float(mpi_improvement2.value),
                        "completion_date": mpi_improvement2.completion_date.isoformat(),
                        "value_added": 100000.0,
                        "value_for_apartment": 784.71,
                        "value_for_housing_company": 113312.69,
                    },
                ],
                "summary": {
                    "value": 250_000.0,
                    "value_added": 120040.0,
                    "excess": {
                        "surface_area": 4332.0,
                        "value_per_square_meter": 30.0,
                        "total": 129960.0,
                    },
                    "value_for_apartment": 941.97,
                    "value_for_housing_company": 136020.56,
                },
            },
            "debt_free_price": 226843.43,
            "debt_free_price_m2": 7561.45,
            "apartment_share_of_housing_company_loans": 2500,
            "apartment_share_of_housing_company_loans_date": "2022-07-28",
            "completion_date": "2019-11-27",
            "completion_date_index": 129.29,
            "calculation_date": "2022-07-05",
            "calculation_date_index": 146.4,
        },
    }

    assert calculations["market_price_index"] == {
        "maximum_price": 223109.29,
        "valid_until": "2022-10-05",
        "maximum": False,
        "calculation_variables": {
            "first_sale_acquisition_price": 199500.0,
            "additional_work_during_construction": 0,
            "basic_price": 199500.0,
            "index_adjustment": 25189.99,
            "housing_company_improvements": {
                "items": [
                    {
                        "name": mpi_improvement.name,
                        "value": float(mpi_improvement.value),
                        "completion_date": mpi_improvement.completion_date.isoformat(),
                        "value_added": 20040.0,
                        "value_for_housing_company": 22161.19,
                        "value_for_apartment": 153.47,
                    },
                    {
                        "name": mpi_improvement2.name,
                        "value": float(mpi_improvement2.value),
                        "completion_date": mpi_improvement2.completion_date.isoformat(),
                        "value_added": 100000.0,
                        "value_for_apartment": 765.82,
                        "value_for_housing_company": 110584.8,
                    },
                ],
                "summary": {
                    "value": 250000.0,
                    "value_added": 120040.0,
                    "excess": {
                        "surface_area": 4332.0,
                        "value_per_square_meter": 30.0,
                        "total": 129960.0,
                    },
                    "value_for_housing_company": 132745.99,
                    "value_for_apartment": 919.29,
                },
            },
            "debt_free_price": 225609.29,
            "debt_free_price_m2": 7520.31,
            "apartment_share_of_housing_company_loans": 2500,
            "apartment_share_of_housing_company_loans_date": "2022-07-28",
            "completion_date": "2019-11-27",
            "completion_date_index": 167.9,
            "calculation_date": "2022-07-05",
            "calculation_date_index": 189.1,
        },
    }

    assert calculations["surface_area_price_ceiling"] == {
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
    }

    response = api_client.get(
        reverse("hitas:maximum-price-detail", args=[a.housing_company.uuid.hex, a.uuid.hex, mpc_id]),
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    response_json = response.json()
    assert_id(response_json.pop("id"))
    assert_created(response_json.pop("created_at"))

    # Update first sale date to after apartment completion date, this should have no effect on the calculation
    sale.purchase_date = datetime.date(2018, 11, 27)  # Later than apartment completion date
    sale.save()
    sale.refresh_from_db()

    response = api_client.post(
        reverse("hitas:maximum-price-list", args=[a.housing_company.uuid.hex, a.uuid.hex]),
        data=data,
        format="json",
    )
    assert response.json()["calculations"] == calculations


@pytest.mark.django_db
def test__api__apartment_max_price__market_price_index__2011_onwards(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        additional_work_during_construction=0,
        completion_date=datetime.date(2014, 8, 27),
        surface_area=48.0,
        share_number_start=1,
        share_number_end=142,
        sales=[],
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    # Create another apartment with rest of the surface area
    ApartmentFactory.create(
        completion_date=datetime.date(2014, 8, 27),
        building__real_estate__housing_company=a.housing_company,
        surface_area=2655,
    )

    # Construction price improvement is not used, since this apartment's housing company is using new hitas rules!
    HousingCompanyConstructionPriceImprovementFactory.create(
        housing_company=a.housing_company, value=150000, completion_date=datetime.date(2020, 5, 21)
    )

    mpi_improvement: HousingCompanyMarketPriceImprovement = HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=a.housing_company, value=150000, completion_date=datetime.date(2020, 5, 21)
    )

    sale: ApartmentSale = ApartmentSaleFactory.create(
        apartment=a,
        purchase_price=139706,
        apartment_share_of_housing_company_loans=80955,
        ownerships=[],
    )
    o1: Ownership = OwnershipFactory.create(percentage=100.0, sale=sale)

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
    calculations = response_json.pop("calculations")

    assert response_json == {
        "confirmed_at": None,
        "calculation_date": "2022-07-05",
        "maximum_price": 275924.91,
        "maximum_price_per_square": 5748.44,
        "valid_until": "2022-10-05",
        "index": "market_price_index",
        "new_hitas": True,
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
            },
        },
        "additional_info": "Example",
    }
    assert calculations["construction_price_index"] == {
        "calculation_variables": {
            "first_sale_acquisition_price": 220661.0,
            "additional_work_during_construction": 0.0,
            "basic_price": 220661.0,
            "index_adjustment": 40916.09,
            "housing_company_improvements": {
                "items": [
                    {
                        "name": mpi_improvement.name,
                        "value": float(mpi_improvement.value),
                        "completion_date": mpi_improvement.completion_date.isoformat(),
                        "value_added": 68910.0,
                        "value_for_apartment": 1386.62,
                        "value_for_housing_company": 78083.78,
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
                    "value_for_apartment": 1386.62,
                    "value_for_housing_company": 78083.78,
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
    }
    assert calculations["market_price_index"] == {
        "calculation_variables": {
            "first_sale_acquisition_price": 220661.0,
            "additional_work_during_construction": 0.0,
            "basic_price": 220661.0,
            "index_adjustment": 56410.68,
            "housing_company_improvements": {
                "items": [
                    {
                        "name": mpi_improvement.name,
                        "value": float(mpi_improvement.value),
                        "completion_date": mpi_improvement.completion_date.isoformat(),
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
    }
    assert calculations["surface_area_price_ceiling"] == {
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
    }


@pytest.mark.django_db
def test__api__apartment_max_price__market_price_index__pre_2011(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        interest_during_construction_mpi=3455.0,
        interest_during_construction_cpi=4000.0,
        additional_work_during_construction=4307.0,
        completion_date=datetime.date(2003, 5, 9),
        surface_area=54.5,
        share_number_start=1,
        share_number_end=2,
        sales=[],
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
    )
    # Create another apartment with a later completion date and rest of the surface area.
    # As Old-Hitas rules use the apartment completion date for the maximum price calculation,
    # this apartment should not affect the calculation.
    ApartmentFactory.create(
        completion_date=datetime.date(2003, 6, 9),
        building__real_estate__housing_company=a.housing_company,
        surface_area=3336,
        share_number_start=3,
        share_number_end=4,
        sales__purchase_price=0.0,
        sales__apartment_share_of_housing_company_loans=0.0,
    )

    mpi_ap_improvement: ApartmentMarketPriceImprovement = ApartmentMarketPriceImprovementFactory.create(
        apartment=a, value=10000, completion_date=datetime.date(2003, 5, 1)
    )
    mpi_ap_improvement2: ApartmentMarketPriceImprovement = ApartmentMarketPriceImprovementFactory.create(
        apartment=a, value=10000, completion_date=datetime.date(2003, 5, 1), no_deductions=True
    )

    mpi_hc_improvement: HousingCompanyMarketPriceImprovement = HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=a.housing_company, value=0, completion_date=datetime.date(2003, 5, 1)
    )
    mpi_hc_improvement2: HousingCompanyMarketPriceImprovement = HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=a.housing_company, value=1587, completion_date=datetime.date(2004, 10, 1)
    )
    mpi_hc_improvement3: HousingCompanyMarketPriceImprovement = HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=a.housing_company, value=2000, completion_date=datetime.date(2004, 10, 1), no_deductions=True
    )

    sale: ApartmentSale = ApartmentSaleFactory.create(
        apartment=a,
        purchase_price=104693.0,
        apartment_share_of_housing_company_loans=18480.0,
        ownerships=[],
    )
    o1: Ownership = OwnershipFactory.create(percentage=50.0, sale=sale)
    o2: Ownership = OwnershipFactory.create(percentage=50.0, sale=sale)

    # Create necessary apartment's completion date indices
    ConstructionPriceIndexFactory.create(month=datetime.date(2003, 5, 1), value=244.9)
    MarketPriceIndexFactory.create(month=datetime.date(2003, 5, 1), value=263.60)

    # Create necessary calculation date indices
    ConstructionPriceIndexFactory.create(month=datetime.date(2022, 9, 1), value=364.40)
    MarketPriceIndexFactory.create(month=datetime.date(2022, 9, 1), value=583.3)
    SurfaceAreaPriceCeilingFactory.create(month=datetime.date(2022, 9, 1), value=4872)

    # Create necessary improvement's completion date indices
    ConstructionPriceIndexFactory.create(month=datetime.date(2004, 10, 1), value=238.5)
    MarketPriceIndexFactory.create(month=datetime.date(2004, 10, 1), value=291.1)

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
    calculations = response_json.pop("calculations")

    assert response_json == {
        "confirmed_at": None,
        "calculation_date": "2022-09-07",
        "maximum_price": 313867.91,
        "maximum_price_per_square": 5759.04,
        "valid_until": "2022-12-07",
        "index": "market_price_index",
        "new_hitas": False,
        "apartment": {
            "shares": {"start": 1, "end": 2, "total": 2},
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
            },
        },
        "additional_info": "Example",
    }
    assert calculations["construction_price_index"] == {
        "calculation_variables": {
            "housing_company_acquisition_price": 170_886.35,
            "housing_company_assets": 170_886.35,
            "apartment_share_of_housing_company_assets": 170886.35,
            "interest_during_construction": 4000.0,
            "interest_during_construction_percentage": 14,
            "additional_work_during_construction": 4307.0,
            "index_adjusted_additional_work_during_construction": 6408.62,
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
            "debt_free_price": 181294.97,
            "debt_free_price_m2": 3326.51,
            "apartment_share_of_housing_company_loans": 0,
            "apartment_share_of_housing_company_loans_date": "2022-09-05",
            "completion_date": str(a.completion_date),
            "completion_date_index": 244.9,
            "calculation_date": "2022-09-07",
            "calculation_date_index": 364.4,
            "depreciation_multiplier": "0.9324",
        },
        "maximum_price": 181294.97,
        "valid_until": "2022-12-07",
        "maximum": False,
    }
    assert calculations["market_price_index"] == {
        "calculation_variables": {
            "first_sale_acquisition_price": 123173.0,
            "interest_during_construction": 3455.0,
            "interest_during_construction_percentage": 6,
            "additional_work_during_construction": 4307.0,
            "basic_price": 130935.0,
            "index_adjustment": 158800.91,
            "apartment_improvements": {
                "items": [
                    {
                        "name": mpi_ap_improvement.name,
                        "value": 10000.0,
                        "value_without_excess": 4550.0,
                        "completion_date": "2003-05-01",
                        "depreciation": {"amount": 4550.0, "time": {"months": 4, "years": 19}},
                        "accepted_value": 0.0,
                        "no_deductions": False,
                    },
                    {
                        "name": mpi_ap_improvement2.name,
                        "value": 10000.0,
                        "value_without_excess": 22128.22,
                        "completion_date": "2003-05-01",
                        "depreciation": {"amount": 0.0, "time": {"months": 0, "years": 0}},
                        "accepted_value": 22128.22,
                        "no_deductions": True,
                    },
                ],
                "summary": {
                    "value": 20000.0,
                    "value_without_excess": 22128.22 + 4550.0,
                    "depreciation": 4550.0,
                    "excess": {"surface_area": 54.5, "total": 5450.0, "value_per_square_meter": 100.0},
                    "accepted_value": 22128.22,
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
                        "no_deductions": False,
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
                        "no_deductions": False,
                    },
                    {
                        "name": mpi_hc_improvement3.name,
                        "value": 2000.0,
                        "completion_date": "2004-10-01",
                        "value_without_excess": 4007.56,
                        "depreciation": {
                            "amount": 0.0,
                            "time": {
                                "years": 0,
                                "months": 0,
                            },
                        },
                        "accepted_value_for_housing_company": 4007.56,
                        "accepted_value": 2003.78,
                        "no_deductions": True,
                    },
                ],
                "summary": {
                    "value": 3587.0,
                    "value_without_excess": 4007.56,
                    "excess": {
                        "surface_area": 3390.5,
                        "value_per_square_meter_before_2010": 150.0,
                        "value_per_square_meter_after_2010": None,
                        "total_before_2010": 508575.0,
                        "total_after_2010": None,
                    },
                    "depreciation": 0.0,
                    "accepted_value_for_housing_company": 4007.56,
                    "accepted_value": 2003.78,
                },
            },
            "debt_free_price": 313867.91,
            "debt_free_price_m2": 5759.04,
            "apartment_share_of_housing_company_loans": 0,
            "apartment_share_of_housing_company_loans_date": "2022-09-05",
            "completion_date": str(a.completion_date),
            "completion_date_index": 263.6,
            "calculation_date": "2022-09-07",
            "calculation_date_index": 583.3,
        },
        "maximum_price": 313867.91,
        "valid_until": "2022-12-07",
        "maximum": True,
    }
    assert calculations["surface_area_price_ceiling"] == {
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
    }


@pytest.mark.django_db
def test__api__apartment_max_price__construction_price_index__pre_2011(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        interest_during_construction_mpi=2703.0,
        interest_during_construction_cpi=3233.0,
        additional_work_during_construction=2500.0,
        completion_date=datetime.date(2012, 6, 28),
        surface_area=45.5,
        share_number_start=19717,
        share_number_end=20188,
        sales=[],
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
    )
    # Create another apartment with rest of the surface area
    ApartmentFactory.create(
        building__real_estate__housing_company=a.housing_company,
        completion_date=datetime.date(2010, 1, 1),
        surface_area=10915.0,
        sales__purchase_price=0.0,
        sales__apartment_share_of_housing_company_loans=0.0,
    )
    # Create another apartment with same completion date and rest of the acquisition price
    ApartmentFactory.create(
        building__real_estate__housing_company=a.housing_company,
        completion_date=a.completion_date,
        surface_area=0,
        sales__purchase_price=16551639.5,
        sales__apartment_share_of_housing_company_loans=0.5,
    )
    # Create another apartment with a later completion date and rest of the acquisition price.
    # As Old-Hitas rules use the apartment completion date for the maximum price calculation,
    # this apartment should not affect the calculation.
    ApartmentFactory.create(
        building__real_estate__housing_company=a.housing_company,
        completion_date=datetime.date(2012, 7, 28),
        surface_area=0.0,
        sales__purchase_price=20545029.0,
        sales__apartment_share_of_housing_company_loans=1.0,
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

    sale: ApartmentSale = ApartmentSaleFactory.create(
        apartment=a,
        purchase_price=52738.0,
        apartment_share_of_housing_company_loans=123192.0,
        ownerships=[],
    )
    o1: Ownership = OwnershipFactory.create(percentage=100.0, sale=sale)

    # Create necessary housing company's completion date indices
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
    calculations = response_json.pop("calculations")

    assert response_json == {
        "confirmed_at": None,
        "calculation_date": "2022-11-21",
        "maximum_price": 386683.32,
        "maximum_price_per_square": 8498.53,
        "valid_until": "2023-02-21",
        "index": "market_price_index",
        "new_hitas": False,
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
            },
        },
        "additional_info": "Example",
    }
    assert calculations["construction_price_index"] == {
        "calculation_variables": {
            "housing_company_acquisition_price": 20_374_887.55,
            "housing_company_assets": 20_823_677.55,
            "apartment_share_of_housing_company_assets": 219010.27,
            "interest_during_construction": 3233.0,
            "interest_during_construction_percentage": 6,
            "additional_work_during_construction": 2500.0,
            "index_adjusted_additional_work_during_construction": 3078.35,
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
                    }
                ],
                "summary": {
                    "value": 15_000.0,
                    "index_adjusted": 17288.91,
                    "depreciation": 4178.15,
                    "value_for_apartment": 13110.75,
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
            "debt_free_price": 238432.37,
            "debt_free_price_m2": 5240.27,
            "apartment_share_of_housing_company_loans": 3000,
            "apartment_share_of_housing_company_loans_date": "2022-11-20",
            "completion_date": str(a.completion_date),
            "completion_date_index": 296.10,
            "calculation_date": "2022-11-21",
            "calculation_date_index": 364.6,
            "depreciation_multiplier": "0.9892",
        },
        "maximum_price": 235432.37,
        "valid_until": "2023-02-21",
        "maximum": False,
    }
    assert calculations["market_price_index"] == {
        "calculation_variables": {
            "first_sale_acquisition_price": 175_930.0,
            "interest_during_construction": 2703.0,
            "interest_during_construction_percentage": 6,
            "additional_work_during_construction": 2500.0,
            "basic_price": 181_133.0,
            "index_adjustment": 208_550.32,
            "apartment_improvements": {
                "items": [],
                "summary": {
                    "value": 0.0,
                    "value_without_excess": 0.0,
                    "excess": {
                        "surface_area": 45.5,
                        "total": 4550.0,
                        "value_per_square_meter": 100.0,
                    },
                    "depreciation": 0.0,
                    "accepted_value": 0.0,
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
            "completion_date": str(a.completion_date),
            "completion_date_index": 263.6,
            "calculation_date": "2022-11-21",
            "calculation_date_index": 567.1,
        },
        "maximum_price": 386683.32,
        "valid_until": "2023-02-21",
        "maximum": True,
    }
    assert calculations["surface_area_price_ceiling"] == {
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
    }

    # Update first sale date to after apartment completion date, sale date is used instead of apartment completion date
    sale.purchase_date = datetime.date(2013, 6, 28)  # Later than apartment completion date
    sale.save()
    sale.refresh_from_db()
    ConstructionPriceIndexFactory.create(month=datetime.date(2013, 6, 1), value=1337)

    response = api_client.post(
        reverse("hitas:maximum-price-list", args=[a.housing_company.uuid.hex, a.uuid.hex]),
        data=data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    response_json = response.json()
    construction_price_index_calculation = response_json["calculations"]["construction_price_index"]
    assert construction_price_index_calculation == {
        "calculation_variables": {
            "housing_company_acquisition_price": 4_512_344.21,
            "housing_company_assets": 4_961_134.2,
            "apartment_share_of_housing_company_assets": 52178.07,
            "interest_during_construction": 3233.0,
            "interest_during_construction_percentage": 6,
            "additional_work_during_construction": 2500.0,
            "index_adjusted_additional_work_during_construction": 681.75,
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
                    }
                ],
                "summary": {
                    "value": 15_000.0,
                    "index_adjusted": 17288.91,
                    "depreciation": 4178.15,
                    "value_for_apartment": 13110.75,
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
            "debt_free_price": 69203.58,
            "debt_free_price_m2": 1520.96,
            "apartment_share_of_housing_company_loans": 3000,
            "apartment_share_of_housing_company_loans_date": "2022-11-20",
            "completion_date": str(a.completion_date),
            "completion_date_index": 1337.0,
            "calculation_date": "2022-11-21",
            "calculation_date_index": 364.6,
            "depreciation_multiplier": "0.9892",
        },
        "maximum_price": 66203.58,
        "valid_until": "2023-02-21",
        "maximum": False,
    }


@pytest.mark.parametrize("during_construction", [0, None])
@pytest.mark.django_db
def test__api__apartment_max_price__pre_2011__no_improvements(api_client: HitasAPIClient, during_construction):
    a: Apartment = ApartmentFactory.create(
        interest_during_construction_mpi=during_construction,
        interest_during_construction_cpi=during_construction,
        additional_work_during_construction=during_construction,
        completion_date=datetime.date(2003, 5, 9),
        surface_area=10,
        share_number_start=100,
        share_number_end=200,
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        sales__purchase_price=100000,
        sales__apartment_share_of_housing_company_loans=0,
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
    calculations = response_json.pop("calculations")

    assert calculations["construction_price_index"] == {
        "calculation_variables": {
            "housing_company_acquisition_price": 200000.0,
            "housing_company_assets": 200000.0,
            "apartment_share_of_housing_company_assets": 200000.0,
            "interest_during_construction": 0,
            "interest_during_construction_percentage": 14,
            "additional_work_during_construction": 0.0,
            "index_adjusted_additional_work_during_construction": 0.0,
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
            "depreciation_multiplier": "1",
        },
        "maximum_price": 200000.0,
        "valid_until": "2003-09-01",
        "maximum": True,
    }
    assert calculations["market_price_index"] == {
        "calculation_variables": {
            "first_sale_acquisition_price": 100000.0,
            "interest_during_construction": 0,
            "interest_during_construction_percentage": 6,
            "additional_work_during_construction": 0.0,
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
        additional_work_during_construction=0,
        completion_date=datetime.date(2012, 1, 13),
        surface_area=48.5,
        share_number_start=504,
        share_number_end=601,
        sales=[],
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    # Create another apartment with rest of the surface area
    ApartmentFactory.create(
        completion_date=datetime.date(2012, 1, 13),
        building__real_estate__housing_company=a.housing_company,
        surface_area=2655,
    )

    sale: ApartmentSale = ApartmentSaleFactory.create(
        apartment=a,
        purchase_price=107753,
        apartment_share_of_housing_company_loans=61830,
        ownerships=[],
    )
    o1: Ownership = OwnershipFactory.create(percentage=100.0, sale=sale)

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
    calculations = response_json.pop("calculations")

    assert response_json == {
        "confirmed_at": None,
        "calculation_date": "2022-09-29",
        "maximum_price": 236292.0,
        "maximum_price_per_square": 4872.0,
        "valid_until": "2022-11-30",
        "index": "surface_area_price_ceiling",
        "new_hitas": True,
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
            },
        },
        "additional_info": "Example",
    }
    assert calculations["construction_price_index"] == {
        "calculation_variables": {
            "first_sale_acquisition_price": 169583.0,
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
    }
    assert calculations["market_price_index"] == {
        "calculation_variables": {
            "first_sale_acquisition_price": 169583.0,
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
    }
    assert calculations["surface_area_price_ceiling"] == {
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
    }


@pytest.mark.django_db
def test__api__apartment_max_price__no_sales_on_apartment__post_2011(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2012, 1, 13),
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )

    # Create necessary indices
    ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2012, 1, 1), value=115.9)
    MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2012, 1, 1), value=138.1)
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

    # Calculation should still work without any sales on the housing company apartments
    assert response.status_code == status.HTTP_200_OK, response.json()


@pytest.mark.django_db
def test__api__apartment_max_price__no_sales_on_apartment__has_catalog_prices__pre_2011(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2009, 1, 13),
        sales=[],
        catalog_purchase_price=1000.0,
        catalog_primary_loan_amount=2000.0,
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
    )

    # Create necessary indices
    ConstructionPriceIndexFactory.create(month=datetime.date(2009, 1, 1), value=115.9)
    MarketPriceIndexFactory.create(month=datetime.date(2009, 1, 1), value=138.1)
    ConstructionPriceIndexFactory.create(month=datetime.date(2022, 9, 1), value=149.1)
    MarketPriceIndexFactory.create(month=datetime.date(2022, 9, 1), value=189.1)
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

    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": "apartment_first_sale_purchase_price_missing",
        "message": "Maximum price calculation could not be completed. "
        "Cannot create max price calculation for an apartment without a first sale purchase price.",
        "reason": "Conflict",
        "status": 409,
    }


@pytest.mark.django_db
def test__api__apartment_max_price__no_sales_on_apartment__no_catalog_prices__pre_2011(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2009, 1, 13),
        sales=[],
        catalog_purchase_price=None,
        catalog_primary_loan_amount=None,
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
    )

    # Create necessary indices
    ConstructionPriceIndexFactory.create(month=datetime.date(2009, 1, 1), value=115.9)
    MarketPriceIndexFactory.create(month=datetime.date(2009, 1, 1), value=138.1)
    ConstructionPriceIndexFactory.create(month=datetime.date(2022, 9, 1), value=149.1)
    MarketPriceIndexFactory.create(month=datetime.date(2022, 9, 1), value=189.1)
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

    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": "apartment_first_sale_purchase_price_missing",
        "message": "Maximum price calculation could not be completed. "
        "Cannot create max price calculation for an apartment without a first sale purchase price.",
        "reason": "Conflict",
        "status": 409,
    }


@pytest.mark.django_db
def test__api__apartment_max_price__other_apartment_has_only_catalog_prices__pre_2011(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2009, 1, 13),
        catalog_purchase_price=None,
        catalog_primary_loan_amount=None,
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
    )

    ApartmentFactory.create(
        completion_date=datetime.date(2009, 1, 13),
        sales=[],
        catalog_purchase_price=1000.0,
        catalog_primary_loan_amount=2000.0,
        building__real_estate__housing_company=a.housing_company,
    )

    # Create necessary indices
    ConstructionPriceIndexFactory.create(month=datetime.date(2009, 1, 1), value=115.9)
    MarketPriceIndexFactory.create(month=datetime.date(2009, 1, 1), value=138.1)
    ConstructionPriceIndexFactory.create(month=datetime.date(2022, 9, 1), value=149.1)
    MarketPriceIndexFactory.create(month=datetime.date(2022, 9, 1), value=189.1)
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


@pytest.mark.django_db
def test__api__apartment_max_price__other_apartment_has_no_prices__pre_2011(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2009, 1, 13),
        catalog_purchase_price=None,
        catalog_primary_loan_amount=None,
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
    )

    ApartmentFactory.create(
        completion_date=datetime.date(2009, 1, 13),
        sales=[],
        catalog_purchase_price=None,
        catalog_primary_loan_amount=None,
        building__real_estate__housing_company=a.housing_company,
    )

    # Create necessary indices
    ConstructionPriceIndexFactory.create(month=datetime.date(2009, 1, 1), value=115.9)
    MarketPriceIndexFactory.create(month=datetime.date(2009, 1, 1), value=138.1)
    ConstructionPriceIndexFactory.create(month=datetime.date(2022, 9, 1), value=149.1)
    MarketPriceIndexFactory.create(month=datetime.date(2022, 9, 1), value=189.1)
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


@pytest.mark.django_db
def test__api__apartment_max_price__missing_property_manager(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        additional_work_during_construction=0,
        completion_date=datetime.date(2019, 11, 27),
        surface_area=30.0,
        share_number_start=18402,
        share_number_end=20784,
        sales=[],
        building__real_estate__housing_company__property_manager=None,
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    # Create another apartment with rest of the surface area
    ApartmentFactory.create(
        completion_date=datetime.date(2019, 11, 27),
        building__real_estate__housing_company=a.housing_company,
        surface_area=4302,
    )

    HousingCompanyConstructionPriceImprovementFactory.create(
        housing_company=a.housing_company, value=150000, completion_date=datetime.date(2020, 5, 21)
    )
    HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=a.housing_company, value=150000, completion_date=datetime.date(2020, 5, 21)
    )

    sale: ApartmentSale = ApartmentSaleFactory.create(
        apartment=a,
        purchase_price=80350,
        apartment_share_of_housing_company_loans=119150,
        ownerships=[],
    )
    OwnershipFactory.create(percentage=75.2, sale=sale)
    OwnershipFactory.create(percentage=24.8, sale=sale)

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
        reverse("hitas:maximum-price-list", args=[a.housing_company.uuid.hex, a.uuid.hex]),
        data=data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    assert response.json()["housing_company"]["property_manager"] == {"name": ""}


## RR Housing Companies


@pytest.mark.django_db
def test__api__apartment_max_price__rr_housing_company(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__hitas_type=HitasType.RR_NEW_HITAS,
        completion_date=datetime.date(2020, 1, 1),
        surface_area=100,
    )

    # Create necessary apartment's completion date indices
    ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2020, 1, 1), value=100)
    MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2020, 1, 1), value=100)

    # Create necessary calculation date indices
    ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2022, 1, 1), value=200)
    MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2022, 1, 1), value=200)
    SurfaceAreaPriceCeilingFactory.create(month=datetime.date(2022, 1, 1), value=200)

    data = {
        "calculation_date": "2022-01-01",
        "apartment_share_of_housing_company_loans": 2500,
        "apartment_share_of_housing_company_loans_date": "2022-07-28",
        "additional_info": "Example",
    }
    url = reverse("hitas:maximum-price-list", args=[a.housing_company.uuid.hex, a.uuid.hex])

    # First calculation we create should use the apartment's completion date, which is the same as housing company's
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()
    calculations = response.json().pop("calculations")
    assert calculations["construction_price_index"]["calculation_variables"]["completion_date"] == "2020-01-01"
    assert calculations["construction_price_index"]["calculation_variables"]["completion_date_index"] == 100
    assert calculations["market_price_index"]["calculation_variables"]["completion_date"] == "2020-01-01"
    assert calculations["market_price_index"]["calculation_variables"]["completion_date_index"] == 100

    # Now we create a second apartment which is incomplete, as RR, this should not affect the calculation even though
    # the housing company is not fully completed
    ApartmentFactory.create(
        building__real_estate__housing_company=a.housing_company,
        completion_date=None,
        surface_area=0,
    )

    # Create a second calculation, which should be unaffected by the new apartment as its incomplete
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json().pop("calculations") == calculations

    # But if the housing company has an apartment with a later completion date, that date is used instead
    ApartmentFactory.create(
        building__real_estate__housing_company=a.housing_company,
        completion_date=datetime.date(2021, 1, 1),
    )
    ConstructionPriceIndex2005Equal100Factory.create(month=datetime.date(2021, 1, 1), value=150)
    MarketPriceIndex2005Equal100Factory.create(month=datetime.date(2021, 1, 1), value=150)

    # Create a second calculation, which should be unaffected by the new apartment as its incomplete
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()
    calculations = response.json().pop("calculations")
    assert calculations["construction_price_index"]["calculation_variables"]["completion_date"] == "2021-01-01"
    assert calculations["construction_price_index"]["calculation_variables"]["completion_date_index"] == 150
    assert calculations["market_price_index"]["calculation_variables"]["completion_date"] == "2021-01-01"
    assert calculations["market_price_index"]["calculation_variables"]["completion_date_index"] == 150


@pytest.mark.django_db
def test__api__apartment_max_price__rr_housing_company__missing_surface_area(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__hitas_type=HitasType.RR_NEW_HITAS,
        completion_date=datetime.date(2020, 1, 1),
    )
    ApartmentFactory.create(
        building__real_estate__housing_company=a.housing_company,
        completion_date=None,
        surface_area=None,
    )

    data = {
        "calculation_date": "2022-01-01",
        "apartment_share_of_housing_company_loans": 0,
        "apartment_share_of_housing_company_loans_date": "2022-07-28",
        "additional_info": "Example",
    }

    response = api_client.post(
        reverse("hitas:maximum-price-list", args=[a.housing_company.uuid.hex, a.uuid.hex]), data=data, format="json"
    )
    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": "missing_surface_area_for_apartment",
        "message": "Maximum price calculation could not be completed. "
        "Cannot create max price calculation as an apartment is missing surface area.",
        "reason": "Conflict",
        "status": 409,
    }


@pytest.mark.django_db
def test__api__apartment_max_price__rr_housing_company__missing_share_numbers(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__hitas_type=HitasType.RR_NEW_HITAS,
        completion_date=datetime.date(2020, 1, 1),
    )
    ApartmentFactory.create(
        building__real_estate__housing_company=a.housing_company,
        completion_date=None,
        share_number_start=None,
        share_number_end=None,
    )

    data = {
        "calculation_date": "2022-01-01",
        "apartment_share_of_housing_company_loans": 0,
        "apartment_share_of_housing_company_loans_date": "2022-07-28",
        "additional_info": "Example",
    }

    response = api_client.post(
        reverse("hitas:maximum-price-list", args=[a.housing_company.uuid.hex, a.uuid.hex]), data=data, format="json"
    )
    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": "missing_share_numbers_for_apartment",
        "message": "Maximum price calculation could not be completed. "
        "Cannot create max price calculation for as an apartment is missing share numbers.",
        "reason": "Conflict",
        "status": 409,
    }


@pytest.mark.django_db
def test__api__apartment_max_price__rr_housing_company__apartment_not_complete(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__hitas_type=HitasType.RR_NEW_HITAS,
        completion_date=None,
    )
    ApartmentFactory.create(
        building__real_estate__housing_company=a.housing_company,
        completion_date=datetime.date(2020, 1, 1),
    )

    data = {
        "calculation_date": "2022-01-01",
        "apartment_share_of_housing_company_loans": 0,
        "apartment_share_of_housing_company_loans_date": "2022-07-28",
        "additional_info": "Example",
    }

    response = api_client.post(
        reverse("hitas:maximum-price-list", args=[a.housing_company.uuid.hex, a.uuid.hex]), data=data, format="json"
    )
    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": "missing_completion_date",
        "message": "Maximum price calculation could not be completed. Cannot create "
        "max price calculation for an apartment without completion date.",
        "reason": "Conflict",
        "status": 409,
    }
