import datetime

import pytest
from django.urls import reverse
from rest_framework import status

from hitas.models import Apartment
from hitas.models.housing_company import HitasType
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories.apartment import (
    ApartmentFactory,
)
from hitas.tests.factories.indices import (
    ConstructionPriceIndex2005Equal100Factory,
    MarketPriceIndex2005Equal100Factory,
    SurfaceAreaPriceCeilingFactory,
)


@pytest.mark.django_db
def test__api__apartment_unconfirmed_max_price__retrieve_for_date(api_client: HitasAPIClient):
    apartment: Apartment = ApartmentFactory(
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        completion_date=datetime.date(2021, 1, 1),
        additional_work_during_construction=10000,
        surface_area=100,
        sales__purchase_price=100000,
        sales__apartment_share_of_housing_company_loans=10000,
    )

    this_month = datetime.date.today().replace(day=1)
    past_month = datetime.date(2021, 5, 1)
    completion_month = apartment.completion_date.replace(day=1)

    # Completion month indices
    ConstructionPriceIndex2005Equal100Factory.create(month=completion_month, value=100)
    MarketPriceIndex2005Equal100Factory.create(month=completion_month, value=200)
    # Past month indices
    ConstructionPriceIndex2005Equal100Factory.create(month=past_month, value=150)
    MarketPriceIndex2005Equal100Factory.create(month=past_month, value=250)
    SurfaceAreaPriceCeilingFactory.create(month=past_month, value=3000)
    # Current month indices (should not be used in calculation)
    ConstructionPriceIndex2005Equal100Factory.create(month=this_month, value=200)
    MarketPriceIndex2005Equal100Factory.create(month=this_month, value=300)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=4000)

    # Results found
    response = api_client.get(
        reverse(
            "hitas:apartment-retrieve-unconfirmed-prices-for-date",
            args=[apartment.housing_company.uuid.hex, apartment.uuid.hex],
        )
        + f"?request_date={past_month.isoformat()}"
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "construction_price_index": {"maximum": False, "value": 180000.0},
        "market_price_index": {"maximum": False, "value": 150000.0},
        "surface_area_price_ceiling": {"maximum": True, "value": 300000.0},
    }
