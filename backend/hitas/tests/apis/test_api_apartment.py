import datetime
import uuid
from typing import Any, NamedTuple

import pytest
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from hitas.models import (
    Apartment,
    ApartmentMarketPriceImprovement,
    ApartmentMaximumPriceCalculation,
    ApartmentSale,
    ApartmentType,
    Building,
    ConditionOfSale,
    HousingCompany,
    Owner,
    Ownership,
    RealEstate,
)
from hitas.models.apartment import ApartmentConstructionPriceImprovement, ApartmentState
from hitas.models.condition_of_sale import GracePeriod
from hitas.models.housing_company import HitasType
from hitas.tests.apis.helpers import HitasAPIClient, InvalidInput, parametrize_helper
from hitas.tests.factories import (
    ApartmentConstructionPriceImprovementFactory,
    ApartmentFactory,
    ApartmentMarketPriceImprovementFactory,
    ApartmentSaleFactory,
    ApartmentTypeFactory,
    BuildingFactory,
    ConditionOfSaleFactory,
    HousingCompanyFactory,
    OwnerFactory,
    OwnershipFactory,
    RealEstateFactory,
)
from hitas.tests.factories.apartment import ApartmentMaximumPriceCalculationFactory
from hitas.tests.factories.indices import (
    ConstructionPriceIndex2005Equal100Factory,
    ConstructionPriceIndexFactory,
    MarketPriceIndex2005Equal100Factory,
    MarketPriceIndexFactory,
    SurfaceAreaPriceCeilingFactory,
)
from hitas.views.apartment import ApartmentDetailSerializer

