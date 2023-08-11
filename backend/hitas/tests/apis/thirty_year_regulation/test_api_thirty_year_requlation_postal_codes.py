import pytest
from _decimal import Decimal
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from rest_framework import status

from hitas.models.external_sales_data import CostAreaData
from hitas.models.housing_company import HitasType
from hitas.services.thirty_year_regulation import (
    combine_sales_data,
    get_external_sales_data,
    get_sales_data,
)
from hitas.tests.apis.helpers import HitasAPIClient, count_queries
from hitas.tests.apis.thirty_year_regulation.utils import (
    create_external_sales_data_for_postal_code,
    create_high_price_sale_for_apartment,
    create_low_price_sale_for_apartment,
    create_new_apartment,
    create_no_external_sales_data,
    get_relevant_dates,
)
from hitas.tests.factories import ApartmentSaleFactory, HitasPostalCodeFactory
from hitas.utils import business_quarter, hitas_calculation_quarter, to_quarter


@pytest.mark.django_db
def test__api__regulation_postal_codes__simple(api_client: HitasAPIClient, freezer):
    this_month, two_months_ago, _ = get_relevant_dates(freezer)

    # Apartment where sales happened in the previous year
    apartment = create_new_apartment(
        postal_code="00001",
        building__real_estate__housing_company__postal_code__cost_area=1,
    )
    create_high_price_sale_for_apartment(apartment)

    # Create necessary external sales data
    create_external_sales_data_for_postal_code(postal_code="00002")

    url = reverse("hitas:thirty-year-regulation-postal-codes-list")

    with count_queries(3):
        response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == [
        {
            "postal_code": "00001",
            "price_by_area": 14_900.0,
            "cost_area": 1,
        },
        {
            "postal_code": "00002",
            "price_by_area": 25_000.0,
            "cost_area": None,
        },
    ]


