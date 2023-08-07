import datetime
from decimal import Decimal

import pytest
from dateutil.relativedelta import relativedelta
from rest_framework import status
from rest_framework.reverse import reverse

from hitas.models import Apartment, ApartmentSale, ExternalSalesData
from hitas.models.external_sales_data import QuarterData
from hitas.models.housing_company import HitasType, RegulationStatus
from hitas.models.thirty_year_regulation import (
    FullSalesData,
    RegulationResult,
    ThirtyYearRegulationResults,
    ThirtyYearRegulationResultsRow,
)
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import ApartmentFactory, ApartmentSaleFactory
from hitas.tests.factories.indices import MarketPriceIndexFactory, SurfaceAreaPriceCeilingFactory
from hitas.utils import to_quarter


@pytest.mark.django_db
def test__api__regulation__fetch_exising__not_available(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "thirty_year_regulation_results_not_found",
        "message": "Thirty Year Regulation Results not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__regulation__indices_missing(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    regulation_month = this_month - relativedelta(years=30)

    # Create necessary sale, apartment, and housing company for regulation
    ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": "missing_values",
        "fields": [
            {
                "field": "non_field_errors",
                "message": "Pre 2011 market price indices missing for months: '1993-02', '2023-02'.",
            },
        ],
        "message": "Missing required indices",
        "reason": "Conflict",
        "status": 409,
    }


@pytest.mark.django_db
def test__api__regulation__external_sales_data_missing(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    regulation_month = this_month - relativedelta(years=30)

    # Create necessary sale, apartment, and housing company for regulation
    ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )

    # Create necessary indices
    MarketPriceIndexFactory.create(month=regulation_month, value=100)
    MarketPriceIndexFactory.create(month=this_month, value=200)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=5000)

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "external_sales_data_not_found",
        "message": "External sales data not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__regulation__surface_area_price_ceiling_missing(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    regulation_month = this_month - relativedelta(years=30)

    # Create necessary sale, apartment, and housing company for regulation
    ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )

    MarketPriceIndexFactory.create(month=regulation_month, value=100)
    MarketPriceIndexFactory.create(month=this_month, value=200)

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "surface_area_price_ceiling_not_found",
        "message": "Surface area price ceiling not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__regulation__no_sales_data_for_postal_code__use_replacements__one_missing_price(
    api_client: HitasAPIClient,
    freezer,
):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    previous_year_last_month = this_month - relativedelta(months=2)
    regulation_month = this_month - relativedelta(years=30)

    # Create necessary indices
    MarketPriceIndexFactory.create(month=regulation_month, value=100)
    MarketPriceIndexFactory.create(month=this_month, value=200)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=5000)

    # Sale for the apartment in a housing company that will be under regulation checking
    # Index adjusted price for the housing company will be: (50_000 + 10_000) / 10 * (200 / 100) = 12_000
    ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )

    # Apartment where sales happened in the previous year, but it is on another postal code
    apartment: Apartment = ApartmentFactory.create(
        completion_date=previous_year_last_month,
        building__real_estate__housing_company__postal_code__value="00002",
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sales__purchase_date=previous_year_last_month,  # first sale, not counted
    )

    # Sale in the previous year
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=40_000,
        apartment_share_of_housing_company_loans=9_000,
    )

    # Create necessary external sales data (no external sales)
    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(this_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=3)), areas=[]),
        quarter_4=QuarterData(quarter=to_quarter(previous_year_last_month), areas=[]),
    )

    url = reverse("hitas:thirty-year-regulation-list")

    data = {
        "replacement_postal_codes": [
            {
                "postal_code": "00001",
                "replacements": ["00002", "00003"],
            },
        ],
    }

    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": "missing",
        "message": "Missing price data for replacement postal codes: ['00003'].",
        "reason": "Conflict",
        "status": 409,
    }


@pytest.mark.django_db
def test__api__regulation__no_catalog_prices_or_sales(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    regulation_month = this_month - relativedelta(years=30)

    # Create necessary indices
    MarketPriceIndexFactory.create(month=regulation_month, value=100)
    MarketPriceIndexFactory.create(month=this_month, value=200)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=5000)

    # Apartment in a housing company that will be under regulation checking
    # Since there are no sales or catalog prices, validation will fail
    apartment: Apartment = ApartmentFactory.create(
        catalog_purchase_price=None,
        catalog_primary_loan_amount=None,
        surface_area=10,
        completion_date=regulation_month,
        building__real_estate__housing_company__postal_code__value="00001",
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sales=[],
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": "missing_values",
        "fields": [
            {
                "field": "non_field_errors",
                "message": (
                    f"Average price per square meter could not be calculated for "
                    f"'{apartment.housing_company.display_name}': "
                    f"Apartment '{apartment.address}' does not have any sales or sales catalog prices."
                ),
            },
        ],
        "message": "Missing apartment details",
        "reason": "Conflict",
        "status": 409,
    }


