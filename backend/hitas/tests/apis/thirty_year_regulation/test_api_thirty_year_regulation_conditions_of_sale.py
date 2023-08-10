import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from hitas.models import ConditionOfSale
from hitas.models.housing_company import RegulationStatus
from hitas.models.owner import Owner
from hitas.services.thirty_year_regulation import RegulationResults
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.apis.thirty_year_regulation.utils import (
    create_low_price_sale_for_apartment,
    create_necessary_indices,
    create_new_apartment,
    create_no_external_sales_data,
    create_thirty_year_old_housing_company,
    get_comparison_data_for_single_housing_company,
    get_relevant_dates,
)
from hitas.tests.factories import ConditionOfSaleFactory, OwnerFactory


@pytest.mark.django_db
def test__api__regulation__conditions_of_sale_fulfilled(api_client: HitasAPIClient, freezer):
    this_month, two_months_ago, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices()

    owner: Owner = OwnerFactory.create()

    # Sale for an old apartment for the owner.
    old_housing_company = create_thirty_year_old_housing_company(
        postal_code="00001",
        sales__ownerships__owner=owner,
    )
    # Sale for a new apartment for the same owner.
    new_apartment = create_new_apartment(
        postal_code="00002",
        sales__ownerships__owner=owner,
    )

    # There is a condition of sale between the apartment that will be released from regulation and the new apartment.
    condition_of_sale: ConditionOfSale = ConditionOfSaleFactory.create(
        new_ownership=new_apartment.sales.first().ownerships.first(),
        old_ownership=owner.ownerships.exclude(sale__apartment=new_apartment).first(),
    )
    assert condition_of_sale.fulfilled is None

    # Apartment where sales happened in the previous year
    apartment = create_new_apartment()

    # Sale in the previous year, which affect the average price per square meter
    # Average sales price will be: (4_000 + 900) / 1 = 4_900
    create_low_price_sale_for_apartment(apartment)

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
                old_housing_company,
                regulation_month,
                current_regulation_status=RegulationStatus.RELEASED_BY_HITAS,
            ),
        ],
        stays_regulated=[],
        skipped=[],
        # The owner is not obfuscated, since they still own the new apartment
        obfuscated_owners=[],
    )

    # When the old apartment is released from regulation, the condition of sale is fulfilled.
    condition_of_sale.refresh_from_db()
    assert condition_of_sale.fulfilled is not None
