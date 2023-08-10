import pytest
from dateutil.relativedelta import relativedelta
from rest_framework import status
from rest_framework.reverse import reverse

from hitas.models.housing_company import HitasType, RegulationStatus
from hitas.models.owner import Owner, OwnerT
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
def test__api__regulation__owner_still_owns_half_hitas_apartment(api_client: HitasAPIClient, freezer):
    this_month, two_months_ago, regulation_month = get_relevant_dates(freezer)
    less_than_two_years_ago = this_month - relativedelta(years=2) + relativedelta(days=1)

    create_necessary_indices()

    sale = create_apartment_sale_for_date(regulation_month)

    owner: Owner = sale.ownerships.first().owner

    # Sale in a half-hitas apartment for the same owner.
    ApartmentSaleFactory.create(
        purchase_date=less_than_two_years_ago,
        exclude_from_statistics=True,
        apartment__completion_date=less_than_two_years_ago,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HALF_HITAS,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.RELEASED_BY_HITAS,
        ownerships__owner=owner,
    )

    # Apartment where sales happened in the previous year
    apartment = create_new_apartment()

    # Sale in the previous year, which affect the average price per square meter
    # Average sales price will be: (4_000 + 900) / 1 = 4_900
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=two_months_ago + relativedelta(days=1),
        purchase_price=4_000,
        apartment_share_of_housing_company_loans=900,
    )

    create_no_external_sales_data()

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

    #
    # Since the housing company's index adjusted acquisition price is 12_000, which is higher than the
    # surface area price ceiling of 5_000, the acquisition price will be used in the comparison.
    #
    # Since the average sales price per square meter for the area in the last year (4_900) is lower than the
    # housing company's compared value (in this case the index adjusted acquisition price of 12_000),
    # the company is released from regulation.
    #
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == RegulationResults(
        automatically_released=[],
        released_from_regulation=[
            get_comparison_data_for_single_housing_company(
                sale.apartment.housing_company,
                regulation_month,
                current_regulation_status=RegulationStatus.RELEASED_BY_HITAS,
            ),
        ],
        stays_regulated=[],
        skipped=[],
        # Owner is not obfuscated since it has not been
        # two years from the sale of the owner's half-hitas apartment.
        obfuscated_owners=[],
    )

    #
    # Check that the housing company was freed from regulation
    #
    sale.apartment.housing_company.refresh_from_db()
    assert sale.apartment.housing_company.regulation_status == RegulationStatus.RELEASED_BY_HITAS


@pytest.mark.django_db
def test__api__regulation__owner_still_owns_half_hitas_apartment__over_2_years(api_client: HitasAPIClient, freezer):
    this_month, two_months_ago, regulation_month = get_relevant_dates(freezer)
    two_years_ago = this_month - relativedelta(years=2)

    create_necessary_indices()

    sale = create_apartment_sale_for_date(regulation_month)

    owner: Owner = sale.ownerships.first().owner

    # Sale in a half-hitas apartment for the same owner.
    ApartmentSaleFactory.create(
        purchase_date=two_years_ago,
        exclude_from_statistics=True,
        apartment__completion_date=two_years_ago,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HALF_HITAS,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.RELEASED_BY_HITAS,
        ownerships__owner=owner,
    )

    # Apartment where sales happened in the previous year
    apartment = create_new_apartment()

    # Sale in the previous year, which affect the average price per square meter
    # Average sales price will be: (4_000 + 900) / 1 = 4_900
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=two_months_ago + relativedelta(days=1),
        purchase_price=4_000,
        apartment_share_of_housing_company_loans=900,
    )

    create_no_external_sales_data()

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

    #
    # Since the housing company's index adjusted acquisition price is 12_000, which is higher than the
    # surface area price ceiling of 5_000, the acquisition price will be used in the comparison.
    #
    # Since the average sales price per square meter for the area in the last year (4_900) is lower than the
    # housing company's compared value (in this case the index adjusted acquisition price of 12_000),
    # the company is released from regulation.
    #
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == RegulationResults(
        automatically_released=[],
        released_from_regulation=[
            get_comparison_data_for_single_housing_company(
                sale.apartment.housing_company,
                regulation_month,
                current_regulation_status=RegulationStatus.RELEASED_BY_HITAS,
            ),
        ],
        stays_regulated=[],
        skipped=[],
        obfuscated_owners=[
            OwnerT(
                name=owner.name,
                identifier=owner.identifier,
                email=owner.email,
            ),
        ],
    )

    #
    # Check that the housing company was freed from regulation
    #
    sale.apartment.housing_company.refresh_from_db()
    assert sale.apartment.housing_company.regulation_status == RegulationStatus.RELEASED_BY_HITAS