@pytest.mark.django_db
def test__api__regulation__catalog_price_zero(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    regulation_month = this_month - relativedelta(years=30)

    # Create necessary indices
    MarketPriceIndexFactory.create(month=regulation_month, value=100)
    MarketPriceIndexFactory.create(month=this_month, value=200)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=5000)

    # Apartment in a housing company that will be under regulation checking
    # Since there are no sales or catalog prices, an error will be raised when trying to make index adjustments
    apartment: Apartment = ApartmentFactory.create(
        catalog_purchase_price=0,
        catalog_primary_loan_amount=0,
        surface_area=10,
        completion_date=regulation_month,
        building__real_estate__housing_company__postal_code__value="00001",
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sales=[],
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "non_field_errors",
                "message": (
                    f"Average price per square meter zero or missing for these housing companies: "
                    f"'{apartment.housing_company.display_name}'. Index adjustments cannot be made."
                ),
            },
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__regulation__no_surface_area(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    regulation_month = this_month - relativedelta(years=30)

    # Create necessary indices
    MarketPriceIndexFactory.create(month=regulation_month, value=100)
    MarketPriceIndexFactory.create(month=this_month, value=200)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=5000)

    # Sale for the apartment in a housing company that will be under regulation checking
    # Since there is no total surface area for the housing company, validation will fail
    sale: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=None,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": "missing_values",
        "fields": [
            {
                "field": "non_field_errors",
                "message": (
                    f"Average price per square meter could not be calculated for "
                    f"'{sale.apartment.housing_company.display_name}': "
                    f"Apartment '{sale.apartment.address}' does not have surface area set."
                ),
            },
        ],
        "message": "Missing apartment details",
        "reason": "Conflict",
        "status": 409,
    }


@pytest.mark.django_db
def test__api__regulation__surface_area_zero(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    regulation_month = this_month - relativedelta(years=30)

    # Create necessary indices
    MarketPriceIndexFactory.create(month=regulation_month, value=100)
    MarketPriceIndexFactory.create(month=this_month, value=200)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=5000)

    # Sale for the apartment in a housing company that will be under regulation checking
    # Since there is no total surface area for the housing company,
    # an error will be raised when trying to make index adjustments
    sale: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=0,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "non_field_errors",
                "message": (
                    f"Average price per square meter zero or missing for these housing companies: "
                    f"'{sale.apartment.housing_company.display_name}'. Index adjustments cannot be made."
                ),
            },
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__regulation__no_catalog_prices_or_sales_or_surface_area(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    regulation_month = this_month - relativedelta(years=30)

    # Create necessary indices
    MarketPriceIndexFactory.create(month=regulation_month, value=100)
    MarketPriceIndexFactory.create(month=this_month, value=200)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=5000)

    # Apartment in a housing company that will be under regulation checking
    # Since there are no sales or catalog prices, validation will fail
    apartment: Apartment = ApartmentFactory.create(
        catalog_purchase_price=None,
        catalog_primary_loan_amount=None,
        surface_area=None,
        completion_date=regulation_month,
        building__real_estate__housing_company__postal_code__value="00001",
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sales=[],
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": "missing_values",
        "fields": [
            {
                "field": "non_field_errors",
                "message": (
                    f"Average price per square meter could not be calculated for "
                    f"'{apartment.housing_company.display_name}': "
                    f"Apartment '{apartment.address}' does not have any "
                    f"sales or sales catalog prices or surface area set."
                ),
            },
        ],
        "message": "Missing apartment details",
        "reason": "Conflict",
        "status": 409,
    }


@pytest.mark.django_db
def test__api__regulation__regulation_already_made(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    regulation_month = this_month - relativedelta(years=30)

    # Sale in a housing company that already has regulation data
    sale: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )

    results = ThirtyYearRegulationResults.objects.create(
        calculation_month=this_month,
        regulation_month=regulation_month,
        surface_area_price_ceiling=Decimal("5000"),
        sales_data=FullSalesData(internal={}, external={}, price_by_area={}),
        replacement_postal_codes=[],
    )
    ThirtyYearRegulationResultsRow.objects.create(
        parent=results,
        housing_company=sale.apartment.housing_company,
        completion_date=regulation_month,
        surface_area=10,
        postal_code="00001",
        realized_acquisition_price=Decimal("60000.0"),
        unadjusted_average_price_per_square_meter=Decimal("6000.0"),
        adjusted_average_price_per_square_meter=Decimal("12000.0"),
        completion_month_index=Decimal("100"),
        calculation_month_index=Decimal("200"),
        regulation_result=RegulationResult.STAYS_REGULATED,
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": "unique",
        "message": "Previous regulation exists. Cannot re-check regulation for this quarter.",
        "reason": "Conflict",
        "status": 409,
    }
