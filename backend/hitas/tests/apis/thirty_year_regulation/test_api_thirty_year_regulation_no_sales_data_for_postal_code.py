from decimal import Decimal

import pytest
from dateutil.relativedelta import relativedelta
from rest_framework import status
from rest_framework.reverse import reverse

from hitas.models import Apartment, ApartmentSale
from hitas.models.external_sales_data import SaleData
from hitas.models.housing_company import HitasType, RegulationStatus
from hitas.models.thirty_year_regulation import (
    FullSalesData,
    RegulationResult,
    ReplacementPostalCodesWithPrice,
    ThirtyYearRegulationResults,
)
from hitas.services.thirty_year_regulation import AddressInfo, ComparisonData, PropertyManagerInfo, RegulationResults
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.apis.thirty_year_regulation.utils import (
    create_necessary_indices,
    create_no_external_sales_data,
    get_relevant_dates,
)
from hitas.tests.factories import ApartmentFactory, ApartmentSaleFactory


@pytest.mark.django_db
def test__api__regulation__no_sales_data_for_postal_code(api_client: HitasAPIClient, freezer):
    this_month, previous_year_last_month, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices(this_month, regulation_month)

    # Sale for the apartment in a housing company that will be under regulation checking
    # Index adjusted price for the housing company will be: (50_000 + 10_000) / 10 * (200 / 100) = 12_000
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
            ComparisonData(
                id=sale.apartment.housing_company.uuid.hex,
                display_name=sale.apartment.housing_company.display_name,
                address=AddressInfo(
                    street_address=sale.apartment.housing_company.street_address,
                    postal_code=sale.apartment.housing_company.postal_code.value,
                    city=sale.apartment.housing_company.postal_code.city,
                ),
                price=Decimal("12000.0"),
                old_ruleset=sale.apartment.housing_company.hitas_type.old_hitas_ruleset,
                completion_date=regulation_month.isoformat(),
                property_manager=PropertyManagerInfo(
                    id=sale.apartment.housing_company.property_manager.uuid.hex,
                    name=sale.apartment.housing_company.property_manager.name,
                    email=sale.apartment.housing_company.property_manager.email,
                    last_modified=this_month.isoformat(),
                ),
                letter_fetched=False,
                current_regulation_status=RegulationStatus.REGULATED.value,
            )
        ],
        obfuscated_owners=[],
    )


@pytest.mark.django_db
def test__api__regulation__no_sales_data_for_postal_code__use_replacements(api_client: HitasAPIClient, freezer):
    this_month, previous_year_last_month, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices(this_month, regulation_month)

    # Sale for the apartment in a housing company that will be under regulation checking
    # Index adjusted price for the housing company will be: (50_000 + 10_000) / 10 * (200 / 100) = 12_000
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

    # Apartment where sales happened in the previous year, but it is on another postal code
    apartment_1: Apartment = ApartmentFactory.create(
        completion_date=previous_year_last_month,
        building__real_estate__housing_company__postal_code__value="00002",
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sales__purchase_date=previous_year_last_month,  # first sale, not counted
    )

    # Sale in the previous year
    # Average sales price will be: (40_000 + 9_000) / 1 = 49_000
    ApartmentSaleFactory.create(
        apartment=apartment_1,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=40_000,
        apartment_share_of_housing_company_loans=9_000,
    )

    # Apartment where sales happened in the previous year, but it is on another postal code
    apartment_2: Apartment = ApartmentFactory.create(
        completion_date=previous_year_last_month,
        building__real_estate__housing_company__postal_code__value="00003",
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sales__purchase_date=previous_year_last_month,  # first sale, not counted
    )

    # Sale in the previous year
    # Average sales price will be: (4_000 + 900) / 1 = 4_900
    ApartmentSaleFactory.create(
        apartment=apartment_2,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=4_000,
        apartment_share_of_housing_company_loans=900,
    )

    create_no_external_sales_data(this_month, previous_year_last_month)

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

    #
    # Since there is no sales data for the postal code, we use the replacement postal codes.
    # The average price per square meter for the replacement postal codes is (49_000 + 4_900) / 2 = 26_950.
    #
    # Since the average sales price per square meter in the last year (26_950) is higher than the
    # housing company's compared value (in this case the index adjusted acquisition price of 12_000),
    # the company stays regulated.
    #
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == RegulationResults(
        automatically_released=[],
        released_from_regulation=[],
        stays_regulated=[
            ComparisonData(
                id=sale.apartment.housing_company.uuid.hex,
                display_name=sale.apartment.housing_company.display_name,
                address=AddressInfo(
                    street_address=sale.apartment.housing_company.street_address,
                    postal_code=sale.apartment.housing_company.postal_code.value,
                    city=sale.apartment.housing_company.postal_code.city,
                ),
                price=Decimal("12000.0"),
                old_ruleset=sale.apartment.housing_company.hitas_type.old_hitas_ruleset,
                completion_date=regulation_month.isoformat(),
                property_manager=PropertyManagerInfo(
                    id=sale.apartment.housing_company.property_manager.uuid.hex,
                    name=sale.apartment.housing_company.property_manager.name,
                    email=sale.apartment.housing_company.property_manager.email,
                    last_modified=this_month.isoformat(),
                ),
                letter_fetched=False,
                current_regulation_status=RegulationStatus.REGULATED.value,
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
        internal={
            "00002": {"2022Q4": SaleData(sale_count=1, price=49_000)},
            "00003": {"2022Q4": SaleData(sale_count=1, price=4_900)},
        },
        external={},
        price_by_area={"00002": 49000.0, "00003": 4900.0},
    )
    assert regulation_results[0].replacement_postal_codes == [
        ReplacementPostalCodesWithPrice(
            postal_code="00001",
            replacements=["00002", "00003"],
            price_by_area=26950.0,
        ),
    ]

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
def test__api__regulation__no_sales_data_for_postal_code__half_hitas(api_client: HitasAPIClient, freezer):
    this_month, previous_year_last_month, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices(this_month, regulation_month)

    # Sale for the apartment in a housing company that will be under regulation checking
    # Index adjusted price for the housing company will be: (50_000 + 10_000) / 10 * (200 / 100) = 12_000
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

    # Apartment where sales happened in the previous year, but it is in a half-hitas housing company
    apartment: Apartment = ApartmentFactory.create(
        completion_date=previous_year_last_month,
        building__real_estate__housing_company__postal_code__value="00001",
        building__real_estate__housing_company__hitas_type=HitasType.HALF_HITAS,
        sales__purchase_date=previous_year_last_month,  # first sale, not counted
    )

    # Sale in the previous year, but it is for half-hitas housing company
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
            ComparisonData(
                id=sale.apartment.housing_company.uuid.hex,
                display_name=sale.apartment.housing_company.display_name,
                address=AddressInfo(
                    street_address=sale.apartment.housing_company.street_address,
                    postal_code=sale.apartment.housing_company.postal_code.value,
                    city=sale.apartment.housing_company.postal_code.city,
                ),
                price=Decimal("12000.0"),
                old_ruleset=sale.apartment.housing_company.hitas_type.old_hitas_ruleset,
                completion_date=regulation_month.isoformat(),
                property_manager=PropertyManagerInfo(
                    id=sale.apartment.housing_company.property_manager.uuid.hex,
                    name=sale.apartment.housing_company.property_manager.name,
                    email=sale.apartment.housing_company.property_manager.email,
                    last_modified=this_month.isoformat(),
                ),
                letter_fetched=False,
                current_regulation_status=RegulationStatus.REGULATED.value,
            )
        ],
        obfuscated_owners=[],
    )


