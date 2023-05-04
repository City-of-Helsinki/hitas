import datetime
from decimal import Decimal

import pytest
from dateutil.relativedelta import relativedelta
from rest_framework import status
from rest_framework.reverse import reverse

from hitas.models import Apartment, ApartmentSale, ExternalSalesData, HousingCompanyState
from hitas.models.external_sales_data import CostAreaData, QuarterData, SaleData
from hitas.models.housing_company import HitasType, RegulationStatus
from hitas.models.owner import Owner, OwnerT
from hitas.models.thirty_year_regulation import (
    FullSalesData,
    RegulationResult,
    ThirtyYearRegulationResults,
    ThirtyYearRegulationResultsRow,
)
from hitas.services.thirty_year_regulation import AddressInfo, ComparisonData, PropertyManagerInfo, RegulationResults
from hitas.tests.apis.helpers import HitasAPIClient, count_queries
from hitas.tests.factories import ApartmentFactory, ApartmentSaleFactory
from hitas.tests.factories.indices import MarketPriceIndexFactory, SurfaceAreaPriceCeilingFactory
from hitas.utils import to_quarter

# Read regulation results


@pytest.mark.django_db
def test__api__regulation__fetch_exising(api_client: HitasAPIClient, freezer):
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
            ComparisonData(
                id=sale.apartment.housing_company.uuid.hex,
                display_name=sale.apartment.housing_company.display_name,
                address=AddressInfo(
                    street_address=sale.apartment.housing_company.street_address,
                    postal_code=sale.apartment.housing_company.postal_code.value,
                    city=sale.apartment.housing_company.postal_code.city,
                ),
                price=row.adjusted_average_price_per_square_meter,
                old_ruleset=sale.apartment.housing_company.hitas_type.old_hitas_ruleset,
                completion_date=regulation_month.isoformat(),
                property_manager=PropertyManagerInfo(
                    id=sale.apartment.housing_company.property_manager.uuid.hex,
                    name=sale.apartment.housing_company.property_manager.name,
                    email=sale.apartment.housing_company.property_manager.email,
                    address=AddressInfo(
                        street_address=sale.apartment.housing_company.property_manager.street_address,
                        postal_code=sale.apartment.housing_company.property_manager.postal_code,
                        city=sale.apartment.housing_company.property_manager.city,
                    ),
                ),
                letter_fetched=True,
            )
        ],
        skipped=[],
        obfuscated_owners=[],
    )


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


# Perform regulation


