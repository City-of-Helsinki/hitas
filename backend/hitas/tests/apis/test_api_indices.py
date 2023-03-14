import datetime
from itertools import product

import pytest
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from rest_framework import status

from hitas.models import ApartmentSale, HousingCompanyState
from hitas.models.indices import (
    CalculationData,
    HousingCompanyData,
    SurfaceAreaPriceCeilingCalculationData,
    SurfaceAreaPriceCeilingResult,
)
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import ApartmentSaleFactory
from hitas.tests.factories.indices import (
    ConstructionPriceIndex2005Equal100Factory,
    ConstructionPriceIndexFactory,
    MarketPriceIndex2005Equal100Factory,
    MarketPriceIndexFactory,
    MaximumPriceIndexFactory,
    SurfaceAreaPriceCeilingFactory,
)

indices = [
    "maximum-price-index",
    "market-price-index",
    "market-price-index-2005-equal-100",
    "construction-price-index",
    "construction-price-index-2005-equal-100",
    "surface-area-price-ceiling",
]

factories = [
    MaximumPriceIndexFactory,
    MarketPriceIndexFactory,
    MarketPriceIndex2005Equal100Factory,
    ConstructionPriceIndexFactory,
    ConstructionPriceIndex2005Equal100Factory,
    SurfaceAreaPriceCeilingFactory,
]

# List tests


@pytest.mark.parametrize("index", indices)
@pytest.mark.django_db
def test__api__indices__list__empty(api_client: HitasAPIClient, index):
    response = api_client.get(reverse(f"hitas:{index}-list"))
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


