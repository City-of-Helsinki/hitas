import datetime
from decimal import Decimal
from typing import NamedTuple

import pytest
from dateutil.relativedelta import relativedelta
from rest_framework import status
from rest_framework.reverse import reverse

from hitas.models import Apartment
from hitas.models.external_sales_data import SaleData
from hitas.models.housing_company import HitasType, RegulationStatus
from hitas.models.owner import Owner, OwnerT
from hitas.models.thirty_year_regulation import (
    FullSalesData,
    RegulationResult,
    ThirtyYearRegulationResults,
    ThirtyYearRegulationResultsRow,
)
from hitas.services.thirty_year_regulation import RegulationResults
from hitas.tests.apis.helpers import HitasAPIClient, parametrize_helper
from hitas.tests.apis.thirty_year_regulation.utils import (
    create_apartment_sale_for_date,
    create_external_sales_data_for_postal_code,
    create_necessary_indices,
    create_new_apartment,
    create_no_external_sales_data,
    get_comparison_data_for_single_housing_company,
    get_relevant_dates,
)
from hitas.tests.factories import ApartmentFactory, ApartmentSaleFactory
from hitas.tests.factories.indices import SurfaceAreaPriceCeilingFactory

# Read regulation results


@pytest.mark.django_db
def test__api__regulation__fetch_exising(api_client: HitasAPIClient, freezer):
    this_month, _, regulation_month = get_relevant_dates(freezer)

    # Sale in a housing company that already has regulation data
    sale = ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=(
            RegulationStatus.RELEASED_BY_PLOT_DEPARTMENT
        ),
    )

    results = ThirtyYearRegulationResults.objects.create(
        calculation_month=this_month,
        regulation_month=regulation_month,
        surface_area_price_ceiling=Decimal("5000"),
        sales_data=FullSalesData(internal={}, external={}, price_by_area={}),
        replacement_postal_codes=[],
    )
    row = ThirtyYearRegulationResultsRow.objects.create(
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
        letter_fetched=True,
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == RegulationResults(
        automatically_released=[],
        released_from_regulation=[],
        stays_regulated=[
            get_comparison_data_for_single_housing_company(
                sale.apartment.housing_company,
                regulation_month,
                price=row.adjusted_average_price_per_square_meter,
                current_regulation_status=RegulationStatus.RELEASED_BY_PLOT_DEPARTMENT,
                letter_fetched=True,
            ),
        ],
        skipped=[],
        obfuscated_owners=[],
    )


# Perform regulation


@pytest.mark.django_db
def test__api__regulation__empty(api_client: HitasAPIClient, freezer):
    get_relevant_dates(freezer)

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == RegulationResults(
        automatically_released=[],
        released_from_regulation=[],
        stays_regulated=[],
        skipped=[],
        obfuscated_owners=[],
    )


class RegulationTestArgs(NamedTuple):
    current_date: datetime.date


@pytest.mark.parametrize(
    **parametrize_helper(
        {
            "Companies stay regulated with correct conditions": RegulationTestArgs(
                current_date=datetime.date(2023, 1, 1),
            ),
            # Calculation is made on the last day of the hitas calculation period.
            # It should still work just the same as if it was the first day of the period.
            "Regulation can be run even on the last date of the period": RegulationTestArgs(
                current_date=datetime.datetime(2023, 4, 30),
            ),
        }
    )
)
@pytest.mark.django_db
def test__api__regulation__stays_regulated(api_client: HitasAPIClient, freezer, current_date):
    this_month, previous_year_last_month, regulation_month = get_relevant_dates(freezer)

    freezer.move_to(current_date)

    create_necessary_indices(this_month, regulation_month)

    sale = create_apartment_sale_for_date(regulation_month)

    # Apartment where sales happened in the previous year
    apartment = create_new_apartment(previous_year_last_month)

    # Sale in the previous year, which affect the average price per square meter
    # Average sales price will be: (40_000 + 9_000) / 1 = 49_000
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=40_000,
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

    #
    # Check that the housing company stays regulated
    #
    sale.apartment.housing_company.refresh_from_db()
    assert sale.apartment.housing_company.regulation_status == RegulationStatus.REGULATED

    #
    # Check that the regulation results were saved
    #
    regulation_results = list(ThirtyYearRegulationResults.objects.all())
    assert len(regulation_results) == 1
    assert regulation_results[0].regulation_month == regulation_month
    assert regulation_results[0].calculation_month == this_month
    assert regulation_results[0].surface_area_price_ceiling == Decimal("5000.0")
    assert regulation_results[0].sales_data == FullSalesData(
        internal={"00001": {"2022Q4": SaleData(sale_count=1, price=49_000)}},
        external={},
        price_by_area={"00001": 49_000},
    )
    assert regulation_results[0].replacement_postal_codes == []

    result_rows = list(regulation_results[0].rows.all())
    assert len(result_rows) == 1
    assert result_rows[0].housing_company == sale.apartment.housing_company
    assert result_rows[0].completion_date == regulation_month
    assert result_rows[0].surface_area == Decimal("10")
    assert result_rows[0].realized_acquisition_price == Decimal("60000.0")
    assert result_rows[0].unadjusted_average_price_per_square_meter == Decimal("6000.0")
    assert result_rows[0].adjusted_average_price_per_square_meter == Decimal("12000.0")
    assert result_rows[0].completion_month_index == Decimal("100")
    assert result_rows[0].calculation_month_index == Decimal("200")
    assert result_rows[0].regulation_result == RegulationResult.STAYS_REGULATED


@pytest.mark.django_db
def test__api__regulation__released_from_regulation(api_client: HitasAPIClient, freezer):
    this_month, previous_year_last_month, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices(this_month, regulation_month)

    sale = create_apartment_sale_for_date(regulation_month)

    owner: Owner = sale.ownerships.first().owner

    # Apartment where sales happened in the previous year
    apartment = create_new_apartment(previous_year_last_month)

    # Sale in the previous year, which affect the average price per square meter
    # Average sales price will be: (4_000 + 900) / 1 = 4_900
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=4_000,
        apartment_share_of_housing_company_loans=900,
    )

    create_no_external_sales_data(this_month, previous_year_last_month)

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

    #
    # Check that the regulation results were saved
    #
    regulation_results = list(ThirtyYearRegulationResults.objects.all())
    assert len(regulation_results) == 1
    assert regulation_results[0].regulation_month == regulation_month
    assert regulation_results[0].calculation_month == this_month
    assert regulation_results[0].surface_area_price_ceiling == Decimal("5000.0")
    assert regulation_results[0].sales_data == FullSalesData(
        internal={"00001": {"2022Q4": SaleData(sale_count=1, price=4_900)}},
        external={},
        price_by_area={"00001": 4_900},
    )
    assert regulation_results[0].replacement_postal_codes == []

    result_rows = list(regulation_results[0].rows.all())
    assert len(result_rows) == 1
    assert result_rows[0].housing_company == sale.apartment.housing_company
    assert result_rows[0].completion_date == regulation_month
    assert result_rows[0].surface_area == Decimal("10")
    assert result_rows[0].realized_acquisition_price == Decimal("60000.0")
    assert result_rows[0].unadjusted_average_price_per_square_meter == Decimal("6000.0")
    assert result_rows[0].adjusted_average_price_per_square_meter == Decimal("12000.0")
    assert result_rows[0].completion_month_index == Decimal("100")
    assert result_rows[0].calculation_month_index == Decimal("200")
    assert result_rows[0].regulation_result == RegulationResult.RELEASED_FROM_REGULATION


