import pytest
from dateutil.relativedelta import relativedelta
from rest_framework import status
from rest_framework.reverse import reverse

from hitas.services.thirty_year_regulation import RegulationResults
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.apis.thirty_year_regulation.utils import (
    create_apartment_sale_for_date,
    create_necessary_indices,
    create_new_apartment,
    create_no_external_sales_data,
    get_comparison_data_for_single_housing_company,
    get_relevant_dates,
)
from hitas.tests.factories import ApartmentSaleFactory


@pytest.mark.django_db
def test__api__regulation__exclude_from_statistics__housing_company(api_client: HitasAPIClient, freezer):
    this_month, previous_year_last_month, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices(this_month, regulation_month)

    sale = create_apartment_sale_for_date(regulation_month)

    # Apartment where sales happened in the previous year, but it is in a housing company that should not be
    # included in statistics, so its sales do not affect postal code average square price calculation
    apartment = create_new_apartment(
        previous_year_last_month,
        building__real_estate__housing_company__exclude_from_statistics=True,
    )

    # Sale in the previous year
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=40_000,
        apartment_share_of_housing_company_loans=9_000,
    )

    create_no_external_sales_data(this_month, previous_year_last_month)

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
                sale.apartment.housing_company,
                regulation_month,
            )
        ],
        obfuscated_owners=[],
    )


@pytest.mark.django_db
def test__api__regulation__exclude_from_statistics__sale__all(api_client: HitasAPIClient, freezer):
    this_month, previous_year_last_month, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices(this_month, regulation_month)

    sale = create_apartment_sale_for_date(regulation_month)

    # Apartment where sales happened in the previous year
    apartment = create_new_apartment(previous_year_last_month)

    # Sale in the previous year, but it is excluded from statistics
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=40_000,
        exclude_from_statistics=True,
        apartment_share_of_housing_company_loans=9_000,
    )

    create_no_external_sales_data(this_month, previous_year_last_month)

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
                sale.apartment.housing_company,
                regulation_month,
            )
        ],
        obfuscated_owners=[],
    )


@pytest.mark.django_db
def test__api__regulation__exclude_from_statistics__sale__partial(api_client: HitasAPIClient, freezer):
    this_month, previous_year_last_month, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices(this_month, regulation_month)

    sale = create_apartment_sale_for_date(regulation_month)

    # Apartment where sales happened in the previous year
    apartment = create_new_apartment(previous_year_last_month)

    # Sale in the previous year, which affect the average price per square meter
    # This sale will not affect the average price per square meter since it is excluded from statistics
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=100_000,
        exclude_from_statistics=True,
        apartment_share_of_housing_company_loans=99_999,
    )
    # This sale does affect the average price per square meter, since it is excluded from statistics
    # Average sales price will be: (40_000 + 9_000) / 1 = 49_000
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=2),
        purchase_price=40_000,
        exclude_from_statistics=False,  # being explicit here
        apartment_share_of_housing_company_loans=9_000,
    )

    create_no_external_sales_data(this_month, previous_year_last_month)

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

    #
    # Since the housing company's index adjusted acquisition price is 12_000, which is higher than the
    # surface area price ceiling of 5_000, the acquisition price will be used in the comparison.
    #
    # Since the average sales price per square meter for the area in the last year (49_000) is higher than the
    # housing company's compared value (in this case the index adjusted acquisition price of 12_000),
    # the company stays regulated.
    #
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == RegulationResults(
        automatically_released=[],
        released_from_regulation=[],
        stays_regulated=[
            get_comparison_data_for_single_housing_company(
                sale.apartment.housing_company,
                regulation_month,
            )
        ],
        skipped=[],
        obfuscated_owners=[],
    )