PRE_2005_DATE = datetime.date(2004, 12, 1)
PRE_2011_DATE = datetime.date(2010, 12, 1)
POST_2011_DATE = datetime.date(2011, 1, 1)


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
    ap1: Apartment = ApartmentFactory.create(building=b, apartment_number=1, sales=[])
    ap2: Apartment = ApartmentFactory.create(building=b, apartment_number=2, sales=[])

    sale_1: ApartmentSale = ApartmentSaleFactory.create(apartment=ap1, ownerships=[])
    o1: Ownership = OwnershipFactory.create(percentage=50, sale=sale_1)
    o2: Ownership = OwnershipFactory.create(percentage=50, sale=sale_1)

    ap3: Apartment = ApartmentFactory.create(completion_date=datetime.date(2022, 1, 1), sales=[])
    sale_2: ApartmentSale = ApartmentSaleFactory.create(
        apartment=ap3, purchase_date=datetime.date(2022, 2, 1), ownerships=[]
    )
    o3: Ownership = OwnershipFactory.create(owner=o2.owner, percentage=100, sale=sale_2)

    ConditionOfSaleFactory.create(
        new_ownership=o3,
        old_ownership=o2,
        grace_period=GracePeriod.NOT_GIVEN,
    )

    response = api_client.get(reverse("hitas:apartment-list", args=[hc.uuid.hex]))

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "contents": [
            {
                "id": ap1.uuid.hex,
                "state": ap1.state.value,
                "type": ap1.apartment_type.value,
                "surface_area": float(ap1.surface_area),
                "rooms": ap1.rooms,
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
                    },
                    {
                        "owner": {
                            "id": o2.owner.uuid.hex,
                            "name": o2.owner.name,
                            "identifier": o2.owner.identifier,
                            "email": o2.owner.email,
                        },
                        "percentage": float(o2.percentage),
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
                "has_conditions_of_sale": True,
                "has_grace_period": False,
                "sell_by_date": str(sale_2.purchase_date),
            },
            {
                "id": ap2.uuid.hex,
                "state": ap2.state.value,
                "type": ap2.apartment_type.value,
                "surface_area": float(ap2.surface_area),
                "rooms": ap2.rooms,
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
                "has_conditions_of_sale": False,
                "has_grace_period": False,
                "sell_by_date": None,
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


@pytest.mark.django_db
def test__api__apartment__list__those_with_conditions_of_sale_come_first(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    re: RealEstate = RealEstateFactory.create(housing_company=hc)
    b: Building = BuildingFactory.create(real_estate=re)
    ap1: Apartment = ApartmentFactory.create(building=b, apartment_number=1, sales=[])
    ap2: Apartment = ApartmentFactory.create(building=b, apartment_number=2, sales=[])
    ap3: Apartment = ApartmentFactory.create(building=b, apartment_number=3, sales=[])

    sale_1: ApartmentSale = ApartmentSaleFactory.create(apartment=ap1, ownerships=[])
    sale_2: ApartmentSale = ApartmentSaleFactory.create(apartment=ap3, ownerships=[])
    o1: Ownership = OwnershipFactory.create(percentage=100, sale=sale_1)
    o2: Ownership = OwnershipFactory.create(owner=o1.owner, percentage=100, sale=sale_2)

    ConditionOfSaleFactory.create(
        new_ownership=o2,
        old_ownership=o1,
        grace_period=GracePeriod.NOT_GIVEN,
    )

    response = api_client.get(reverse("hitas:apartment-list", args=[hc.uuid.hex]))

    assert response.status_code == status.HTTP_200_OK, response.json()
    response_data = response.json()["contents"]
    assert len(response_data) == 3
    assert response_data[0]["id"] == ap1.uuid.hex
    assert response_data[1]["id"] == ap3.uuid.hex
    assert response_data[2]["id"] == ap2.uuid.hex


@pytest.mark.django_db
def test__api__apartment__list__minimal(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    re: RealEstate = RealEstateFactory.create(housing_company=hc)
    b: Building = BuildingFactory.create(real_estate=re)
    ap1: Apartment = ApartmentFactory.create(
        building=b,
        state=ApartmentState.FREE,
        apartment_type=None,
        surface_area=None,
        rooms=None,
        share_number_start=None,
        share_number_end=None,
        completion_date=None,
        street_address="Fakestreet 1",
        apartment_number=1,
        floor=None,
        stair="A",
        additional_work_during_construction=None,
        loans_during_construction=None,
        interest_during_construction_6=None,
        interest_during_construction_14=None,
        debt_free_purchase_price_during_construction=None,
        notes=None,
        sales=[],
    )

    response = api_client.get(reverse("hitas:apartment-list", args=[hc.uuid.hex]))

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "id": ap1.uuid.hex,
            "state": ap1.state.value,
            "type": ap1.apartment_type,
            "surface_area": ap1.surface_area,
            "rooms": ap1.rooms,
            "address": {
                "street_address": ap1.street_address,
                "postal_code": hc.postal_code.value,
                "city": hc.postal_code.city,
                "apartment_number": ap1.apartment_number,
                "stair": ap1.stair,
                "floor": ap1.floor,
            },
            "completion_date": ap1.completion_date,
            "ownerships": [],
            "links": {
                "housing_company": {
                    "id": hc.uuid.hex,
                    "display_name": hc.display_name,
                    "link": f"/api/v1/housing-companies/{hc.uuid.hex}",
                },
                "real_estate": {
                    "id": ap1.building.real_estate.uuid.hex,
                    "link": (
                        f"/api/v1/housing-companies/{hc.uuid.hex}" f"/real-estates/{ap1.building.real_estate.uuid.hex}"
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
            "has_conditions_of_sale": False,
            "has_grace_period": False,
            "sell_by_date": None,
        },
    ]


@pytest.mark.django_db
def test__api__apartment__list__fulfilled_not_listed(api_client: HitasAPIClient, settings):
    new_apartment: Apartment = ApartmentFactory.create(sales=[])
    old_apartment: Apartment = ApartmentFactory.create()
    cos: ConditionOfSale = ConditionOfSaleFactory.create(
        new_ownership__sale__apartment=new_apartment,
        old_ownership__sale__apartment=old_apartment,
    )
    cos.delete()

    url = reverse(
        "hitas:apartment-list",
        kwargs={"housing_company_uuid": old_apartment.building.real_estate.housing_company.uuid.hex},
    )
    response_1 = api_client.get(url)

    assert response_1.status_code == status.HTTP_200_OK, response_1.json()
    assert len(response_1.json()["contents"]) == 1
    assert response_1.json()["contents"][0]["has_conditions_of_sale"] is False


class GracePeriodTestArgs(NamedTuple):
    grace_period: GracePeriod
    sell_by_date: datetime.date


@pytest.mark.parametrize(
    **parametrize_helper(
        {
            "No grace period": GracePeriodTestArgs(
                grace_period=GracePeriod.NOT_GIVEN,
                sell_by_date=datetime.date(2023, 1, 1),
            ),
            "Grace period of three months": GracePeriodTestArgs(
                grace_period=GracePeriod.THREE_MONTHS,
                sell_by_date=datetime.date(2023, 4, 1),
            ),
            "Grace period of six months": GracePeriodTestArgs(
                grace_period=GracePeriod.SIX_MONTHS,
                sell_by_date=datetime.date(2023, 7, 1),
            ),
        }
    )
)
@pytest.mark.django_db
def test__api__apartment__list__sell_by_date(api_client: HitasAPIClient, grace_period, sell_by_date):
    old_ownership: Ownership = OwnershipFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(
        sale__apartment__completion_date=datetime.date(2023, 1, 1),
        sale__purchase_date=datetime.date(2023, 1, 1),
    )

    ConditionOfSaleFactory.create(
        new_ownership=new_ownership,
        old_ownership=old_ownership,
        grace_period=grace_period,
    )

    url = reverse(
        "hitas:apartment-list",
        kwargs={
            "housing_company_uuid": old_ownership.apartment.housing_company.uuid.hex,
        },
    )
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == 1
    assert response.json()["contents"][0]["sell_by_date"] == str(sell_by_date)


@pytest.mark.parametrize(
    **parametrize_helper(
        {
            "No grace period, New apartment 1 is first": GracePeriodTestArgs(
                grace_period=GracePeriod.NOT_GIVEN,
                sell_by_date=datetime.date(2023, 1, 1),
            ),
            "Grace period of three months, New apartment 2 is first": GracePeriodTestArgs(
                grace_period=GracePeriod.THREE_MONTHS,
                sell_by_date=datetime.date(2023, 3, 1),
            ),
            "Grace period of six months, New apartment 2 is first": GracePeriodTestArgs(
                grace_period=GracePeriod.SIX_MONTHS,
                sell_by_date=datetime.date(2023, 3, 1),
            ),
        }
    )
)
@pytest.mark.django_db
def test__api__apartment__list__sell_by_date__multiple(api_client: HitasAPIClient, grace_period, sell_by_date):
    old_ownership: Ownership = OwnershipFactory.create()
    new_ownership_1: Ownership = OwnershipFactory.create(
        sale__apartment__completion_date=datetime.date(2023, 1, 1),
        sale__purchase_date=datetime.date(2023, 1, 1),
    )
    new_ownership_2: Ownership = OwnershipFactory.create(
        sale__apartment__completion_date=datetime.date(2023, 3, 1),
        sale__purchase_date=datetime.date(2023, 3, 1),
    )

    ConditionOfSaleFactory.create(
        new_ownership=new_ownership_1,
        old_ownership=old_ownership,
        grace_period=grace_period,
    )
    ConditionOfSaleFactory.create(
        new_ownership=new_ownership_2,
        old_ownership=old_ownership,
        grace_period=GracePeriod.NOT_GIVEN,
    )

    url = reverse(
        "hitas:apartment-list",
        kwargs={
            "housing_company_uuid": old_ownership.apartment.housing_company.uuid.hex,
        },
    )
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == 1
    assert response.json()["contents"][0]["sell_by_date"] == str(sell_by_date)


@pytest.mark.django_db
def test__api__apartment__list__sell_by_date__first_sale_after_completion(api_client: HitasAPIClient):
    completion_date = datetime.date(2023, 1, 1)
    first_sale_date = datetime.date(2023, 2, 1)

    old_ownerships: Ownership = OwnershipFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(
        sale__apartment__completion_date=completion_date,
        sale__purchase_date=first_sale_date,
    )

    ConditionOfSaleFactory.create(
        new_ownership=new_ownership,
        old_ownership=old_ownerships,
        grace_period=GracePeriod.NOT_GIVEN,
    )

    url = reverse(
        "hitas:apartment-list",
        kwargs={
            "housing_company_uuid": old_ownerships.apartment.housing_company.uuid.hex,
        },
    )
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == 1
    assert response.json()["contents"][0]["sell_by_date"] == str(first_sale_date)


# Retrieve tests


@pytest.mark.django_db
def test__api__apartment__retrieve(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    ap1: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2011, 1, 1),
        additional_work_during_construction=4999.9,
        surface_area=50.5,
        sales=[],
    )
    ap2: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2020, 1, 1),
        sales=[],
    )

    hc: HousingCompany = ap1.housing_company
    cpi: ApartmentConstructionPriceImprovement = ApartmentConstructionPriceImprovementFactory.create(apartment=ap1)
    mpi: ApartmentMarketPriceImprovement = ApartmentMarketPriceImprovementFactory.create(apartment=ap1)
    ampc: ApartmentMaximumPriceCalculation = ApartmentMaximumPriceCalculationFactory.create(apartment=ap1)

    ConstructionPriceIndex2005Equal100Factory.create(month=ap1.completion_date, value=100.5)
    MarketPriceIndex2005Equal100Factory.create(month=ap1.completion_date, value=200.5)

    now = datetime.date.today().replace(day=1)
    ConstructionPriceIndex2005Equal100Factory.create(month=now, value=150.5)
    MarketPriceIndex2005Equal100Factory.create(month=now, value=250.5)
    SurfaceAreaPriceCeilingFactory.create(month=now, value=3000.5)

    sale_1: ApartmentSale = ApartmentSaleFactory.create(
        apartment=ap1,
        purchase_price=80000.1,
        apartment_share_of_housing_company_loans=15000.3,
        ownerships=[],
    )
    sale_2: ApartmentSale = ApartmentSaleFactory.create(
        apartment=ap2,
        purchase_date=datetime.date(2021, 1, 1),
        ownerships=[],
    )

    os1: Ownership = OwnershipFactory.create(sale=sale_1, owner=owner, percentage=100)
    os2: Ownership = OwnershipFactory.create(sale=sale_2, owner=owner, percentage=100)
    cos: ConditionOfSale = ConditionOfSaleFactory.create(
        new_ownership=os2,
        old_ownership=os1,
        grace_period=GracePeriod.NOT_GIVEN,
    )

    response = api_client.get(
        reverse(
            "hitas:apartment-detail",
            args=[hc.uuid.hex, ap1.uuid.hex],
        )
    )

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": ap1.uuid.hex,
        "state": ap1.state.value,
        "type": {
            "id": ap1.apartment_type.uuid.hex,
            "value": ap1.apartment_type.value,
            "description": ap1.apartment_type.description,
            "code": ap1.apartment_type.legacy_code_number,
        },
        "surface_area": float(ap1.surface_area),
        "rooms": ap1.rooms,
        "shares": {
            "start": ap1.share_number_start,
            "end": ap1.share_number_end,
            "total": ap1.share_number_end - ap1.share_number_start + 1,
        },
        "address": {
            "street_address": ap1.street_address,
            "postal_code": hc.postal_code.value,
            "city": hc.postal_code.city,
            "apartment_number": ap1.apartment_number,
            "floor": ap1.floor,
            "stair": ap1.stair,
        },
        "completion_date": str(ap1.completion_date),
        "prices": {
            "first_sale_purchase_price": float(ap1.first_sale_purchase_price),
            "first_sale_share_of_housing_company_loans": float(ap1.first_sale_share_of_housing_company_loans),
            "first_sale_acquisition_price": float(ap1.first_sale_acquisition_price),
            "catalog_purchase_price": float(ap1.catalog_purchase_price),
            "catalog_share_of_housing_company_loans": float(ap1.catalog_primary_loan_amount),
            "catalog_acquisition_price": float(ap1.catalog_acquisition_price),
            "first_purchase_date": str(ap1.first_purchase_date),
            "latest_sale_purchase_price": ap1.latest_sale_purchase_price,
            "latest_purchase_date": ap1.latest_purchase_date,
            "construction": {
                "loans": float(ap1.loans_during_construction),
                "interest": {
                    "rate_6": float(ap1.interest_during_construction_6),
                    "rate_14": float(ap1.interest_during_construction_14),
                },
                "debt_free_purchase_price": float(ap1.debt_free_purchase_price_during_construction),
                "additional_work": float(ap1.additional_work_during_construction),
            },
            "maximum_prices": {
                "confirmed": {
                    "id": ampc.uuid.hex,
                    "created_at": ampc.created_at.isoformat()[:-6] + "Z",
                    "confirmed_at": ampc.confirmed_at.isoformat()[:-6] + "Z",
                    "calculation_date": str(ampc.calculation_date),
                    "maximum_price": float(ampc.maximum_price),
                    "valid": {
                        "valid_until": ampc.valid_until.strftime("%Y-%m-%d"),
                        "is_valid": ampc.valid_until >= datetime.date.today(),
                    },
                },
                "unconfirmed": {
                    "pre_2011": None,
                    "onwards_2011": {
                        "construction_price_index": {
                            "value": 149751.69,  # (80000.1 + 15000.3 + 4999.9) * 150.5/100.5
                            "maximum": False,
                        },
                        "market_price_index": {
                            "value": 124938.03,  # (80000.1 + 15000.3 + 4999.9) * 250/200
                            "maximum": False,
                        },
                        "surface_area_price_ceiling": {
                            "value": 151525.25,  # 50.5 (surface_area) * 3000.5
                            "maximum": True,
                        },
                    },
                },
            },
        },
        "links": {
            "housing_company": {
                "id": hc.uuid.hex,
                "display_name": hc.display_name,
                "link": f"/api/v1/housing-companies/{hc.uuid.hex}",
            },
            "real_estate": {
                "id": ap1.building.real_estate.uuid.hex,
                "link": f"/api/v1/housing-companies/{hc.uuid.hex}/real-estates/{ap1.building.real_estate.uuid.hex}",
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
        "ownerships": [
            {
                "owner": {
                    "id": os1.owner.uuid.hex,
                    "name": os1.owner.name,
                    "identifier": os1.owner.identifier,
                    "email": os1.owner.email,
                },
                "percentage": float(os1.percentage),
            },
        ],
        "improvements": {
            "construction_price_index": [
                {
                    "name": cpi.name,
                    "value": float(cpi.value),
                    "completion_date": cpi.completion_date.strftime("%Y-%m"),
                    "depreciation_percentage": float(cpi.depreciation_percentage.value),
                },
            ],
            "market_price_index": [
                {
                    "name": mpi.name,
                    "value": float(mpi.value),
                    "completion_date": mpi.completion_date.strftime("%Y-%m"),
                    "no_deductions": False,
                },
            ],
        },
        "notes": ap1.notes,
        "conditions_of_sale": [
            {
                "id": cos.uuid.hex,
                "grace_period": str(cos.grace_period.value),
                "fulfilled": cos.fulfilled,
                "sell_by_date": str(sale_2.purchase_date),
                "apartment": {
                    "id": ap2.uuid.hex,
                    "address": {
                        "street_address": ap2.street_address,
                        "apartment_number": ap2.apartment_number,
                        "floor": ap2.floor,
                        "stair": ap2.stair,
                        "city": "Helsinki",
                        "postal_code": ap2.postal_code.value,
                    },
                    "housing_company": {
                        "id": ap2.housing_company.uuid.hex,
                        "display_name": ap2.housing_company.display_name,
                    },
                },
                "owner": {
                    "id": os2.owner.uuid.hex,
                    "name": os2.owner.name,
                    "identifier": os2.owner.identifier,
                    "email": os2.owner.email,
                },
            }
        ],
        "sell_by_date": str(sale_2.purchase_date),
    }


@pytest.mark.django_db
def test__api__apartment__retrieve__migrated_max_price(api_client: HitasAPIClient):
    ap: Apartment = ApartmentFactory.create(completion_date=datetime.date(2011, 1, 1))
    ampc: ApartmentMaximumPriceCalculation = ApartmentMaximumPriceCalculationFactory.create(
        apartment=ap, json=None, json_version=None
    )

    response = api_client.get(
        reverse(
            "hitas:apartment-detail",
            args=[ap.housing_company.uuid.hex, ap.uuid.hex],
        )
    )

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["prices"]["maximum_prices"]["confirmed"] == {
        "id": None,  # id hidden
        "created_at": ampc.created_at.isoformat()[:-6] + "Z",
        "confirmed_at": ampc.confirmed_at.isoformat()[:-6] + "Z",
        "calculation_date": str(ampc.calculation_date),
        "maximum_price": float(ampc.maximum_price),
        "valid": {
            "valid_until": ampc.valid_until.strftime("%Y-%m-%d"),
            "is_valid": ampc.valid_until >= datetime.date.today(),
        },
    }


@pytest.mark.django_db
def test__api__apartment__retrieve__confirmed_old_json_version(api_client: HitasAPIClient):
    ap: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2011, 1, 1),
    )
    ampc: ApartmentMaximumPriceCalculation = ApartmentMaximumPriceCalculationFactory.create(
        apartment=ap, json_version=1
    )

    response = api_client.get(
        reverse(
            "hitas:apartment-detail",
            args=[ap.housing_company.uuid.hex, ap.uuid.hex],
        )
    )

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["prices"]["maximum_prices"]["confirmed"] == {
        "id": None,  # id hidden
        "created_at": ampc.created_at.isoformat()[:-6] + "Z",
        "confirmed_at": ampc.confirmed_at.isoformat()[:-6] + "Z",
        "calculation_date": str(ampc.calculation_date),
        "maximum_price": float(ampc.maximum_price),
        "valid": {
            "valid_until": ampc.valid_until.strftime("%Y-%m-%d"),
            "is_valid": ampc.valid_until >= datetime.date.today(),
        },
    }


@pytest.mark.django_db
def test__api__apartment__retrieve__migrated_max_price__multiple_same_time(api_client: HitasAPIClient):
    ap: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2011, 1, 1),
    )
    ampc: ApartmentMaximumPriceCalculation = ApartmentMaximumPriceCalculationFactory.create(
        apartment=ap,
        json=None,
        json_version=None,
        maximum_price=100,
    )
    ampc2: ApartmentMaximumPriceCalculation = ApartmentMaximumPriceCalculationFactory.create(
        apartment=ap, json=None, json_version=None, maximum_price=200, confirmed_at=ampc.confirmed_at
    )
    ApartmentMaximumPriceCalculationFactory.create(
        apartment=ap, json=None, json_version=None, maximum_price=50, confirmed_at=ampc.confirmed_at
    )

    response = api_client.get(
        reverse(
            "hitas:apartment-detail",
            args=[ap.housing_company.uuid.hex, ap.uuid.hex],
        )
    )

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["prices"]["maximum_prices"]["confirmed"] == {
        "id": None,
        "created_at": ampc2.created_at.isoformat()[:-6] + "Z",
        "confirmed_at": ampc2.confirmed_at.isoformat()[:-6] + "Z",
        "calculation_date": str(ampc2.calculation_date),
        "maximum_price": ampc2.maximum_price,
        "valid": {
            "valid_until": str(ampc2.valid_until),
            "is_valid": ampc2.valid_until >= datetime.date.today(),
        },
    }