@pytest.mark.django_db
def test__api__regulation__comparison_is_equal(api_client: HitasAPIClient, freezer):
    this_month, previous_year_last_month, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices(this_month, regulation_month)

    sale = create_apartment_sale_for_date(regulation_month)

    owner: Owner = sale.ownerships.first().owner

    # Apartment where sales happened in the previous year
    apartment = create_new_apartment(previous_year_last_month)

    # Sale in the previous year, which affect the average price per square meter
    # Average sales price will be: (10_000 + 2_000) / 1 = 12_000
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=10_000,
        apartment_share_of_housing_company_loans=2_000,
    )

    create_no_external_sales_data(this_month, previous_year_last_month)

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

    #
    # Since the housing company's index adjusted acquisition price is 12_000, which is higher than the
    # surface area price ceiling of 5_000, the acquisition price will be used in the comparison.
    #
    # Since the average sales price per square meter for the area in the last year (12_000) is equal to the
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


@pytest.mark.django_db
def test__api__regulation__automatically_release__all(api_client: HitasAPIClient, freezer):
    this_month, previous_year_last_month, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices(this_month, regulation_month)

    # Create necessary sale, apartment, and housing company for regulation
    # This housing company will be automatically released, since it is not using the old hitas ruleset
    sale = create_apartment_sale_for_date(regulation_month, hitas_type=HitasType.NEW_HITAS_I)

    owner: Owner = sale.ownerships.first().owner

    create_no_external_sales_data(this_month, previous_year_last_month)

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == RegulationResults(
        automatically_released=[
            get_comparison_data_for_single_housing_company(
                sale.apartment.housing_company,
                regulation_month,
                price="0",
                current_regulation_status=RegulationStatus.RELEASED_BY_HITAS,
            ),
        ],
        released_from_regulation=[],
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

    #
    # Check that the regulation results were saved
    #
    regulation_results = list(ThirtyYearRegulationResults.objects.all())
    assert len(regulation_results) == 1
    assert regulation_results[0].regulation_month == regulation_month
    assert regulation_results[0].calculation_month == this_month
    assert regulation_results[0].surface_area_price_ceiling is None
    assert regulation_results[0].sales_data == FullSalesData(internal={}, external={}, price_by_area={})
    assert regulation_results[0].replacement_postal_codes == []

    result_rows = list(regulation_results[0].rows.all())
    assert len(result_rows) == 1
    assert result_rows[0].housing_company == sale.apartment.housing_company
    assert result_rows[0].completion_date == regulation_month
    assert result_rows[0].surface_area == Decimal("10")
    assert result_rows[0].realized_acquisition_price == Decimal("60000.0")
    assert result_rows[0].unadjusted_average_price_per_square_meter == Decimal("6000.0")
    assert result_rows[0].adjusted_average_price_per_square_meter is None
    assert result_rows[0].completion_month_index is None
    assert result_rows[0].calculation_month_index is None
    assert result_rows[0].regulation_result == RegulationResult.AUTOMATICALLY_RELEASED


@pytest.mark.django_db
def test__api__regulation__automatically_release__partial(api_client: HitasAPIClient, freezer):
    this_month, previous_year_last_month, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices(this_month, regulation_month)

    # Sales for the apartment in a housing company that will be under regulation checking
    # This housing company will be automatically released, since it is not using the old hitas ruleset
    sale_1 = create_apartment_sale_for_date(regulation_month, hitas_type=HitasType.NEW_HITAS_I)
    # This housing company will be checked, since it is using the old hitas ruleset
    sale_2 = create_apartment_sale_for_date(regulation_month)

    owner_1: Owner = sale_1.ownerships.first().owner
    owner_2: Owner = sale_2.ownerships.first().owner

    # Apartment where sales happened in the previous year
    apartment = create_new_apartment(previous_year_last_month)

    # Sale in the previous year, which affect the average price per square meter
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=4_000,
        apartment_share_of_housing_company_loans=900,
    )

    create_no_external_sales_data(this_month, previous_year_last_month)

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == RegulationResults(
        automatically_released=[
            get_comparison_data_for_single_housing_company(
                sale_1.apartment.housing_company,
                regulation_month,
                price="0",
                current_regulation_status=RegulationStatus.RELEASED_BY_HITAS,
            ),
        ],
        released_from_regulation=[
            get_comparison_data_for_single_housing_company(
                sale_2.apartment.housing_company,
                regulation_month,
                current_regulation_status=RegulationStatus.RELEASED_BY_HITAS,
            ),
        ],
        stays_regulated=[],
        skipped=[],
        obfuscated_owners=[
            OwnerT(
                name=owner_1.name,
                identifier=owner_1.identifier,
                email=owner_1.email,
            ),
            OwnerT(
                name=owner_2.name,
                identifier=owner_2.identifier,
                email=owner_2.email,
            ),
        ],
    )

    #
    # Check that the first housing companies were freed from regulation
    #
    sale_1.apartment.housing_company.refresh_from_db()
    assert sale_1.apartment.housing_company.regulation_status == RegulationStatus.RELEASED_BY_HITAS

    sale_2.apartment.housing_company.refresh_from_db()
    assert sale_2.apartment.housing_company.regulation_status == RegulationStatus.RELEASED_BY_HITAS