@pytest.mark.django_db
def test__api__regulation_postal_codes__missing_external_sales_data(api_client: HitasAPIClient, freezer):
    get_relevant_dates(freezer)

    url = reverse("hitas:thirty-year-regulation-postal-codes-list")

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "external_sales_data_not_found",
        "message": "External sales data not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__regulation_postal_codes__wrong_calculation_date(api_client: HitasAPIClient, freezer):
    this_month, two_months_ago, _ = get_relevant_dates(freezer)

    # Create necessary external sales data
    create_external_sales_data_for_postal_code(postal_code="00002")

    url = reverse("hitas:thirty-year-regulation-postal-codes-list") + "?calculation_date=2022-02-01"

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "external_sales_data_not_found",
        "message": "External sales data not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__regulation_postal_codes__complex(api_client: HitasAPIClient, freezer):
    this_month, two_months_ago, _ = get_relevant_dates(freezer)

    # Initialize necessary postal codes with areas
    HitasPostalCodeFactory.create(value="00001", cost_area=1)
    HitasPostalCodeFactory.create(value="00002", cost_area=2)
    HitasPostalCodeFactory.create(value="00003", cost_area=3)
    HitasPostalCodeFactory.create(value="00004", cost_area=4)
    HitasPostalCodeFactory.create(value="00005", cost_area=4)

    # Create base for external sales data
    external_sales_data = create_no_external_sales_data()

    #
    # 00001
    #
    # Apartment sales: (14900) / 1 = 14_900
    # Apartment sales count: 1
    # External sales price: (10_000 * 1 + 21000 * 10) / 11 = 20_000
    # External sales count: 11
    #
    # Combined price: (14_900 * 1 + 20_000 * 11) / (12) = 19_575
    #
    # Normal sale only
    apartment_1 = create_new_apartment(postal_code="00001")
    # Normal sale, which affects the average price per square meter
    create_high_price_sale_for_apartment(apartment_1)  # = 14_900
    # Add external sales data
    external_sales_data.quarter_1["areas"].append(CostAreaData(postal_code="00001", sale_count=1, price=10_000))
    external_sales_data.quarter_2["areas"].append(CostAreaData(postal_code="00001", sale_count=10, price=21_000))

    #
    # 00002
    #
    # Apartment sales: (14900 + 4900) / 2 = 9900
    # Apartment sales count: 2
    # External sales price: (1_000_000 * 1 + 1000 * 500) / 501 = 2994,01197605
    # External sales count: 501
    #
    # Combined price: (9900 * 2 + 2994,01197605 * 501) / (2 + 501) = 3021,47117296 = 3021,47
    #
    # Normal sales and excluded sales, RENTAL HITAS
    apartment_2 = create_new_apartment(postal_code="00002", hitas_type=HitasType.RENTAL_HITAS_I)
    # Normal sales, which affects the average price per square meter
    create_high_price_sale_for_apartment(apartment_2)  # = 14_900
    create_low_price_sale_for_apartment(apartment_2)  # = 4900
    # Sale is excluded, so it won't affect the average price per square meter
    ApartmentSaleFactory.create(
        apartment=apartment_2,
        purchase_date=two_months_ago + relativedelta(days=1),
        purchase_price=1_000_000,
        apartment_share_of_housing_company_loans=999_999,
        exclude_from_statistics=True,
    )
    # Add external sales data
    external_sales_data.quarter_1["areas"].append(CostAreaData(postal_code="00002", sale_count=1, price=1_000_000))
    external_sales_data.quarter_4["areas"].append(CostAreaData(postal_code="00002", sale_count=500, price=1000))

    #
    # 00003
    #
    # Apartment sales price: (14900 + 4900 + 4900 + 4900 + 4900) / 5 = 6900
    # Apartment sales count: 5
    # External sales price: 0
    # External sales count: 0
    #
    # Combined price: (6900 * 5 + 0 * 0) / (5 + 0) = 6900
    #
    # Normal sales and excluded sales, NEW HITAS
    apartment_3 = create_new_apartment(postal_code="00003", hitas_type=HitasType.NEW_HITAS_I)
    # Normal sales, which affects the average price per square meter
    create_high_price_sale_for_apartment(apartment_3)  # = 14_900
    create_low_price_sale_for_apartment(apartment_3)  # = 4900
    create_low_price_sale_for_apartment(apartment_3)  # = 4900
    create_low_price_sale_for_apartment(apartment_3)  # = 4900
    create_low_price_sale_for_apartment(apartment_3)  # = 4900
    # Sale is excluded, so it won't affect the average price per square meter
    ApartmentSaleFactory.create(
        apartment=apartment_3,
        purchase_date=two_months_ago + relativedelta(days=1),
        purchase_price=1_000_000,
        apartment_share_of_housing_company_loans=999_999,
        exclude_from_statistics=True,
    )
    # No external sales data for this postal code
    pass

    #
    # 00004
    #
    # Apartment sales: 0
    # Apartment sales count: 0
    # External sales price: 1234 * 5 / 5 = 1234
    # External sales count: 5
    #
    # Combined price: (0 * 0 + 1234 * 5) / (0 + 5) = 1234
    #
    # Half hitas, sales won't be included in the statistics
    apartment_4 = create_new_apartment(postal_code="00004", hitas_type=HitasType.HALF_HITAS)
    create_low_price_sale_for_apartment(apartment_4)
    # Add external sales data
    external_sales_data.quarter_1["areas"].append(CostAreaData(postal_code="00004", sale_count=5, price=1234))

    #
    # 00005
    #
    # Apartment sales: 0
    # Apartment sales count: 0
    # External sales price: 0
    # External sales count: 0
    #
    # Combined price: (0 * 0 + 0 * 0) / (0 + 0) = 0
    #
    # Housing company is marked excluded from statistics, sales won't be included in the statistics
    apartment_5 = create_new_apartment(
        postal_code="00005",
        building__real_estate__housing_company__exclude_from_statistics=True,
    )
    create_low_price_sale_for_apartment(apartment_5)
    # No external sales data for this postal code
    pass

    external_sales_data.save()
    external_sales_data.refresh_from_db()

    #
    # The below code is step-by-step copy-paste from the ThirtyYearRegulationPostalCodesView
    # To find out if there are any issues with the calculation method we check the results between every step
    #
    calculation_month = hitas_calculation_quarter(this_month)
    this_quarter = business_quarter(calculation_month)
    this_quarter_previous_year = this_quarter - relativedelta(years=1)

    # Get sales data from Hitas sales
    sales_data = get_sales_data(this_quarter_previous_year, this_quarter)
    assert sales_data == {
        "00001": {"2022Q4": {"price": Decimal("14900"), "sale_count": 1}},
        "00002": {"2022Q4": {"price": Decimal("9900"), "sale_count": 2}},
        "00003": {"2022Q4": {"price": Decimal("6900"), "sale_count": 5}},
    }

    # Parse external sales data
    external_sales_data = get_external_sales_data(to_quarter(this_quarter))
    assert external_sales_data == {
        "00001": {
            "2022Q1": {"price": 10000, "sale_count": 1},
            "2022Q2": {"price": 21000, "sale_count": 10},
        },
        "00002": {
            "2022Q1": {"price": 1000000, "sale_count": 1},
            "2022Q4": {"price": 1000, "sale_count": 500},
        },
        "00004": {
            "2022Q1": {"price": 1234, "sale_count": 5},
        },
    }

    # Combine sales hitas and external sales data
    price_by_area = combine_sales_data(sales_data, external_sales_data)
    assert price_by_area == {
        "00001": Decimal("19575.00"),
        "00002": Decimal("3021.47"),
        "00003": Decimal("6900.00"),
        "00004": Decimal("1234.00"),
        # Postal code 00005 is excluded because it's value is 0
    }

    # Confirm the API returns the same results
    url = reverse("hitas:thirty-year-regulation-postal-codes-list")

    with count_queries(3):
        response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == [
        {"postal_code": "00001", "cost_area": 1, "price_by_area": 19_575.0},
        {"postal_code": "00002", "cost_area": 2, "price_by_area": 3021.47},
        {"postal_code": "00003", "cost_area": 3, "price_by_area": 6900.0},
        {"postal_code": "00004", "cost_area": 4, "price_by_area": 1234.0},
        # Postal code 00005 is excluded because it's value is 0
    ]
