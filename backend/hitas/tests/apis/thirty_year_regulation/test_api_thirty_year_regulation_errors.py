from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from hitas.models import Apartment
from hitas.models.housing_company import HitasType, RegulationStatus
from hitas.models.thirty_year_regulation import (
    FullSalesData,
    RegulationResult,
    ThirtyYearRegulationResults,
    ThirtyYearRegulationResultsRow,
)
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.apis.thirty_year_regulation.utils import (
    create_high_price_sale_for_apartment,
    create_necessary_indices,
    create_new_apartment,
    create_no_external_sales_data,
    create_thirty_year_old_housing_company,
    get_relevant_dates,
)
from hitas.tests.factories import ApartmentFactory, ApartmentSaleFactory


@pytest.mark.django_db
def test__api__regulation__fetch_exising__not_available(api_client: HitasAPIClient, freezer):
    get_relevant_dates(freezer)

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
    this_month, _, regulation_month = get_relevant_dates(freezer)

    # Create necessary sale, apartment, and housing company for regulation
    create_thirty_year_old_housing_company()

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

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
    this_month, _, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices()

    # Create necessary sale, apartment, and housing company for regulation
    create_thirty_year_old_housing_company()

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "external_sales_data_not_found",
        "message": "External sales data not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__regulation__surface_area_price_ceiling_missing(api_client: HitasAPIClient, freezer):
    this_month, _, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices(skip_surface_area_price_ceiling=True)

    # Create necessary sale, apartment, and housing company for regulation
    create_thirty_year_old_housing_company()

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

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
    this_month, two_months_ago, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices()

    # Sale for the apartment in a housing company that will be under regulation checking
    # Index adjusted price for the housing company will be: (50_000 + 10_000) / 10 * (200 / 100) = 12_000
    create_thirty_year_old_housing_company()

    # Apartment where sales happened in the previous year, but it is on another postal code
    apartment = create_new_apartment(postal_code="00002")

    # Sale in the previous year
    create_high_price_sale_for_apartment(apartment)

    create_no_external_sales_data()

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
    this_month, _, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices()

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

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

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
    this_month, _, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices()

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

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

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
    this_month, _, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices()

    # Sale for the apartment in a housing company that will be under regulation checking
    # Since there is no total surface area for the housing company, validation will fail
    sale = ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=None,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

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
    this_month, _, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices()

    # Sale for the apartment in a housing company that will be under regulation checking
    # Since there is no total surface area for the housing company,
    # an error will be raised when trying to make index adjustments
    sale = ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=0,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

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
    this_month, _, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices()

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

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

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
    this_month, _, regulation_month = get_relevant_dates(freezer)

    # Sale in a housing company that already has regulation data
    old_housing_company = create_thirty_year_old_housing_company()

    results = ThirtyYearRegulationResults.objects.create(
        calculation_month=this_month,
        regulation_month=regulation_month,
        surface_area_price_ceiling=Decimal("5000"),
        sales_data=FullSalesData(internal={}, external={}, price_by_area={}),
        replacement_postal_codes=[],
    )
    ThirtyYearRegulationResultsRow.objects.create(
        parent=results,
        housing_company=old_housing_company,
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

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": "unique",
        "message": "Previous regulation exists. Cannot re-check regulation for this quarter.",
        "reason": "Conflict",
        "status": 409,
    }