@pytest.mark.django_db
def test__api__regulation__empty(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == RegulationResults(
        automatically_released=[],
        released_from_regulation=[],
        stays_regulated=[],
        skipped=[],
        obfuscated_owners=[],
    )


@pytest.mark.django_db
def test__api__regulation__stays_regulated(api_client: HitasAPIClient, freezer):
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

    # Apartment where sales happened in the previous year
    apartment: Apartment = ApartmentFactory.create(
        completion_date=previous_year_last_month,
        building__real_estate__housing_company__postal_code__value="00001",
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sales__purchase_date=previous_year_last_month,  # first sale, not counted
    )

    # Sale in the previous year, which affect the average price per square meter
    # Average sales price will be: (40_000 + 9_000) / 1 = 49_000
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=40_000,
        apartment_share_of_housing_company_loans=9_000,
    )

    # Create necessary external sales data (no external sales)
    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(previous_year_last_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=3)), areas=[]),
        quarter_4=QuarterData(quarter=to_quarter(previous_year_last_month), areas=[]),
    )

    url = reverse("hitas:thirty-year-regulation-list")

    # 1. Check for previous regulation results
    # 2. Fetch housing companies
    # 3. Prefetch real estates for housing companies
    # 4. Prefetch buildings for real estates
    # 5. Prefetch apartments for buildings
    # 6. Fetch apartments with missing prices
    # 7. Fetch market price indices
    # 8. Fetch surface area price ceiling
    # 9. Fetch hitas sales
    # 10. Fetch external sales data
    # 11. Fetch housing companies for audit log update
    # 12. Set housing companies' states
    # 13. Search for owners to be obfuscated (none found)
    # 14. Select thirty year regulation results for update
    # 15. Save thirty year regulation results
    # 16. Fetch current thirty year regulation result row ids
    # 17. Save thirty year regulation results' rows
    # 18. Select current thirty year regulation result rows for audit log update
    # 19. TODO: ???
    # 20. TODO: ???
    with count_queries(20):
        response = api_client.post(url, data={}, format="json")

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
                    address=AddressInfo(
                        street_address=sale.apartment.housing_company.property_manager.street_address,
                        postal_code=sale.apartment.housing_company.property_manager.postal_code,
                        city=sale.apartment.housing_company.property_manager.city,
                    ),
                ),
                letter_fetched=False,
            )
        ],
        skipped=[],
        obfuscated_owners=[],
    )

    #
    # Check that the housing company stays regulated
    #
    sale.apartment.housing_company.refresh_from_db()
    assert sale.apartment.housing_company.state == HousingCompanyState.GREATER_THAN_30_YEARS_NOT_FREE
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

    owner: Owner = sale.ownerships.first().owner

    # Apartment where sales happened in the previous year
    apartment: Apartment = ApartmentFactory.create(
        completion_date=previous_year_last_month,
        building__real_estate__housing_company__postal_code__value="00001",
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sales__purchase_date=previous_year_last_month,  # first sale, not counted
    )

    # Sale in the previous year, which affect the average price per square meter
    # Average sales price will be: (4_000 + 900) / 1 = 4_900
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=4_000,
        apartment_share_of_housing_company_loans=900,
    )

    # Create necessary external sales data (no external sales)
    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(previous_year_last_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=3)), areas=[]),
        quarter_4=QuarterData(quarter=to_quarter(previous_year_last_month), areas=[]),
    )

    url = reverse("hitas:thirty-year-regulation-list")

    # 1. Check for previous regulation results
    # 2. Fetch housing companies
    # 3. Prefetch real estates for housing companies
    # 4. Prefetch buildings for real estates
    # 5. Prefetch apartments for buildings
    # 6. Fetch apartments with missing prices
    # 7. Fetch market price indices
    # 8. Fetch surface area price ceiling
    # 9. Fetch hitas sales
    # 10. Fetch external sales data
    # 11. Fetch housing companies for audit log update
    # 12. Set housing companies' states
    # 13. Search for owners to be obfuscated
    # 14. Fetch owners for audit log update
    # 15. Obfuscate owners without any regulated apartments
    # 16. Select thirty year regulation results for update
    # 17. Save thirty year regulation results
    # 18. Fetch current thirty year regulation result row ids
    # 19. Save thirty year regulation results' rows
    # 20. Select current thirty year regulation result rows for audit log update
    # 21. TODO: ???
    # 22. TODO: ???
    with count_queries(22):
        response = api_client.post(url, data={}, format="json")

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
                    address=AddressInfo(
                        street_address=sale.apartment.housing_company.property_manager.street_address,
                        postal_code=sale.apartment.housing_company.property_manager.postal_code,
                        city=sale.apartment.housing_company.property_manager.city,
                    ),
                ),
                letter_fetched=False,
            )
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
    assert sale.apartment.housing_company.state == HousingCompanyState.GREATER_THAN_30_YEARS_FREE
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

    owner: Owner = sale.ownerships.first().owner

    # Apartment where sales happened in the previous year
    apartment: Apartment = ApartmentFactory.create(
        completion_date=previous_year_last_month,
        building__real_estate__housing_company__postal_code__value="00001",
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sales__purchase_date=previous_year_last_month,  # first sale, not counted
    )

    # Sale in the previous year, which affect the average price per square meter
    # Average sales price will be: (10_000 + 2_000) / 1 = 12_000
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=10_000,
        apartment_share_of_housing_company_loans=2_000,
    )

    # Create necessary external sales data (no external sales)
    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(previous_year_last_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=3)), areas=[]),
        quarter_4=QuarterData(quarter=to_quarter(previous_year_last_month), areas=[]),
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

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
                    address=AddressInfo(
                        street_address=sale.apartment.housing_company.property_manager.street_address,
                        postal_code=sale.apartment.housing_company.property_manager.postal_code,
                        city=sale.apartment.housing_company.property_manager.city,
                    ),
                ),
                letter_fetched=False,
            )
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
def test__api__regulation__automatically_release__all(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    previous_year_last_month = this_month - relativedelta(months=2)
    regulation_month = this_month - relativedelta(years=30)

    # Create necessary indices
    MarketPriceIndexFactory.create(month=regulation_month, value=100)
    MarketPriceIndexFactory.create(month=this_month, value=200)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=5000)

    # Create necessary sale, apartment, and housing company for regulation
    # This housing company will be automatically released, since it is not using the old hitas ruleset
    sale: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )

    owner: Owner = sale.ownerships.first().owner

    # Create necessary external sales data (no external sales)
    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(previous_year_last_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=3)), areas=[]),
        quarter_4=QuarterData(quarter=to_quarter(previous_year_last_month), areas=[]),
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == RegulationResults(
        automatically_released=[
            ComparisonData(
                id=sale.apartment.housing_company.uuid.hex,
                display_name=sale.apartment.housing_company.display_name,
                address=AddressInfo(
                    street_address=sale.apartment.housing_company.street_address,
                    postal_code=sale.apartment.housing_company.postal_code.value,
                    city=sale.apartment.housing_company.postal_code.city,
                ),
                price=Decimal("0"),
                old_ruleset=sale.apartment.housing_company.hitas_type.old_hitas_ruleset,
                completion_date=regulation_month.isoformat(),
                property_manager=PropertyManagerInfo(
                    id=sale.apartment.housing_company.property_manager.uuid.hex,
                    name=sale.apartment.housing_company.property_manager.name,
                    email=sale.apartment.housing_company.property_manager.email,
                    address=AddressInfo(
                        street_address=sale.apartment.housing_company.property_manager.street_address,
                        postal_code=sale.apartment.housing_company.property_manager.postal_code,
                        city=sale.apartment.housing_company.property_manager.city,
                    ),
                ),
                letter_fetched=False,
            )
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
    assert sale.apartment.housing_company.state == HousingCompanyState.GREATER_THAN_30_YEARS_FREE
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
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    previous_year_last_month = this_month - relativedelta(months=2)
    regulation_month = this_month - relativedelta(years=30)

    # Create necessary indices
    MarketPriceIndexFactory.create(month=regulation_month, value=100)
    MarketPriceIndexFactory.create(month=this_month, value=200)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=5000)

    # Sales for the apartment in a housing company that will be under regulation checking
    # This housing company will be automatically released, since it is not using the old hitas ruleset
    sale_1: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )
    # This housing company will be checked, since it is using the old hitas ruleset
    sale_2: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )

    owner_1: Owner = sale_1.ownerships.first().owner
    owner_2: Owner = sale_2.ownerships.first().owner

    # Apartment where sales happened in the previous year
    apartment: Apartment = ApartmentFactory.create(
        completion_date=previous_year_last_month,
        building__real_estate__housing_company__postal_code__value="00001",
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sales__purchase_date=previous_year_last_month,  # first sale, not counted
    )

    # Sale in the previous year, which affect the average price per square meter
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=4_000,
        apartment_share_of_housing_company_loans=900,
    )

    # Create necessary external sales data (no external sales)
    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(previous_year_last_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=3)), areas=[]),
        quarter_4=QuarterData(quarter=to_quarter(previous_year_last_month), areas=[]),
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == RegulationResults(
        automatically_released=[
            ComparisonData(
                id=sale_1.apartment.housing_company.uuid.hex,
                display_name=sale_1.apartment.housing_company.display_name,
                address=AddressInfo(
                    street_address=sale_1.apartment.housing_company.street_address,
                    postal_code=sale_1.apartment.housing_company.postal_code.value,
                    city=sale_1.apartment.housing_company.postal_code.city,
                ),
                price=Decimal("0"),
                old_ruleset=sale_1.apartment.housing_company.hitas_type.old_hitas_ruleset,
                completion_date=regulation_month.isoformat(),
                property_manager=PropertyManagerInfo(
                    id=sale_1.apartment.housing_company.property_manager.uuid.hex,
                    name=sale_1.apartment.housing_company.property_manager.name,
                    email=sale_1.apartment.housing_company.property_manager.email,
                    address=AddressInfo(
                        street_address=sale_1.apartment.housing_company.property_manager.street_address,
                        postal_code=sale_1.apartment.housing_company.property_manager.postal_code,
                        city=sale_1.apartment.housing_company.property_manager.city,
                    ),
                ),
                letter_fetched=False,
            )
        ],
        released_from_regulation=[
            ComparisonData(
                id=sale_2.apartment.housing_company.uuid.hex,
                display_name=sale_2.apartment.housing_company.display_name,
                address=AddressInfo(
                    street_address=sale_2.apartment.housing_company.street_address,
                    postal_code=sale_2.apartment.housing_company.postal_code.value,
                    city=sale_2.apartment.housing_company.postal_code.city,
                ),
                price=Decimal("12000.0"),
                old_ruleset=sale_2.apartment.housing_company.hitas_type.old_hitas_ruleset,
                completion_date=regulation_month.isoformat(),
                property_manager=PropertyManagerInfo(
                    id=sale_2.apartment.housing_company.property_manager.uuid.hex,
                    name=sale_2.apartment.housing_company.property_manager.name,
                    email=sale_2.apartment.housing_company.property_manager.email,
                    address=AddressInfo(
                        street_address=sale_2.apartment.housing_company.property_manager.street_address,
                        postal_code=sale_2.apartment.housing_company.property_manager.postal_code,
                        city=sale_2.apartment.housing_company.property_manager.city,
                    ),
                ),
                letter_fetched=False,
            )
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
    assert sale_1.apartment.housing_company.state == HousingCompanyState.GREATER_THAN_30_YEARS_FREE
    assert sale_1.apartment.housing_company.regulation_status == RegulationStatus.RELEASED_BY_HITAS

    sale_2.apartment.housing_company.refresh_from_db()
    assert sale_2.apartment.housing_company.state == HousingCompanyState.GREATER_THAN_30_YEARS_FREE
    assert sale_2.apartment.housing_company.regulation_status == RegulationStatus.RELEASED_BY_HITAS


@pytest.mark.django_db
def test__api__regulation__surface_area_price_ceiling_is_used_in_comparison(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    previous_year_last_month = this_month - relativedelta(months=2)
    regulation_month = this_month - relativedelta(years=30)

    # Create necessary indices
    MarketPriceIndexFactory.create(month=regulation_month, value=100)
    MarketPriceIndexFactory.create(month=this_month, value=200)

    # Surface area price will be higher than the housing company index adjusted price
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=50_000)

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

    owner: Owner = sale.ownerships.first().owner

    # Apartment where sales happened in the previous year
    apartment: Apartment = ApartmentFactory.create(
        completion_date=previous_year_last_month,
        building__real_estate__housing_company__postal_code__value="00001",
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sales__purchase_date=previous_year_last_month,  # first sale, not counted
    )

    # Sale in the previous year, which affect the average price per square meter
    # Average sales price will be: (40_000 + 9_000) / 1 = 49_000
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=40_000,
        apartment_share_of_housing_company_loans=9_000,
    )

    # Create necessary external sales data (no external sales)
    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(previous_year_last_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=3)), areas=[]),
        quarter_4=QuarterData(quarter=to_quarter(previous_year_last_month), areas=[]),
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

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
            ComparisonData(
                id=sale.apartment.housing_company.uuid.hex,
                display_name=sale.apartment.housing_company.display_name,
                address=AddressInfo(
                    street_address=sale.apartment.housing_company.street_address,
                    postal_code=sale.apartment.housing_company.postal_code.value,
                    city=sale.apartment.housing_company.postal_code.city,
                ),
                price=Decimal("50000.0"),
                old_ruleset=sale.apartment.housing_company.hitas_type.old_hitas_ruleset,
                completion_date=regulation_month.isoformat(),
                property_manager=PropertyManagerInfo(
                    id=sale.apartment.housing_company.property_manager.uuid.hex,
                    name=sale.apartment.housing_company.property_manager.name,
                    email=sale.apartment.housing_company.property_manager.email,
                    address=AddressInfo(
                        street_address=sale.apartment.housing_company.property_manager.street_address,
                        postal_code=sale.apartment.housing_company.property_manager.postal_code,
                        city=sale.apartment.housing_company.property_manager.city,
                    ),
                ),
                letter_fetched=False,
            )
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
def test__api__regulation__no_sales_data_for_postal_code(api_client: HitasAPIClient, freezer):
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

    # Create necessary external sales data (no external sales)
    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(previous_year_last_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=3)), areas=[]),
        quarter_4=QuarterData(quarter=to_quarter(previous_year_last_month), areas=[]),
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

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
                    address=AddressInfo(
                        street_address=sale.apartment.housing_company.property_manager.street_address,
                        postal_code=sale.apartment.housing_company.property_manager.postal_code,
                        city=sale.apartment.housing_company.property_manager.city,
                    ),
                ),
                letter_fetched=False,
            )
        ],
        obfuscated_owners=[],
    )