@pytest.mark.django_db
def test__api__regulation__no_sales_data_for_postal_code__sale_previous_year(api_client: HitasAPIClient, freezer):
    this_month, previous_year_last_month, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices(this_month, regulation_month)

    # Sale for the apartment in a housing company that will be under regulation checking
    # Index adjusted price for the housing company will be: (50_000 + 10_000) / 10 * (200 / 100) = 12_000
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

    # Apartment where sales happened
    apartment: Apartment = ApartmentFactory.create(
        completion_date=previous_year_last_month - relativedelta(years=1),
        building__real_estate__housing_company__postal_code__value="00001",
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sales__purchase_date=previous_year_last_month - relativedelta(years=1),  # first sale, not counted
    )

    # Sale is not in the previous four quarters, so it is not counted
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month - relativedelta(years=1) + relativedelta(days=1),
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
            ComparisonData(
                id=sale.apartment.housing_company.uuid.hex,
                display_name=sale.apartment.housing_company.display_name,
                address=AddressInfo(
                    street_address=sale.apartment.housing_company.street_address,
                    postal_code=sale.apartment.housing_company.postal_code.value,
                    city=sale.apartment.housing_company.postal_code.city,
                ),
                price=Decimal("12000.0"),
                old_ruleset=sale.apartment.housing_company.hitas_type.old_hitas_ruleset,
                completion_date=regulation_month.isoformat(),
                property_manager=PropertyManagerInfo(
                    id=sale.apartment.housing_company.property_manager.uuid.hex,
                    name=sale.apartment.housing_company.property_manager.name,
                    email=sale.apartment.housing_company.property_manager.email,
                    last_modified=this_month.isoformat(),
                ),
                letter_fetched=False,
                current_regulation_status=RegulationStatus.REGULATED.value,
            )
        ],
        obfuscated_owners=[],
    )


@pytest.mark.django_db
def test__api__regulation__no_sales_data_for_postal_code__other_not_regulated(api_client: HitasAPIClient, freezer):
    this_month, previous_year_last_month, regulation_month = get_relevant_dates(freezer)

    create_necessary_indices(this_month, regulation_month)

    # Sale for the apartment in a housing company that has no sales in its postal code
    sale_1: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )
    # This housing company would be released, but since the other one is not, the regulation won't finish
    sale_2: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00002",
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
            ComparisonData(
                id=sale_1.apartment.housing_company.uuid.hex,
                display_name=sale_1.apartment.housing_company.display_name,
                address=AddressInfo(
                    street_address=sale_1.apartment.housing_company.street_address,
                    postal_code=sale_1.apartment.housing_company.postal_code.value,
                    city=sale_1.apartment.housing_company.postal_code.city,
                ),
                price=Decimal("12000.0"),
                old_ruleset=sale_1.apartment.housing_company.hitas_type.old_hitas_ruleset,
                completion_date=regulation_month.isoformat(),
                property_manager=PropertyManagerInfo(
                    id=sale_1.apartment.housing_company.property_manager.uuid.hex,
                    name=sale_1.apartment.housing_company.property_manager.name,
                    email=sale_1.apartment.housing_company.property_manager.email,
                    last_modified=this_month.isoformat(),
                ),
                letter_fetched=False,
                current_regulation_status=RegulationStatus.REGULATED.value,
            )
        ],
        obfuscated_owners=[],
    )

    #
    # Check that the housing companies have not been regulated
    #
    sale_1.apartment.housing_company.refresh_from_db()
    assert sale_1.apartment.housing_company.regulation_status == RegulationStatus.REGULATED

    sale_2.apartment.housing_company.refresh_from_db()
    assert sale_2.apartment.housing_company.regulation_status == RegulationStatus.REGULATED