def _test_max_prices(
    api_client: HitasAPIClient,
    completion_date: datetime.date,
    create_completion_indices: bool,
    create_current_indices: bool,
    null_values: bool = False,
    old_hitas_ruleset: bool = False,
):
    pre_2011: bool = completion_date < datetime.date(2011, 1, 1)
    pre_2005: bool = completion_date < datetime.date(2005, 1, 1)

    # Setup test
    cpi_factory = ConstructionPriceIndexFactory if pre_2011 else ConstructionPriceIndex2005Equal100Factory
    mpi_factory = MarketPriceIndexFactory if pre_2011 else MarketPriceIndex2005Equal100Factory

    ap: Apartment = ApartmentFactory.create(
        completion_date=completion_date,
        additional_work_during_construction=5000 if not null_values else None,
        surface_area=50 if not null_values else None,
        interest_during_construction_6=1000,
        interest_during_construction_14=2000,
        building__real_estate__housing_company__hitas_type=(
            HitasType.HITAS_I if old_hitas_ruleset else HitasType.NEW_HITAS_I
        ),
        sales=[],
    )

    if not null_values:
        ApartmentSaleFactory.create(apartment=ap, purchase_price=80000, apartment_share_of_housing_company_loans=15000)

    if create_completion_indices:
        cpi_factory.create(month=ap.completion_date, value=100)
        mpi_factory.create(month=ap.completion_date, value=200)

    if create_current_indices:
        now = datetime.date.today().replace(day=1)
        cpi_factory.create(month=now, value=150)
        mpi_factory.create(month=now, value=250)
        SurfaceAreaPriceCeilingFactory.create(month=now, value=3000)

    # Validate apartment details has correct data returned
    response = api_client.get(
        reverse(
            "hitas:apartment-detail",
            args=[ap.housing_company.uuid.hex, ap.uuid.hex],
        )
    )

    values = {
        "construction_price_index": {
            "value": (
                153000  # (80000 + 15000 + 5000 + 2000) * 150 / 100
                if old_hitas_ruleset and pre_2005
                else 151500  # (80000 + 15000 + 5000 + 1000) * 150 / 100
                if old_hitas_ruleset
                else 150000  # (80000 + 15000 + 5000) * 150 / 100
                if create_current_indices and create_completion_indices and not null_values
                else None
            ),
            "maximum": create_current_indices and create_completion_indices and not null_values,
        },
        "market_price_index": {
            "value": (
                126250  # (80000 + 15000 + 5000 + 1000) * 250 / 200
                if old_hitas_ruleset
                else 125000  # (80000 + 15000 + 5000) * 250 / 200
                if create_current_indices and create_completion_indices and not null_values
                else None
            ),
            "maximum": False,
        },
        "surface_area_price_ceiling": {
            "value": 150000 if create_current_indices and not null_values else None,
            "maximum": create_current_indices and not null_values and not old_hitas_ruleset and not pre_2005,
        },
    }

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["prices"]["maximum_prices"]["unconfirmed"] == {
        "pre_2011": values if pre_2011 else None,
        "onwards_2011": None if pre_2011 else values,
    }

    # Validate fetching PDF report of unconfirmed prices

    response = api_client.post(
        reverse("hitas:apartment-detail", args=[ap.housing_company.uuid.hex, ap.uuid.hex])
        + "/reports/download-latest-unconfirmed-prices",
        data={"additional_info": "This is additional information"},
        format="json",
    )

    if create_current_indices and create_completion_indices and not null_values:
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.get("content-type") == "application/pdf"
    else:
        assert response.status_code == status.HTTP_409_CONFLICT, response.json()