@pytest.mark.django_db
def test__api__regulation__no_sales_data_for_postal_code__half_hitas(api_client: HitasAPIClient, freezer):
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

    # Create necessary external sales data (no external sales)
    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(previous_year_last_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=3)), areas=[]),
        quarter_4=QuarterData(quarter=to_quarter(previous_year_last_month), areas=[]),
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

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
                    address=AddressInfo(
                        street_address=sale.apartment.housing_company.property_manager.street_address,
                        postal_code=sale.apartment.housing_company.property_manager.postal_code,
                        city=sale.apartment.housing_company.property_manager.city,
                    ),
                ),
                letter_fetched=False,
            )
        ],
        obfuscated_owners=[],
    )


@pytest.mark.django_db
def test__api__regulation__no_sales_data_for_postal_code__sale_previous_year(api_client: HitasAPIClient, freezer):
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

    # Create necessary external sales data (no external sales)
    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(previous_year_last_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=3)), areas=[]),
        quarter_4=QuarterData(quarter=to_quarter(previous_year_last_month), areas=[]),
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

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
                    address=AddressInfo(
                        street_address=sale.apartment.housing_company.property_manager.street_address,
                        postal_code=sale.apartment.housing_company.property_manager.postal_code,
                        city=sale.apartment.housing_company.property_manager.city,
                    ),
                ),
                letter_fetched=False,
            )
        ],
        obfuscated_owners=[],
    )