@pytest.mark.parametrize("index,factory", zip(indices, factories))
@pytest.mark.django_db
def test__api__indices__list(api_client: HitasAPIClient, index, factory):
    factory.create(month=datetime.date(2022, 1, 1), value=127.48)
    factory.create(month=datetime.date(1999, 12, 1), value=256)

    response = api_client.get(reverse(f"hitas:{index:}-list"))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "contents": [
            {"month": "2022-01", "value": 127.48},
            {"month": "1999-12", "value": 256},
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


@pytest.mark.parametrize("index,factory", zip(indices, factories))
@pytest.mark.django_db
def test__api__indices__list__filter_by_year(api_client: HitasAPIClient, index, factory):
    factory.create(month=datetime.date(2021, 12, 1), value=256)
    factory.create(month=datetime.date(2022, 1, 1), value=127.48)
    factory.create(month=datetime.date(2022, 12, 1), value=150.0)
    factory.create(month=datetime.date(2023, 1, 1), value=256)

    response = api_client.get(reverse(f"hitas:{index:}-list") + "?year=2022")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "contents": [
            {"month": "2022-12", "value": 150.0},
            {"month": "2022-01", "value": 127.48},
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


@pytest.mark.parametrize(
    "index,test",
    product(
        indices,
        [
            {
                "year": "1969",
                "field": {
                    "field": "year",
                    "message": "Ensure this value is greater than or equal to 1970.",
                },
            },
            {
                "year": "2100",
                "field": {
                    "field": "year",
                    "message": "Ensure this value is less than or equal to 2099.",
                },
            },
        ],
    ),
)
@pytest.mark.django_db
def test__api__indices__list__filter_by_year__invalid(api_client: HitasAPIClient, index, test):
    response = api_client.get(reverse(f"hitas:{index:}-list") + "?year=" + test["year"], openapi_validate_request=False)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [test["field"]],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


# Create


@pytest.mark.parametrize("index", indices[:-1])
@pytest.mark.django_db
def test__api__indices__create(api_client: HitasAPIClient, index):
    response = api_client.post(reverse(f"hitas:{index}-list"), data={}, openapi_validate=False)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED, response.json()
    assert response.json() == {
        "error": "method_not_allowed",
        "message": "Method not allowed",
        "reason": "Method Not Allowed",
        "status": 405,
    }


# Create (SurfaceAreaPriceCeiling)


@pytest.mark.django_db
def test__api__indices__create__surface_area_price_ceiling__empty(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    url = reverse("hitas:surface-area-price-ceiling-list")
    data = {}

    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": "missing",
        "message": "No housing companies completed before '2023-02-01' or all have wrong state.",
        "reason": "Conflict",
        "status": 409,
    }


@pytest.mark.django_db
def test__api__indices__create__surface_area_price_ceiling__wrong_state(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    completion_month = this_month - relativedelta(years=1)

    # Housing companies in these states should not be included in surface area price ceiling calculation
    for state in [
        HousingCompanyState.GREATER_THAN_30_YEARS_FREE,
        HousingCompanyState.GREATER_THAN_30_YEARS_PLOT_DEPARTMENT_NOTIFICATION,
        HousingCompanyState.HALF_HITAS,
        HousingCompanyState.READY_NO_STATISTICS,
    ]:
        ApartmentSaleFactory.create(
            purchase_date=completion_month,
            purchase_price=50_000,
            apartment_share_of_housing_company_loans=10_000,
            apartment__surface_area=10,
            apartment__completion_date=completion_month,
            apartment__building__real_estate__housing_company__state=state,
        )

    url = reverse("hitas:surface-area-price-ceiling-list")
    data = {}

    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": "missing",
        "message": "No housing companies completed before '2023-02-01' or all have wrong state.",
        "reason": "Conflict",
        "status": 409,
    }


@pytest.mark.django_db
def test__api__indices__create__surface_area_price_ceiling__single(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    completion_month = this_month - relativedelta(years=1)

    # Create necessary indices
    MarketPriceIndex2005Equal100Factory.create(month=completion_month, value=100)
    MarketPriceIndex2005Equal100Factory.create(month=this_month, value=200)

    # Sale in a finished housing company.
    # Index adjusted price for the housing company will be: (50_000 + 10_000) / 10 * (200 / 100) = 12_000
    sale: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=completion_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=completion_month,
        apartment__building__real_estate__housing_company__state=HousingCompanyState.LESS_THAN_30_YEARS,
    )

    url = reverse("hitas:surface-area-price-ceiling-list")
    data = {}

    response = api_client.post(url, data=data, format="json")

    #
    # Since there is only one housing company, the new surface area price ceiling will be
    # that housing company's average price per square meter.
    #
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == [
        SurfaceAreaPriceCeilingResult(month="2023-02", value=12_000.0),
        SurfaceAreaPriceCeilingResult(month="2023-03", value=12_000.0),
        SurfaceAreaPriceCeilingResult(month="2023-04", value=12_000.0),
    ]

    calc_data = list(SurfaceAreaPriceCeilingCalculationData.objects.all())
    assert len(calc_data) == 1
    assert calc_data[0].calculation_month == this_month
    assert calc_data[0].data == CalculationData(
        housing_company_data=[
            HousingCompanyData(
                name=sale.apartment.housing_company.display_name,
                completion_date=completion_month.isoformat(),
                surface_area=float(sale.apartment.surface_area),
                realized_acquisition_price=60_000.0,
                unadjusted_average_price_per_square_meter=6_000.0,
                adjusted_average_price_per_square_meter=12_000.0,
                completion_month_index=100.0,
                calculation_month_index=200.0,
            ),
        ],
        created_surface_area_price_ceilings=[
            SurfaceAreaPriceCeilingResult(month="2023-02", value=12_000.0),
            SurfaceAreaPriceCeilingResult(month="2023-03", value=12_000.0),
            SurfaceAreaPriceCeilingResult(month="2023-04", value=12_000.0),
        ],
    )


@pytest.mark.django_db
def test__api__indices__create__surface_area_price_ceiling__multiple(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    completion_month = this_month - relativedelta(years=1)

    # Create necessary indices
    MarketPriceIndex2005Equal100Factory.create(month=completion_month, value=100)
    MarketPriceIndex2005Equal100Factory.create(month=this_month, value=200)

    # Sale in a finished housing company.
    # Index adjusted price for the housing company will be: (50_000 + 10_000) / 10 * (200 / 100) = 12_000
    sale_1: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=completion_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=completion_month,
        apartment__building__real_estate__housing_company__state=HousingCompanyState.LESS_THAN_30_YEARS,
    )

    # Sale in another finished housing company.
    # Index adjusted price for the housing company will be: (30_000 + 10_000) / 25 * (200 / 100) = 3_200
    sale_2: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=completion_month,
        purchase_price=30_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=25,
        apartment__completion_date=completion_month,
        apartment__building__real_estate__housing_company__state=HousingCompanyState.LESS_THAN_30_YEARS,
    )

    url = reverse("hitas:surface-area-price-ceiling-list")
    data = {}

    response = api_client.post(url, data=data, format="json")

    #
    # The surface area price ceiling will be the average of the two housing companies average price per square meter:
    # (12_000 + 3_200) / 2 = 7600
    #
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == [
        SurfaceAreaPriceCeilingResult(month="2023-02", value=7_600.0),
        SurfaceAreaPriceCeilingResult(month="2023-03", value=7_600.0),
        SurfaceAreaPriceCeilingResult(month="2023-04", value=7_600.0),
    ]

    calc_data = list(SurfaceAreaPriceCeilingCalculationData.objects.all())
    assert len(calc_data) == 1
    assert calc_data[0].calculation_month == this_month
    assert calc_data[0].data == CalculationData(
        housing_company_data=[
            HousingCompanyData(
                name=sale_1.apartment.housing_company.display_name,
                completion_date=completion_month.isoformat(),
                surface_area=float(sale_1.apartment.surface_area),
                realized_acquisition_price=60_000.0,
                unadjusted_average_price_per_square_meter=6_000.0,
                adjusted_average_price_per_square_meter=12_000.0,
                completion_month_index=100.0,
                calculation_month_index=200.0,
            ),
            HousingCompanyData(
                name=sale_2.apartment.housing_company.display_name,
                completion_date=completion_month.isoformat(),
                surface_area=float(sale_2.apartment.surface_area),
                realized_acquisition_price=40_000.0,
                unadjusted_average_price_per_square_meter=1_600.0,
                adjusted_average_price_per_square_meter=3_200.0,
                completion_month_index=100.0,
                calculation_month_index=200.0,
            ),
        ],
        created_surface_area_price_ceilings=[
            SurfaceAreaPriceCeilingResult(month="2023-02", value=7_600.0),
            SurfaceAreaPriceCeilingResult(month="2023-03", value=7_600.0),
            SurfaceAreaPriceCeilingResult(month="2023-04", value=7_600.0),
        ],
    )


@pytest.mark.django_db
def test__api__indices__create__surface_area_price_ceiling__missing_indices(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    completion_month = this_month - relativedelta(years=1)

    # Sale in a finished housing company, but indices are missing
    ApartmentSaleFactory.create(
        purchase_date=completion_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=completion_month,
        apartment__building__real_estate__housing_company__state=HousingCompanyState.LESS_THAN_30_YEARS,
    )

    url = reverse("hitas:surface-area-price-ceiling-list")
    data = {}

    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": "missing_values",
        "fields": [
            {
                "field": "non_field_errors",
                "message": "Post 2011 market price indices missing for months: '2022-02', '2023-02'.",
            }
        ],
        "message": "Missing required indices",
        "reason": "Conflict",
        "status": 409,
    }


# Read


@pytest.mark.parametrize("index,factory", zip(indices, factories))
@pytest.mark.django_db
def test__api__indices__retrieve(api_client: HitasAPIClient, index, factory):
    factory.create(month=datetime.date(2022, 1, 1), value=127.48)

    response = api_client.get(reverse(f"hitas:{index}-detail", kwargs={"month": "2022-01"}))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "month": "2022-01",
        "value": 127.48,
    }