@pytest.mark.django_db
def test__api__apartment__retrieve__2011_onwards__indices_set(api_client: HitasAPIClient):
    _test_max_prices(
        api_client,
        completion_date=POST_2011_DATE,
        create_completion_indices=True,
        create_current_indices=True,
    )


@pytest.mark.django_db
def test__api__apartment__retrieve__2011_onwards__completion_indices_missing(api_client: HitasAPIClient):
    _test_max_prices(
        api_client,
        completion_date=POST_2011_DATE,
        create_completion_indices=False,
        create_current_indices=True,
    )


@pytest.mark.django_db
def test__api__apartment__retrieve__2011_onwards__current_month_indices_missing(api_client: HitasAPIClient):
    _test_max_prices(
        api_client,
        completion_date=POST_2011_DATE,
        create_completion_indices=True,
        create_current_indices=False,
    )


@pytest.mark.django_db
def test__api__apartment__retrieve__2011_onwards__indices_missing(api_client: HitasAPIClient):
    _test_max_prices(
        api_client,
        completion_date=POST_2011_DATE,
        create_completion_indices=False,
        create_current_indices=False,
    )


@pytest.mark.django_db
def test__api__apartment__retrieve__pre_2011__indices_set(api_client: HitasAPIClient):
    _test_max_prices(
        api_client,
        completion_date=PRE_2011_DATE,
        create_completion_indices=True,
        create_current_indices=True,
    )


@pytest.mark.django_db
def test__api__apartment__retrieve__pre_2011__old_hitas_ruleset(api_client: HitasAPIClient):
    _test_max_prices(
        api_client,
        completion_date=PRE_2011_DATE,
        create_completion_indices=True,
        create_current_indices=True,
        old_hitas_ruleset=True,
    )


@pytest.mark.django_db
def test__api__apartment__retrieve__pre_2011__completion_indices_missing(api_client: HitasAPIClient):
    _test_max_prices(
        api_client,
        completion_date=PRE_2011_DATE,
        create_completion_indices=False,
        create_current_indices=True,
    )


@pytest.mark.django_db
def test__api__apartment__retrieve__pre_2011__current_month_indices_missing(api_client: HitasAPIClient):
    _test_max_prices(
        api_client,
        completion_date=PRE_2011_DATE,
        create_completion_indices=True,
        create_current_indices=False,
    )