@pytest.mark.django_db
def test__api__regulation__no_sales_data_for_postal_code__other_not_regulated(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    previous_year_last_month = this_month - relativedelta(months=2)
    regulation_month = this_month - relativedelta(years=30)

    # Create necessary indices
    MarketPriceIndexFactory.create(month=regulation_month, value=100)
    MarketPriceIndexFactory.create(month=this_month, value=200)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=5000)

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

    # Create necessary external sales data (no external sales)
    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(previous_year_last_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=3)), areas=[]),
        quarter_4=QuarterData(quarter=to_quarter(previous_year_last_month), areas=[]),
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

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
                    address=AddressInfo(
                        street_address=sale_1.apartment.housing_company.property_manager.street_address,
                        postal_code=sale_1.apartment.housing_company.property_manager.postal_code,
                        city=sale_1.apartment.housing_company.property_manager.city,
                    ),
                ),
                letter_fetched=False,
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


@pytest.mark.django_db
def test__api__regulation__only_external_sales_data(api_client: HitasAPIClient, freezer):
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

    # Create necessary external sales data
    # Average sales price will be: (15_000 + 30_000) / (1 + 2) = 15_000
    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(previous_year_last_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(
            quarter=to_quarter(previous_year_last_month - relativedelta(months=3)),
            areas=[CostAreaData(postal_code="00001", sale_count=1, price=15_000)],
        ),
        quarter_4=QuarterData(
            quarter=to_quarter(previous_year_last_month),
            areas=[
                CostAreaData(postal_code="00001", sale_count=2, price=30_000),
            ],
        ),
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

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
                    address=AddressInfo(
                        street_address=sale.apartment.housing_company.property_manager.street_address,
                        postal_code=sale.apartment.housing_company.property_manager.postal_code,
                        city=sale.apartment.housing_company.property_manager.city,
                    ),
                ),
                letter_fetched=False,
            )
        ],
        skipped=[],
        obfuscated_owners=[],
    )


