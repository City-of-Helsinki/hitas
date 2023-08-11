import pytest
from dateutil.relativedelta import relativedelta
from rest_framework import status
from rest_framework.reverse import reverse

from hitas.services.thirty_year_regulation import RegulationResults
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.apis.thirty_year_regulation.utils import (
    create_high_price_sale_for_apartment,
    create_necessary_indices,
    create_new_apartment,
    create_no_external_sales_data,
    create_thirty_year_old_housing_company,
    get_comparison_data_for_single_housing_company,
    get_relevant_dates,
)
from hitas.tests.factories import ApartmentSaleFactory


@pytest.mark.django_db
def test__api__regulation__exclude_from_statistics__housing_company(api_client: HitasAPIClient, freezer):
    this_month, two_months_ago, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices()

    old_housing_company = create_thirty_year_old_housing_company()

    # Apartment where sales happened in the previous year, but it is in a housing company that should not be
    # included in statistics, so its sales do not affect postal code average square price calculation
    apartment = create_new_apartment(building__real_estate__housing_company__exclude_from_statistics=True)

    # Sale in the previous year
    create_high_price_sale_for_apartment(apartment)

    create_no_external_sales_data()

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

    #
    # Since postal code average square price does not exist, the housing company cannot be regulated,
    # and thus is not in either of the lists.
    #
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == RegulationResults(
        automatically_released=[],
        released_from_regulation=[],
        stays_regulated=[],
        skipped=[
            get_comparison_data_for_single_housing_company(
                old_housing_company,
                regulation_month,
            )
        ],
        obfuscated_owners=[],
    )


@pytest.mark.django_db
def test__api__regulation__exclude_from_statistics__sale__all(api_client: HitasAPIClient, freezer):
    this_month, two_months_ago, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices()

    old_housing_company = create_thirty_year_old_housing_company()

    # Apartment where sales happened in the previous year
    apartment = create_new_apartment()

    # Sale in the previous year, but it is excluded from statistics
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=two_months_ago + relativedelta(days=1),
        purchase_price=40_000,
        exclude_from_statistics=True,
        apartment_share_of_housing_company_loans=9_000,
    )

    create_no_external_sales_data()

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

    #
    # Since postal code average square price does not exist, the housing company cannot be regulated,
    # and thus is not in either of the lists.
    #
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == RegulationResults(
        automatically_released=[],
        released_from_regulation=[],
        stays_regulated=[],
        skipped=[
            get_comparison_data_for_single_housing_company(
                old_housing_company,
                regulation_month,
            )
        ],
        obfuscated_owners=[],
    )


@pytest.mark.django_db
def test__api__regulation__exclude_from_statistics__sale__partial(api_client: HitasAPIClient, freezer):
    this_month, two_months_ago, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices()

    old_housing_company = create_thirty_year_old_housing_company()

    # Apartment where sales happened in the previous year
    apartment = create_new_apartment()

    # This sale will not affect the average price per square meter since it is excluded from statistics
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=two_months_ago + relativedelta(days=1),
        purchase_price=1_000_000,
        apartment_share_of_housing_company_loans=999_999,
        exclude_from_statistics=True,
    )
    # This sale does affect the average price per square meter, since it is not excluded from statistics
    create_high_price_sale_for_apartment(apartment)

    create_no_external_sales_data()

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

    #
    # The housing company's index adjusted acquisition price/m² is 12_000.
    # The housing company's surface area price ceiling is 5_000.
    # Since the index adjusted acquisition price/m² is higher than the SAPC, it will be used in the comparison
    #
    # The average sales price/m² for the postal code in the last year is 14_900.
    # Since it's higher than the housing company's compared value (12_000), the housing company stays regulated.
    #
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == RegulationResults(
        automatically_released=[],
        released_from_regulation=[],
        stays_regulated=[
            get_comparison_data_for_single_housing_company(
                old_housing_company,
                regulation_month,
            )
        ],
        skipped=[],
        obfuscated_owners=[],
    )