@pytest.mark.django_db
def test__api__apartment__retrieve__pre_2011__indices_missing(api_client: HitasAPIClient):
    _test_max_prices(
        api_client,
        completion_date=PRE_2011_DATE,
        create_completion_indices=False,
        create_current_indices=False,
    )


@pytest.mark.django_db
def test__api__apartment__retrieve__pre_2005__old_hitas_ruleset(api_client: HitasAPIClient):
    _test_max_prices(
        api_client,
        completion_date=PRE_2005_DATE,
        create_completion_indices=True,
        create_current_indices=True,
        old_hitas_ruleset=True,
    )


@pytest.mark.parametrize(
    "completed,create_completion_indices,create_current_indices",
    (
        [PRE_2005_DATE, False, False],
        [PRE_2005_DATE, False, True],
        [PRE_2005_DATE, True, False],
        [PRE_2005_DATE, True, True],
        [PRE_2011_DATE, False, False],
        [PRE_2011_DATE, False, True],
        [PRE_2011_DATE, True, False],
        [PRE_2011_DATE, True, True],
        [POST_2011_DATE, False, True],
        [POST_2011_DATE, True, False],
    ),
)
@pytest.mark.django_db
def test__api__apartment__retrieve__indices__null_values(
    api_client: HitasAPIClient,
    completed: datetime.date,
    create_completion_indices: bool,
    create_current_indices: bool,
):
    _test_max_prices(
        api_client,
        completion_date=completed,
        create_completion_indices=create_completion_indices,
        create_current_indices=create_current_indices,
        null_values=True,
    )