@pytest.mark.django_db
def test__api__regulation__both_hitas_and_external_sales_data(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    previous_year_last_month = day.date() - relativedelta(months=2)
    regulation_month = day.date() - relativedelta(years=30)

    # Create necessary indices
    MarketPriceIndexFactory.create(month=regulation_month, value=100)
    MarketPriceIndexFactory.create(month=this_month, value=200)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=5000)

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

    # Apartment where sales happened in the previous year
    apartment: Apartment = ApartmentFactory.create(
        completion_date=previous_year_last_month,
        building__real_estate__housing_company__postal_code__value="00001",
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sales__purchase_date=previous_year_last_month,  # first sale, not counted
    )

    # Sale in the previous year, which affect the average price per square meter
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=40_000,
        apartment_share_of_housing_company_loans=9_000,
    )
    # Create necessary external sales data
    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(previous_year_last_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(
            quarter=to_quarter(previous_year_last_month - relativedelta(months=3)),
            areas=[CostAreaData(postal_code="00001", sale_count=1, price=15_000)],
        ),
        quarter_4=QuarterData(
            quarter=to_quarter(previous_year_last_month),
            areas=[
                CostAreaData(postal_code="00001", sale_count=2, price=30_000),
            ],
        ),
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

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
                    address=AddressInfo(
                        street_address=sale.apartment.housing_company.property_manager.street_address,
                        postal_code=sale.apartment.housing_company.property_manager.postal_code,
                        city=sale.apartment.housing_company.property_manager.city,
                    ),
                ),
                letter_fetched=False,
            )
        ],
        skipped=[],
        obfuscated_owners=[],
    )


