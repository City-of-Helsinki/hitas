import datetime

import pytest
from dateutil import relativedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from hitas.models import Apartment
from hitas.models.housing_company import HitasType
from hitas.tests.apis.apartment_max_price.utils import create_necessary_indices
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import (
    ApartmentFactory,
    HousingCompanyMarketPriceImprovementFactory,
)
from hitas.tests.factories.indices import (
    ConstructionPriceIndex2005Equal100Factory,
    MarketPriceIndex2005Equal100Factory,
    SurfaceAreaPriceCeilingFactory,
)
from hitas.utils import monthify, this_month


@pytest.mark.parametrize(
    "data,fields",
    [
        (
            {"calculation_date": "foo"},
            [
                {
                    "field": "calculation_date",
                    "message": "Date has wrong format. Use one of these formats instead: YYYY-MM-DD.",
                }
            ],
        ),
        (
            {"calculation_date": "-1"},
            [
                {
                    "field": "calculation_date",
                    "message": "Date has wrong format. Use one of these formats instead: YYYY-MM-DD.",
                }
            ],
        ),
        (
            {"calculation_date": timezone.now().date() + relativedelta.relativedelta(days=1)},
            [{"field": "calculation_date", "message": "Field has to be less than or equal to current date."}],
        ),
        (
            {"apartment_share_of_housing_company_loans": "foo"},
            [{"field": "apartment_share_of_housing_company_loans", "message": "A valid integer is required."}],
        ),
        (
            {"apartment_share_of_housing_company_loans": "-1"},
            [
                {
                    "field": "apartment_share_of_housing_company_loans",
                    "message": "Ensure this value is greater than or equal to 0.",
                }
            ],
        ),
        (
            {"apartment_share_of_housing_company_loans_date": "foo"},
            [
                {
                    "field": "apartment_share_of_housing_company_loans_date",
                    "message": "Date has wrong format. Use one of these formats instead: YYYY-MM-DD.",
                }
            ],
        ),
    ],
)
@pytest.mark.django_db
def test__api__apartment_max_price__invalid_params(api_client: HitasAPIClient, data, fields):
    a: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )

    response = api_client.post(
        reverse("hitas:maximum-price-list", args=[a.housing_company.uuid.hex, a.uuid.hex]),
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


@pytest.mark.parametrize(
    "missing_index,error_msg",
    [
        ("cpi_completion_date", "cpi2005eq100.2014-08"),
        ("mpi_completion_date", "mpi2005eq100.2014-08"),
        ("cpi_calculation_date", "cpi2005eq100.2022-07"),
        ("mpi_calculation_date", "mpi2005eq100.2022-07"),
        ("sapc", "sapc.2022-07"),
        ("improvement_mpi", "mpi2005eq100.2020-05"),
        ("improvement_cpi", "cpi2005eq100.2020-05"),
    ],
)
@pytest.mark.django_db
def test__api__apartment_max_price__missing_index(api_client: HitasAPIClient, missing_index: str, error_msg: str):
    calculation_date = datetime.date(2022, 7, 5)
    apartment_completion_date = datetime.date(2014, 8, 27)
    improvement_completion_date = datetime.date(2020, 5, 21)

    apartment: Apartment = ApartmentFactory.create(
        completion_date=apartment_completion_date,
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    # Construction price improvement is not used since this is a new hitas apartment (copied from MPI-improvements)
    HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=apartment.housing_company,
        value=150000,
        completion_date=improvement_completion_date,
    )

    # Create necessary apartment's completion date indices
    if missing_index != "cpi_completion_date":
        ConstructionPriceIndex2005Equal100Factory.create(month=monthify(apartment_completion_date), value=129.29)
    if missing_index != "mpi_completion_date":
        MarketPriceIndex2005Equal100Factory.create(month=monthify(apartment_completion_date), value=167.9)
    if missing_index != "cpi_calculation_date":
        ConstructionPriceIndex2005Equal100Factory.create(month=monthify(calculation_date), value=146.4)
    if missing_index != "mpi_calculation_date":
        MarketPriceIndex2005Equal100Factory.create(month=monthify(calculation_date), value=189.1)
    if missing_index != "sapc":
        SurfaceAreaPriceCeilingFactory.create(month=monthify(calculation_date), value=4869)
    if missing_index != "improvement_mpi":
        MarketPriceIndex2005Equal100Factory.create(month=monthify(improvement_completion_date), value=171.0)
    if missing_index != "improvement_cpi":
        ConstructionPriceIndex2005Equal100Factory.create(month=monthify(improvement_completion_date), value=171.0)

    data = {
        "calculation_date": calculation_date.isoformat(),
    }

    url = reverse(
        "hitas:maximum-price-list",
        kwargs={
            "housing_company_uuid": apartment.housing_company.uuid.hex,
            "apartment_uuid": apartment.uuid.hex,
        },
    )
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": error_msg,
        "message": "One or more indices required for max price calculation is missing.",
        "reason": "Conflict",
        "status": 409,
    }


@pytest.mark.django_db
def test__api__apartment_max_price__too_high_loan(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2011, 1, 1),
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )

    create_necessary_indices(completion_month=monthify(a.completion_date), calculation_month=this_month())

    data = {
        "calculation_date": this_month(),
        "apartment_share_of_housing_company_loans": 9999999999,
    }

    response = api_client.post(
        reverse("hitas:maximum-price-list", args=[a.housing_company.uuid.hex, a.uuid.hex]), data=data, format="json"
    )
    assert response.status_code == status.HTTP_409_CONFLICT, response.json()

    assert response.json() == {
        "error": "max_price_lte_zero",
        "message": "Maximum price calculation could not be completed. "
        "Calculated maximum price is less than or equal to zero",
        "reason": "Conflict",
        "status": 409,
    }


@pytest.mark.parametrize("date", ["", None])
@pytest.mark.django_db
def test__api__apartment_max_price__missing_date(api_client: HitasAPIClient, date):
    a: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2011, 1, 1),
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    create_necessary_indices(completion_month=monthify(a.completion_date), calculation_month=this_month())

    data = {
        "apartment_share_of_housing_company_loans_date": date,
        "calculation_date": date,
    }

    response = api_client.post(
        reverse("hitas:maximum-price-list", args=[a.housing_company.uuid.hex, a.uuid.hex]), data=data, format="json"
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