@pytest.mark.parametrize("should_be_shown", [False, True])
@pytest.mark.django_db
def test__api__apartment__retrieve__condition_of_sale_fulfilled(api_client, freezer, settings, should_be_shown):
    freezer.move_to("2023-01-01 00:00:00+00:00")
    old_time = timezone.now()

    owner: Owner = OwnerFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(owner=owner)
    old_ownership: Ownership = OwnershipFactory.create(owner=owner)

    cos: ConditionOfSale = ConditionOfSaleFactory.create(new_ownership=new_ownership, old_ownership=old_ownership)
    cos.delete()

    freezer.move_to(
        old_time
        + settings.SHOW_FULFILLED_CONDITIONS_OF_SALE_FOR_MONTHS
        + relativedelta(seconds=int(not should_be_shown))
    )

    response = api_client.get(
        reverse(
            "hitas:apartment-detail",
            args=[
                old_ownership.apartment.housing_company.uuid.hex,
                old_ownership.apartment.uuid.hex,
            ],
        )
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    cos_list = response.json()["conditions_of_sale"]
    if should_be_shown:
        cos_fulfilled_str = cos.fulfilled.replace(tzinfo=None).isoformat(timespec="seconds") + "Z"

        assert len(cos_list) == 1
        assert cos_list[0]["id"] == cos.uuid.hex
        assert cos_list[0]["fulfilled"] == cos_fulfilled_str
    else:
        assert cos_list == []


@pytest.mark.parametrize("invalid_id", ["foo", "38432c233a914dfb9c2f54d9f5ad9063"])
@pytest.mark.django_db
def test__api__apartment__invalid_apartment_id(api_client: HitasAPIClient, invalid_id):
    a: Apartment = ApartmentFactory.create()

    response = api_client.get(
        reverse(
            "hitas:apartment-detail",
            args=[
                a.housing_company.uuid.hex,
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

    data = {
        "state": ApartmentState.SOLD.value,
        "type": {"id": apartment_type.uuid.hex},
        "surface_area": 69,
        "rooms": 88,
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
            "first_sale_purchase_price": 12345.1,
            "first_sale_share_of_housing_company_loans": 34567.3,
            "first_purchase_date": "2000-01-01",
            "latest_sale_purchase_price": 23456.2,
            "latest_purchase_date": "2020-05-05",
            "construction": {
                "loans": 123.1,
                "interest": {
                    "rate_6": 234.2,
                    "rate_14": 345.3,
                },
                "debt_free_purchase_price": 345.3,
                "additional_work": 456.4,
            },
        },
        "improvements": {
            "construction_price_index": [
                {
                    "value": 1234.5,
                    "name": "test-construction-price-1",
                    "completion_date": "2020-01",
                    "depreciation_percentage": 10,
                },
                {
                    "value": 2345.6,
                    "name": "test-construction-price-2",
                    "completion_date": "2023-12",
                    "depreciation_percentage": 2.5,
                },
            ],
            "market_price_index": [
                {
                    "value": 3456.7,
                    "name": "test-market-price-1",
                    "completion_date": "1998-05",
                    "no_deductions": False,
                },
            ],
        },
        "building": {"id": building.uuid.hex},
        "notes": "Lorem ipsum",
    }
    return data


def get_minimal_apartment_data(data):
    return {
        "type": None,
        "state": None,
        "surface_area": None,
        "shares": None,
        "address": {
            "street_address": data["address"]["street_address"],
            "apartment_number": data["address"]["apartment_number"],
            "floor": None,
            "stair": data["address"]["stair"],
        },
        "prices": {
            "first_sale_purchase_price": None,
            "first_sale_share_of_housing_company_loans": None,
            "first_sale_acquisition_price": None,
            "catalog_purchase_price": None,
            "catalog_share_of_housing_company_loans": None,
            "catalog_acquisition_price": None,
            "first_purchase_date": None,
            "latest_sale_purchase_price": None,
            "latest_purchase_date": None,
            "construction": {
                "loans": None,
                "additional_work": None,
                "interest": None,
                "debt_free_purchase_price": None,
            },
        },
        "completion_date": None,
        "notes": None,
        "improvements": {
            "market_price_index": [],
            "construction_price_index": [],
        },
        "rooms": None,
    }


@pytest.mark.parametrize("data_extent", ["full", "nulled", "missing"])
@pytest.mark.django_db
def test__api__apartment__create(api_client: HitasAPIClient, data_extent: str):
    b = BuildingFactory.create()

    data = get_apartment_create_data(b)
    if data_extent == "nulled":
        data.update(get_minimal_apartment_data(data))
    elif data_extent == "missing":
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
    assert len(response.json()["ownerships"]) == 0

    get_response = api_client.get(
        reverse(
            "hitas:apartment-detail",
            args=[b.real_estate.housing_company.uuid.hex, ap.uuid.hex],
        )
    )
    assert response.json() == get_response.json()


@pytest.mark.parametrize("minimal_data", [True, False])
@pytest.mark.django_db
def test__api__apartment__update(api_client: HitasAPIClient, minimal_data: bool):
    b = BuildingFactory.create()

    data = get_apartment_create_data(b)
    post_response = api_client.post(
        reverse(
            "hitas:apartment-list",
            args=[b.real_estate.housing_company.uuid.hex],
        ),
        data=data,
        format="json",
    )
    assert post_response.status_code == status.HTTP_201_CREATED, post_response.json()

    if minimal_data:
        data.update(get_minimal_apartment_data(data))
    response = api_client.put(
        reverse(
            "hitas:apartment-detail",
            args=[b.real_estate.housing_company.uuid.hex, Apartment.objects.first().uuid.hex],
        ),
        data=data,
        format="json",
    )
    res = response.json()

    if not minimal_data:
        assert post_response.json() == res
    else:
        ap = Apartment.objects.first()
        del res["links"]
        assert res == {
            "address": {
                "apartment_number": ap.apartment_number,
                "city": "Helsinki",
                "floor": None,
                "postal_code": ap.postal_code.value,
                "stair": ap.stair,
                "street_address": ap.street_address,
            },
            "completion_date": None,
            "id": ap.uuid.hex,
            "improvements": {
                "construction_price_index": [],
                "market_price_index": [],
            },
            "notes": None,
            "ownerships": [],
            "prices": {
                "first_sale_purchase_price": None,
                "first_sale_share_of_housing_company_loans": None,
                "first_sale_acquisition_price": None,
                "catalog_purchase_price": None,
                "catalog_share_of_housing_company_loans": None,
                "catalog_acquisition_price": None,
                "first_purchase_date": None,
                "latest_sale_purchase_price": None,
                "latest_purchase_date": None,
                "construction": {
                    "additional_work": None,
                    "debt_free_purchase_price": None,
                    "interest": None,
                    "loans": None,
                },
                "maximum_prices": {
                    "confirmed": None,
                    "unconfirmed": {
                        "onwards_2011": {
                            "construction_price_index": {"maximum": False, "value": None},
                            "market_price_index": {"maximum": False, "value": None},
                            "surface_area_price_ceiling": {"maximum": False, "value": None},
                        },
                        "pre_2011": None,
                    },
                },
            },
            "rooms": None,
            "shares": None,
            "state": None,
            "surface_area": None,
            "type": None,
            "conditions_of_sale": [],
            "sell_by_date": None,
        }


@pytest.mark.parametrize(
    **parametrize_helper(
        {
            "type dict not str": InvalidInput(
                invalid_data={"type": "foo"},
                fields=[
                    {"field": "type", "message": "Invalid data. Expected a dictionary, but got str."},
                ],
            ),
            "type dict missing id": InvalidInput(
                invalid_data={"type": {}},
                fields=[
                    {"field": "type.id", "message": "This field is mandatory and cannot be null."},
                ],
            ),
            "type dict id null": InvalidInput(
                invalid_data={"type": {"id": None}},
                fields=[
                    {"field": "type.id", "message": "This field is mandatory and cannot be null."},
                ],
            ),
            "type dict id blank": InvalidInput(
                invalid_data={"type": {"id": ""}},
                fields=[
                    {"field": "type.id", "message": "This field is mandatory and cannot be blank."},
                ],
            ),
            "type dict id not found": InvalidInput(
                invalid_data={"type": {"id": "foo"}},
                fields=[
                    {"field": "type.id", "message": "Object does not exist with given id 'foo'."},
                ],
            ),
            "building dict not str": InvalidInput(
                invalid_data={"building": "foo"},
                fields=[
                    {"field": "building", "message": "Invalid data. Expected a dictionary, but got str."},
                ],
            ),
            "building dict missing id": InvalidInput(
                invalid_data={"building": {}},
                fields=[
                    {"field": "building.id", "message": "This field is mandatory and cannot be null."},
                ],
            ),
            "building dict id null": InvalidInput(
                invalid_data={"building": {"id": None}},
                fields=[
                    {"field": "building.id", "message": "This field is mandatory and cannot be null."},
                ],
            ),
            "building dict id blank": InvalidInput(
                invalid_data={"building": {"id": ""}},
                fields=[
                    {"field": "building.id", "message": "This field is mandatory and cannot be blank."},
                ],
            ),
            "building dict id not found": InvalidInput(
                invalid_data={"building": {"id": "foo"}},
                fields=[
                    {"field": "building.id", "message": "Object does not exist with given id 'foo'."},
                ],
            ),
            "building null": InvalidInput(
                invalid_data={"building": None},
                fields=[
                    {"field": "building", "message": "This field is mandatory and cannot be null."},
                ],
            ),
            "state blank": InvalidInput(
                invalid_data={"state": ""},
                fields=[
                    {"field": "state", "message": "This field is mandatory and cannot be blank."},
                ],
            ),
            "state invalid": InvalidInput(
                invalid_data={"state": "invalid_state"},
                fields=[
                    {
                        "field": "state",
                        "message": (
                            "Unsupported value 'invalid_state'. Supported values are: ['free', 'reserved', 'sold']."
                        ),
                    }
                ],
            ),
            "surface_area not a number": InvalidInput(
                invalid_data={"surface_area": "foo"},
                fields=[
                    {"field": "surface_area", "message": "A valid number is required."},
                ],
            ),
            "surface_area less than 0": InvalidInput(
                invalid_data={"surface_area": -1},
                fields=[
                    {"field": "surface_area", "message": "Ensure this value is greater than or equal to 0."},
                ],
            ),
            "shares start not a number": InvalidInput(
                invalid_data={"shares": {"start": "foo"}},
                fields=[
                    {"field": "shares.start", "message": "A valid integer is required."},
                    {"field": "shares.end", "message": "This field is mandatory and cannot be null."},
                ],
            ),
            "shares end not a number": InvalidInput(
                invalid_data={"shares": {"end": "foo"}},
                fields=[
                    {"field": "shares.start", "message": "This field is mandatory and cannot be null."},
                    {"field": "shares.end", "message": "A valid integer is required."},
                ],
            ),
            "shares end missing": InvalidInput(
                invalid_data={"shares": {"start": 100}},
                fields=[
                    {"field": "shares.end", "message": "This field is mandatory and cannot be null."},
                ],
            ),
            "both shares end and start required": InvalidInput(
                invalid_data={"shares": {"start": None, "end": 100}},
                fields=[
                    {
                        "field": "shares.start",
                        "message": "Both 'shares.start' and 'shares.end' must be given or be 'null'.",
                    },
                    {
                        "field": "shares.end",
                        "message": "Both 'shares.start' and 'shares.end' must be given or be 'null'.",
                    },
                ],
            ),
            "shares end must be greater than shares start": InvalidInput(
                invalid_data={"shares": {"start": 100, "end": 50}},
                fields=[
                    {"field": "shares.start", "message": "'shares.start' must not be greater than 'shares.end'."},
                ],
            ),
            "shares start and end must be greater than 0": InvalidInput(
                invalid_data={"shares": {"start": 0, "end": 0}},
                fields=[
                    {"field": "shares.start", "message": "Ensure this value is greater than or equal to 1."},
                    {"field": "shares.end", "message": "Ensure this value is greater than or equal to 1."},
                ],
            ),
            "address null": InvalidInput(
                invalid_data={"address": None},
                fields=[
                    {"field": "address", "message": "This field is mandatory and cannot be null."},
                ],
            ),
            "address dict items null": InvalidInput(
                invalid_data={
                    "address": {
                        "street_address": None,
                        "apartment_number": None,
                        "stair": None,
                    }
                },
                fields=[
                    {"field": "address.street_address", "message": "This field is mandatory and cannot be null."},
                    {"field": "address.apartment_number", "message": "This field is mandatory and cannot be null."},
                    {"field": "address.stair", "message": "This field is mandatory and cannot be null."},
                ],
            ),
            "address dict items empty": InvalidInput(
                invalid_data={
                    "address": {
                        "street_address": "",
                        "apartment_number": "",
                        "stair": "",
                    }
                },
                fields=[
                    {"field": "address.street_address", "message": "This field is mandatory and cannot be blank."},
                    {"field": "address.apartment_number", "message": "A valid integer is required."},
                    {"field": "address.stair", "message": "This field is mandatory and cannot be blank."},
                ],
            ),
            "apartment number not a number": InvalidInput(
                invalid_data={
                    "address": {
                        "street_address": "test",
                        "apartment_number": "foo",
                        "stair": "1",
                    }
                },
                fields=[
                    {"field": "address.apartment_number", "message": "A valid integer is required."},
                ],
            ),
            "apartment number less than 0": InvalidInput(
                invalid_data={
                    "address": {
                        "street_address": "test",
                        "apartment_number": -1,
                        "stair": "1",
                    }
                },
                fields=[
                    {
                        "field": "address.apartment_number",
                        "message": "Ensure this value is greater than or equal to 0.",
                    }
                ],
            ),
            "construction loan amount less than 0": InvalidInput(
                invalid_data={"prices": {"construction": {"loans": -1}}},
                fields=[
                    {
                        "field": "prices.construction.loans",
                        "message": "Ensure this value is greater than or equal to 0.",
                    }
                ],
            ),
            "construction interest less than 0": InvalidInput(
                invalid_data={"prices": {"construction": {"interest": -1}}},
                fields=[
                    {
                        "field": "prices.construction.interest",
                        "message": "Invalid data. Expected a dictionary, but got int.",
                    },
                ],
            ),
            "construction interest rate 6% less than 0": InvalidInput(
                invalid_data={"prices": {"construction": {"interest": {"rate_6": -1, "rate_14": 1}}}},
                fields=[
                    {
                        "field": "prices.construction.interest.rate_6",
                        "message": "Ensure this value is greater than or equal to 0.",
                    }
                ],
            ),
            "construction interest rate 14% less than 0": InvalidInput(
                invalid_data={"prices": {"construction": {"interest": {"rate_6": 1, "rate_14": -1}}}},
                fields=[
                    {
                        "field": "prices.construction.interest.rate_14",
                        "message": "Ensure this value is greater than or equal to 0.",
                    }
                ],
            ),
            "construction interest rate 6% null": InvalidInput(
                invalid_data={"prices": {"construction": {"interest": {"rate_6": None, "rate_14": 1}}}},
                fields=[
                    {
                        "field": "prices.construction.interest.rate_6",
                        "message": "Both 'rate_6' and 'rate_14' must be given or be 'null'.",
                    },
                    {
                        "field": "prices.construction.interest.rate_14",
                        "message": "Both 'rate_6' and 'rate_14' must be given or be 'null'.",
                    },
                ],
            ),
            "construction interest rate 14% null": InvalidInput(
                invalid_data={"prices": {"construction": {"interest": {"rate_6": 1, "rate_14": None}}}},
                fields=[
                    {
                        "field": "prices.construction.interest.rate_6",
                        "message": "Both 'rate_6' and 'rate_14' must be given or be 'null'.",
                    },
                    {
                        "field": "prices.construction.interest.rate_14",
                        "message": "Both 'rate_6' and 'rate_14' must be given or be 'null'.",
                    },
                ],
            ),
            "construction interest rate 6% greater than 14%": InvalidInput(
                invalid_data={"prices": {"construction": {"interest": {"rate_6": 100, "rate_14": 10}}}},
                fields=[
                    {
                        "field": "prices.construction.interest.rate_6",
                        "message": "'rate_6' must not be greater than 'rate_14'.",
                    },
                ],
            ),
            "construction debt_free_purchase_price less than 0": InvalidInput(
                invalid_data={"prices": {"construction": {"debt_free_purchase_price": -1}}},
                fields=[
                    {
                        "field": "prices.construction.debt_free_purchase_price",
                        "message": "Ensure this value is greater than or equal to 0.",
                    }
                ],
            ),
            "construction additional work less than 0": InvalidInput(
                invalid_data={"prices": {"construction": {"additional_work": -1}}},
                fields=[
                    {
                        "field": "prices.construction.additional_work",
                        "message": "Ensure this value is greater than or equal to 0.",
                    }
                ],
            ),
            "improvements null": InvalidInput(
                invalid_data={"improvements": None},
                fields=[
                    {"field": "improvements", "message": "This field is mandatory and cannot be null."},
                ],
            ),
            "improvements dict empty": InvalidInput(
                invalid_data={"improvements": {}},
                fields=[
                    {
                        "field": "improvements.market_price_index",
                        "message": "This field is mandatory and cannot be null.",
                    },
                    {
                        "field": "improvements.construction_price_index",
                        "message": "This field is mandatory and cannot be null.",
                    },
                ],
            ),
            "market_price_index item empty": InvalidInput(
                invalid_data={
                    "improvements": {
                        "market_price_index": [{}],
                        "construction_price_index": [],
                    }
                },
                fields=[
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
            "market_price_index item data invalid": InvalidInput(
                invalid_data={
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
                fields=[
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
            "construction_price_index item empty": InvalidInput(
                invalid_data={
                    "improvements": {
                        "market_price_index": [],
                        "construction_price_index": [{}],
                    }
                },
                fields=[
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
            "construction_price_index item data invalid": InvalidInput(
                invalid_data={
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
                fields=[
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
        }
    )
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
    b2: Building = BuildingFactory.create()  # Building is in a different housing company
    data = get_apartment_create_data(b1)
    data["building"]["id"] = b2.uuid.hex

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


@pytest.mark.parametrize(
    [
        "start_1",
        "end_1",
        "start_2",
        "end_2",
        "fields",
    ],
    [
        [
            1,  # start_1
            20,  # end_1
            100,  # start_2
            120,  # end_2
            [  # fields
                {"field": "shares.start", "message": "Share 20 has already been taken by foo a 1."},
                {"field": "shares.end", "message": "Share 100 has already been taken by bar b 2."},
            ],
        ],
        [
            1,  # start_1
            21,  # end_1
            99,  # start_2
            120,  # end_2
            [  # fields
                {"field": "shares.start", "message": "Shares 20-21 have already been taken by foo a 1."},
                {"field": "shares.start", "message": "Shares 99-100 have already been taken by bar b 2."},
                {"field": "shares.end", "message": "Shares 20-21 have already been taken by foo a 1."},
                {"field": "shares.end", "message": "Shares 99-100 have already been taken by bar b 2."},
            ],
        ],
        [
            30,  # start_1
            40,  # end_1
            80,  # start_2
            90,  # end_2
            [  # fields
                {"field": "shares.start", "message": "Shares 30-40 have already been taken by foo a 1."},
                {"field": "shares.start", "message": "Shares 80-90 have already been taken by bar b 2."},
                {"field": "shares.end", "message": "Shares 30-40 have already been taken by foo a 1."},
                {"field": "shares.end", "message": "Shares 80-90 have already been taken by bar b 2."},
            ],
        ],
        [
            1,  # start_1
            2,  # end_1
            10,  # start_2
            110,  # end_2
            [  # fields
                {"field": "shares.start", "message": "Shares 20-100 have already been taken by bar b 2."},
                {"field": "shares.end", "message": "Shares 20-100 have already been taken by bar b 2."},
            ],
        ],
        [
            1,  # start_1
            2,  # end_1
            20,  # start_2
            100,  # end_2
            [  # fields
                {"field": "shares.start", "message": "Shares 20-100 have already been taken by bar b 2."},
                {"field": "shares.end", "message": "Shares 20-100 have already been taken by bar b 2."},
            ],
        ],
    ],
    ids=[
        "Single overlapping, start and end are inclusive in both ends",
        "Multiple overlapping, partially outside range from both ends",
        "Multiple overlapping, inside new range from both ends",
        "Multiple overlapping, over new range from both ends",
        "Multiple overlapping, same range",
    ],
)
@pytest.mark.django_db
def test__api__apartment__create__overlapping_shares(
    api_client: HitasAPIClient,
    start_1: int,
    end_1: int,
    start_2: int,
    end_2: int,
    fields: list[dict[str, Any]],
):
    b1: Building = BuildingFactory.create()
    ApartmentFactory.create(
        building=b1,
        street_address="foo",
        stair="a",
        apartment_number=1,
        share_number_start=start_1,
        share_number_end=end_1,
    )
    ApartmentFactory.create(
        building=b1,
        street_address="bar",
        stair="b",
        apartment_number=2,
        share_number_start=start_2,
        share_number_end=end_2,
    )

    data = get_apartment_create_data(b1)

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
        "fields": fields,
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


# Update tests


@pytest.mark.django_db
def test__api__apartment__update__clear_improvements(api_client: HitasAPIClient):
    ap: Apartment = ApartmentFactory.create()
    ApartmentConstructionPriceImprovementFactory.create(apartment=ap)
    ApartmentMarketPriceImprovementFactory.create(apartment=ap)

    data = {
        "state": ApartmentState.SOLD.value,
        "type": {"id": ap.apartment_type.uuid.hex},
        "surface_area": 100,
        "rooms": 2,
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
            "construction": {
                "loans": 44444,
                "interest": {
                    "rate_6": 55555,
                    "rate_14": 88888,
                },
                "debt_free_purchase_price": 66666,
                "additional_work": 77777,
            },
        },
        "notes": "Test Notes",
        "building": {"id": ap.building.uuid.hex},
        "completion_date": None,
        "improvements": {
            "construction_price_index": [],
            "market_price_index": [],
        },
    }

    response = api_client.put(
        reverse(
            "hitas:apartment-detail",
            args=[ap.housing_company.uuid.hex, ap.uuid.hex],
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
    assert ap.loans_during_construction == data["prices"]["construction"]["loans"]
    assert ap.interest_during_construction_6 == data["prices"]["construction"]["interest"]["rate_6"]
    assert ap.interest_during_construction_14 == data["prices"]["construction"]["interest"]["rate_14"]
    assert ap.debt_free_purchase_price_during_construction == data["prices"]["construction"]["debt_free_purchase_price"]
    assert ap.additional_work_during_construction == data["prices"]["construction"]["additional_work"]
    assert ap.notes == data["notes"]
    assert ap.construction_price_improvements.count() == 0
    assert ap.market_price_improvements.count() == 0

    get_response = api_client.get(
        reverse(
            "hitas:apartment-detail",
            args=[ap.housing_company.uuid.hex, ap.uuid.hex],
        )
    )
    assert response.json() == get_response.json()


@pytest.mark.parametrize(
    [
        "start_1",
        "end_1",
        "start_2",
        "end_2",
        "fields",
    ],
    [
        [
            1,  # start_1
            20,  # end_1
            100,  # start_2
            120,  # end_2
            [  # fields
                {"field": "shares.start", "message": "Share 20 has already been taken by foo a 1."},
                {"field": "shares.end", "message": "Share 100 has already been taken by bar b 2."},
            ],
        ],
        [
            1,  # start_1
            21,  # end_1
            99,  # start_2
            120,  # end_2
            [  # fields
                {"field": "shares.start", "message": "Shares 20-21 have already been taken by foo a 1."},
                {"field": "shares.start", "message": "Shares 99-100 have already been taken by bar b 2."},
                {"field": "shares.end", "message": "Shares 20-21 have already been taken by foo a 1."},
                {"field": "shares.end", "message": "Shares 99-100 have already been taken by bar b 2."},
            ],
        ],
        [
            30,  # start_1
            40,  # end_1
            80,  # start_2
            90,  # end_2
            [  # fields
                {"field": "shares.start", "message": "Shares 30-40 have already been taken by foo a 1."},
                {"field": "shares.start", "message": "Shares 80-90 have already been taken by bar b 2."},
                {"field": "shares.end", "message": "Shares 30-40 have already been taken by foo a 1."},
                {"field": "shares.end", "message": "Shares 80-90 have already been taken by bar b 2."},
            ],
        ],
        [
            1,  # start_1
            2,  # end_1
            10,  # start_2
            110,  # end_2
            [  # fields
                {"field": "shares.start", "message": "Shares 20-100 have already been taken by bar b 2."},
                {"field": "shares.end", "message": "Shares 20-100 have already been taken by bar b 2."},
            ],
        ],
        [
            1,  # start_1
            2,  # end_1
            20,  # start_2
            100,  # end_2
            [  # fields
                {"field": "shares.start", "message": "Shares 20-100 have already been taken by bar b 2."},
                {"field": "shares.end", "message": "Shares 20-100 have already been taken by bar b 2."},
            ],
        ],
    ],
    ids=[
        "Single overlapping, start and end are inclusive in both ends",
        "Multiple overlapping, partially outside range from both ends",
        "Multiple overlapping, inside new range from both ends",
        "Multiple overlapping, over new range from both ends",
        "Multiple overlapping, same range",
    ],
)
@pytest.mark.django_db
def test__api__apartment__update__overlapping_shares(
    api_client: HitasAPIClient,
    start_1: int,
    end_1: int,
    start_2: int,
    end_2: int,
    fields: list[dict[str, Any]],
):
    building_1: Building = BuildingFactory.create()
    ApartmentFactory.create(
        building=building_1,
        street_address="foo",
        stair="a",
        apartment_number=1,
        share_number_start=start_1,
        share_number_end=end_1,
    )
    ApartmentFactory.create(
        building=building_1,
        street_address="bar",
        stair="b",
        apartment_number=2,
        share_number_start=start_2,
        share_number_end=end_2,
    )
    apartment_1: Apartment = ApartmentFactory.create(
        building=building_1,
        street_address="baz",
        stair="c",
        apartment_number=3,
        share_number_start=200,
        share_number_end=300,
    )

    data = ApartmentDetailSerializer(apartment_1).data
    del data["id"]
    del data["type"]["value"]
    del data["type"]["description"]
    del data["type"]["code"]
    del data["shares"]["total"]
    del data["address"]["postal_code"]
    del data["address"]["city"]
    del data["links"]
    del data["conditions_of_sale"]
    del data["sell_by_date"]
    del data["ownerships"]
    data["building"] = {"id": building_1.uuid.hex}
    data["shares"]["start"] = 20
    data["shares"]["end"] = 100

    response = api_client.put(
        reverse(
            "hitas:apartment-detail",
            args=[building_1.real_estate.housing_company.uuid.hex, apartment_1.uuid.hex],
        ),
        data=data,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": fields,
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


# Delete tests


@pytest.mark.django_db
def test__api__apartment__delete(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create()

    url = reverse(
        "hitas:apartment-detail",
        args=[
            a.housing_company.uuid.hex,
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

    url = reverse(
        "hitas:apartment-detail",
        args=[
            a.housing_company.uuid.hex,
            a.uuid.hex,
        ],
    )
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()

    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