@pytest.mark.django_db
def test__api__regulation__use_catalog_prices(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    previous_year_last_month = this_month - relativedelta(months=2)
    regulation_month = this_month - relativedelta(years=30)

    # Create necessary indices
    MarketPriceIndexFactory.create(month=regulation_month, value=100)
    MarketPriceIndexFactory.create(month=this_month, value=200)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=5000)

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
    apartment_2: Apartment = ApartmentFactory.create(
        completion_date=previous_year_last_month,
        building__real_estate__housing_company__postal_code__value="00001",
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sales__purchase_date=previous_year_last_month,  # first sale, not counted
    )

    # Sale in the previous year, which affect the average price per square meter
    # Average sales price will be: (40_000 + 9_000) / 1 = 49_000
    ApartmentSaleFactory.create(
        apartment=apartment_2,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=40_000,
        apartment_share_of_housing_company_loans=9_000,
    )

    # Create necessary external sales data (no external sales)
    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(previous_year_last_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=3)), areas=[]),
        quarter_4=QuarterData(quarter=to_quarter(previous_year_last_month), areas=[]),
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

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
            ComparisonData(
                id=apartment_1.housing_company.uuid.hex,
                display_name=apartment_1.housing_company.display_name,
                address=AddressInfo(
                    street_address=apartment_1.housing_company.street_address,
                    postal_code=apartment_1.housing_company.postal_code.value,
                    city=apartment_1.housing_company.postal_code.city,
                ),
                price=Decimal("12000.0"),
                old_ruleset=apartment_1.housing_company.hitas_type.old_hitas_ruleset,
                completion_date=regulation_month.isoformat(),
                property_manager=PropertyManagerInfo(
                    id=apartment_1.housing_company.property_manager.uuid.hex,
                    name=apartment_1.housing_company.property_manager.name,
                    email=apartment_1.housing_company.property_manager.email,
                    address=AddressInfo(
                        street_address=apartment_1.housing_company.property_manager.street_address,
                        postal_code=apartment_1.housing_company.property_manager.postal_code,
                        city=apartment_1.housing_company.property_manager.city,
                    ),
                ),
                letter_fetched=False,
            )
        ],
        skipped=[],
        obfuscated_owners=[],
    )


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
def test__api__regulation__exclude_from_statistics__housing_company(api_client: HitasAPIClient, freezer):
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

    # Apartment where sales happened in the previous year, but it is in a housing company that should not be
    # included in statistics, so its sales do not affect postal code average square price calculation
    apartment: Apartment = ApartmentFactory.create(
        completion_date=previous_year_last_month,
        building__real_estate__housing_company__postal_code__value="00001",
        building__real_estate__housing_company__exclude_from_statistics=True,
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
        calculation_quarter=to_quarter(previous_year_last_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=3)), areas=[]),
        quarter_4=QuarterData(quarter=to_quarter(previous_year_last_month), areas=[]),
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

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
                    address=AddressInfo(
                        street_address=sale.apartment.housing_company.property_manager.street_address,
                        postal_code=sale.apartment.housing_company.property_manager.postal_code,
                        city=sale.apartment.housing_company.property_manager.city,
                    ),
                ),
                letter_fetched=False,
            )
        ],
        obfuscated_owners=[],
    )