@pytest.mark.django_db
def test__api__regulation__surface_area_price_ceiling_is_used_in_comparison(api_client: HitasAPIClient, freezer):
    this_month, previous_year_last_month, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices(this_month, regulation_month, skip_surface_area_price_ceiling=True)

    # Surface area price will be higher than the housing company index adjusted price
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=50_000)

    sale = create_apartment_sale_for_date(regulation_month)

    owner: Owner = sale.ownerships.first().owner

    # Apartment where sales happened in the previous year
    apartment = create_new_apartment(previous_year_last_month)

    # Sale in the previous year, which affect the average price per square meter
    # Average sales price will be: (40_000 + 9_000) / 1 = 49_000
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=40_000,
        apartment_share_of_housing_company_loans=9_000,
    )

    create_no_external_sales_data(this_month, previous_year_last_month)

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

    #
    # Since the housing company's index adjusted acquisition price is 12_000, which is lower than the
    # surface area price ceiling of 50_000, the surface area price ceiling will be used in the comparison.
    #
    # Since the average sales price per square meter for the area in the last year (49_000) is lower than the
    # housing company's compared value (in this case the index surface area price ceiling of 50_000),
    # the company is released from regulation.
    #
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == RegulationResults(
        automatically_released=[],
        released_from_regulation=[
            get_comparison_data_for_single_housing_company(
                sale.apartment.housing_company,
                regulation_month,
                price="50000.0",
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


@pytest.mark.django_db
def test__api__regulation__only_external_sales_data(api_client: HitasAPIClient, freezer):
    this_month, previous_year_last_month, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices(this_month, regulation_month)

    sale = create_apartment_sale_for_date(regulation_month)

    # Create necessary external sales data
    create_external_sales_data_for_postal_code(this_month, previous_year_last_month, postal_code="00001")

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

    #
    # Since the housing company's index adjusted acquisition price is 12_000, which is higher than the
    # surface area price ceiling of 5_000, the acquisition price will be used in the comparison.
    #
    # Since the average sales price per square meter for the area in the last year (15_000) is higher than the
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


@pytest.mark.django_db
def test__api__regulation__both_hitas_and_external_sales_data(api_client: HitasAPIClient, freezer):
    this_month, previous_year_last_month, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices(this_month, regulation_month)

    sale = create_apartment_sale_for_date(regulation_month)

    # Apartment where sales happened in the previous year
    apartment = create_new_apartment(previous_year_last_month)

    # Sale in the previous year, which affect the average price per square meter
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=40_000,
        apartment_share_of_housing_company_loans=9_000,
    )
    # Create necessary external sales data
    create_external_sales_data_for_postal_code(this_month, previous_year_last_month, postal_code="00001")

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

    #
    # Since the housing company's index adjusted acquisition price is 12_000, which is higher than the
    # surface area price ceiling of 5_000, the acquisition price will be used in the comparison.
    #
    # Average sales price will be calculated based on both hitas and external sales:
    # -> (15_000 + 30_000 + (40_000 + 9_000)) / (1 + 2 + 1) = 23_500
    #
    # Since the average sales price per square meter for the area in the last year (23_500) is higher than the
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


@pytest.mark.django_db
def test__api__regulation__use_catalog_prices(api_client: HitasAPIClient, freezer):
    this_month, previous_year_last_month, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices(this_month, regulation_month)

    # Apartment in a housing company that will be under regulation checking
    # Apartment has no sales, so catalog prices will be used.
    # Index adjusted price for the housing company will be: (50_000 + 10_000) / 10 * (200 / 100) = 12_000
    apartment_1: Apartment = ApartmentFactory.create(
        catalog_purchase_price=50_000,
        catalog_primary_loan_amount=10_000,
        surface_area=10,
        completion_date=regulation_month,
        building__real_estate__housing_company__postal_code__value="00001",
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sales=[],
    )

    # Apartment where sales happened in the previous year
    apartment_2 = create_new_apartment(previous_year_last_month)

    # Sale in the previous year, which affect the average price per square meter
    # Average sales price will be: (40_000 + 9_000) / 1 = 49_000
    ApartmentSaleFactory.create(
        apartment=apartment_2,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=40_000,
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
                apartment_1.housing_company,
                regulation_month,
            ),
        ],
        skipped=[],
        obfuscated_owners=[],
    )