@pytest.mark.parametrize("index", indices)
@pytest.mark.django_db
def test__api__indices__retrieve__unexisting_valid_month(api_client: HitasAPIClient, index):
    response = api_client.get(reverse(f"hitas:{index}-detail", kwargs={"month": "2022-01"}))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "month": "2022-01",
        "value": None,
    }


@pytest.mark.parametrize("index,month", product(indices, ["foo", "", "0-1", "2022-1", "2022-13", "2022-00"]))
@pytest.mark.django_db
def test__api__indices__retrieve__invalid_month(api_client: HitasAPIClient, index, month):
    response = api_client.get(reverse(f"hitas:{index}-detail", kwargs={"month": "foo"}), openapi_validate_request=False)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "month",
                "message": "Field has to be a valid month in format 'yyyy-mm'.",
            }
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


# Update


@pytest.mark.parametrize(
    "index_and_factory,create,value", product(zip(indices, factories), [True, False], [None, 1, 1.12])
)
@pytest.mark.django_db
def test__api__indices__update(api_client: HitasAPIClient, index_and_factory, create, value):
    index, factory = index_and_factory[0], index_and_factory[1]

    if create:
        factory.create(month=datetime.date(2022, 1, 1), value=127.48)

    response = api_client.put(
        reverse(f"hitas:{index}-detail", kwargs={"month": "2022-01"}), data={"value": value}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "month": "2022-01",
        "value": value,
    }

    # Fetch and recheck
    response = api_client.get(reverse(f"hitas:{index}-detail", kwargs={"month": "2022-01"}))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "month": "2022-01",
        "value": value,
    }


@pytest.mark.parametrize("index,factory", zip(indices, factories))
@pytest.mark.django_db
def test__api__indices__update__too_many_decimal_points(api_client: HitasAPIClient, index, factory):
    factory.create(month=datetime.date(2022, 1, 1), value=127.48)

    response = api_client.put(
        reverse(f"hitas:{index}-detail", kwargs={"month": "2022-01"}), data={"value": 987.654}, format="json"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "value",
                "message": "Ensure that there are no more than 2 decimal places.",
            }
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.parametrize("index,factory", zip(indices, factories))
@pytest.mark.django_db
def test__api__indices__update__zero_value(api_client: HitasAPIClient, index, factory):
    factory.create(month=datetime.date(2022, 1, 1), value=123)

    response = api_client.put(
        reverse(f"hitas:{index}-detail", kwargs={"month": "2022-01"}), data={"value": 0}, format="json"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "value",
                "message": "Ensure this value is greater than or equal to 1.",
            }
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


# Delete


@pytest.mark.parametrize("index", indices)
@pytest.mark.django_db
def test__api__indices__delete(api_client: HitasAPIClient, index):
    response = api_client.delete(reverse(f"hitas:{index}-detail", kwargs={"month": "2022-01"}), openapi_validate=False)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert response.json() == {
        "error": "method_not_allowed",
        "message": "Method not allowed",
        "reason": "Method Not Allowed",
        "status": 405,
    }