@pytest.mark.django_db
def test__api__regulation__exclude_from_statistics__sale__all(api_client: HitasAPIClient, freezer):
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

    # Apartment where sales happened in the previous year
    apartment: Apartment = ApartmentFactory.create(
        completion_date=previous_year_last_month,
        building__real_estate__housing_company__postal_code__value="00001",
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sales__purchase_date=previous_year_last_month,  # first sale, not counted
    )

    # Sale in the previous year, but it is excluded from statistics
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=40_000,
        exclude_from_statistics=True,
        apartment_share_of_housing_company_loans=9_000,
    )

    # Create necessary external sales data (no external sales)
    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(previous_year_last_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=3)), areas=[]),
        quarter_4=QuarterData(quarter=to_quarter(previous_year_last_month), areas=[]),
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

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
                    address=AddressInfo(
                        street_address=sale.apartment.housing_company.property_manager.street_address,
                        postal_code=sale.apartment.housing_company.property_manager.postal_code,
                        city=sale.apartment.housing_company.property_manager.city,
                    ),
                ),
                letter_fetched=False,
            )
        ],
        obfuscated_owners=[],
    )


@pytest.mark.django_db
def test__api__regulation__exclude_from_statistics__sale__partial(api_client: HitasAPIClient, freezer):
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

    # Apartment where sales happened in the previous year
    apartment: Apartment = ApartmentFactory.create(
        completion_date=previous_year_last_month,
        building__real_estate__housing_company__postal_code__value="00001",
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sales__purchase_date=previous_year_last_month,  # first sale, not counted
    )

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

    # Create necessary external sales data (no external sales)
    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(previous_year_last_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=3)), areas=[]),
        quarter_4=QuarterData(quarter=to_quarter(previous_year_last_month), areas=[]),
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

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
                    address=AddressInfo(
                        street_address=sale.apartment.housing_company.property_manager.street_address,
                        postal_code=sale.apartment.housing_company.property_manager.postal_code,
                        city=sale.apartment.housing_company.property_manager.city,
                    ),
                ),
                letter_fetched=False,
            )
        ],
        skipped=[],
        obfuscated_owners=[],
    )