@pytest.mark.django_db
def test__api__regulation__no_housing_company_over_30_years(api_client: HitasAPIClient, freezer):
    this_month, previous_year_last_month, _ = get_relevant_dates(freezer)

    # Apartment where sales happened in the previous year
    apartment = create_new_apartment(previous_year_last_month)

    # Sale in the previous year, which would be used in comparison, but there are no housing companies to check
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=40_000,
        apartment_share_of_housing_company_loans=9_000,
    )

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == RegulationResults(
        automatically_released=[],
        released_from_regulation=[],
        stays_regulated=[],
        skipped=[],
        obfuscated_owners=[],
    )


@pytest.mark.parametrize(
    ["regulation_status", "is_compared"],
    [
        [RegulationStatus.REGULATED, True],
        [RegulationStatus.RELEASED_BY_HITAS, False],
        [RegulationStatus.RELEASED_BY_PLOT_DEPARTMENT, False],
    ],
)
@pytest.mark.django_db
def test__api__regulation__housing_company_regulation_status(
    api_client: HitasAPIClient,
    regulation_status: RegulationStatus,
    is_compared: bool,
    freezer,
):
    this_month, previous_year_last_month, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices(this_month, regulation_month)

    # Sale for the apartment in a housing company whose state is under test
    sale = ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=regulation_status,
    )

    # Apartment where sales happened in the previous year
    apartment = create_new_apartment(previous_year_last_month)

    # Sale in the previous year, which might be used in comparison if there are housing companies to check
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=40_000,
        apartment_share_of_housing_company_loans=9_000,
    )

    create_no_external_sales_data(this_month, previous_year_last_month)

    response = api_client.post(reverse("hitas:thirty-year-regulation-list"), data={}, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()

    if is_compared:
        assert response.json() == RegulationResults(
            automatically_released=[],
            released_from_regulation=[],
            stays_regulated=[
                get_comparison_data_for_single_housing_company(
                    sale.apartment.housing_company,
                    regulation_month,
                ),
            ],
            skipped=[],
            obfuscated_owners=[],
        )
    else:
        assert response.json() == RegulationResults(
            automatically_released=[],
            released_from_regulation=[],
            stays_regulated=[],
            skipped=[],
            obfuscated_owners=[],
        )