@pytest.mark.django_db
def test__api__regulation__no_housing_company_over_30_years(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    previous_year_last_month = this_month - relativedelta(months=1)

    # Apartment where sales happened in the previous year
    apartment: Apartment = ApartmentFactory.create(
        completion_date=previous_year_last_month,
        building__real_estate__housing_company__postal_code__value="00001",
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sales__purchase_date=previous_year_last_month,  # first sale, not counted
    )

    # Sale in the previous year, which would be used in comparison, but there are no housing companies to check
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=40_000,
        apartment_share_of_housing_company_loans=9_000,
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

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
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    previous_year_last_month = this_month - relativedelta(months=2)
    regulation_month = this_month - relativedelta(years=30)

    # Create necessary indices
    MarketPriceIndexFactory.create(month=regulation_month, value=100)
    MarketPriceIndexFactory.create(month=this_month, value=200)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=5000)

    # Sale for the apartment in a housing company whose state is under test
    sale: ApartmentSale = ApartmentSaleFactory.create(
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
    apartment: Apartment = ApartmentFactory.create(
        completion_date=previous_year_last_month,
        building__real_estate__housing_company__postal_code__value="00001",
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sales__purchase_date=previous_year_last_month,  # first sale, not counted
    )

    # Sale in the previous year, which might be used in comparison if there are housing companies to check
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=40_000,
        apartment_share_of_housing_company_loans=9_000,
    )

    # Create necessary external sales data (no external sales)
    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(previous_year_last_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=3)), areas=[]),
        quarter_4=QuarterData(quarter=to_quarter(previous_year_last_month), areas=[]),
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()

    if is_compared:
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
                        address=AddressInfo(
                            street_address=sale.apartment.housing_company.property_manager.street_address,
                            postal_code=sale.apartment.housing_company.property_manager.postal_code,
                            city=sale.apartment.housing_company.property_manager.city,
                        ),
                    ),
                    letter_fetched=False,
                )
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


@pytest.mark.django_db
def test__api__regulation__end_of_period(api_client: HitasAPIClient, freezer):
    first_day = datetime.date(2023, 2, 1)
    last_day = datetime.datetime(2023, 4, 30)
    # Calculation is made on the last day of the hitas calculation period.
    # It should still work just the same as if it was the first day of the period.
    freezer.move_to(last_day)

    this_month = first_day
    previous_year_last_month = this_month - relativedelta(months=2)
    regulation_month = this_month - relativedelta(years=30)

    # Create necessary indices
    MarketPriceIndexFactory.create(month=regulation_month, value=100)
    MarketPriceIndexFactory.create(month=this_month, value=200)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=5000)

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

    # Apartment where sales happened in the previous year
    apartment: Apartment = ApartmentFactory.create(
        completion_date=previous_year_last_month,
        building__real_estate__housing_company__postal_code__value="00001",
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sales__purchase_date=previous_year_last_month,  # first sale, not counted
    )

    # Sale in the previous year, which affect the average price per square meter
    # Average sales price will be: (40_000 + 9_000) / 1 = 49_000
    ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=previous_year_last_month + relativedelta(days=1),
        purchase_price=40_000,
        apartment_share_of_housing_company_loans=9_000,
    )

    # Create necessary external sales data (no external sales)
    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(previous_year_last_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=3)), areas=[]),
        quarter_4=QuarterData(quarter=to_quarter(previous_year_last_month), areas=[]),
    )

    url = reverse("hitas:thirty-year-regulation-list")

    response = api_client.post(url, data={}, format="json")

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
                    address=AddressInfo(
                        street_address=sale.apartment.housing_company.property_manager.street_address,
                        postal_code=sale.apartment.housing_company.property_manager.postal_code,
                        city=sale.apartment.housing_company.property_manager.city,
                    ),
                ),
            )
        ],
        skipped=[],
        obfuscated_owners=[],
    )
