import datetime
from decimal import Decimal

import pytest
from dateutil.relativedelta import relativedelta
from rest_framework import status
from rest_framework.reverse import reverse

from hitas.models import Apartment, ApartmentSale, ConditionOfSale
from hitas.models.housing_company import HitasType, RegulationStatus
from hitas.models.owner import Owner, OwnerT
from hitas.services.thirty_year_regulation import AddressInfo, ComparisonData, PropertyManagerInfo, RegulationResults
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.apis.thirty_year_regulation.utils import create_no_external_sales_data
from hitas.tests.factories import ApartmentFactory, ApartmentSaleFactory, ConditionOfSaleFactory, OwnerFactory
from hitas.tests.factories.indices import MarketPriceIndexFactory, SurfaceAreaPriceCeilingFactory


@pytest.mark.django_db
def test__api__regulation__conditions_of_sale_fulfilled(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    previous_year_last_month = this_month - relativedelta(months=2)
    regulation_month = this_month - relativedelta(years=30)

    # Create necessary indices
    MarketPriceIndexFactory.create(month=regulation_month, value=100)
    MarketPriceIndexFactory.create(month=this_month, value=200)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=5000)

    owner: Owner = OwnerFactory.create()

    # Sale for the apartment in a housing company that will be under regulation checking
    # Index adjusted price for the housing company will be: (50_000 + 10_000) / 10 * (200 / 100) = 12_000
    sale_old: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        ownerships__owner=owner,
    )

    # Sale for a new apartment for the same owner.
    sale_new: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=this_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=this_month,
        apartment__building__real_estate__housing_company__postal_code__value="00002",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        ownerships__owner=owner,
    )

    # There is a condition of sale between the apartment that will be released from regulation and the new apartment.
    condition_of_sale: ConditionOfSale = ConditionOfSaleFactory.create(
        new_ownership=sale_new.ownerships.first(),
        old_ownership=sale_old.ownerships.first(),
    )
    assert condition_of_sale.fulfilled is None

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

    create_no_external_sales_data(this_month, previous_year_last_month)

    url = reverse("hitas:thirty-year-regulation-list")

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
                id=sale_old.apartment.housing_company.uuid.hex,
                display_name=sale_old.apartment.housing_company.display_name,
                address=AddressInfo(
                    street_address=sale_old.apartment.housing_company.street_address,
                    postal_code=sale_old.apartment.housing_company.postal_code.value,
                    city=sale_old.apartment.housing_company.postal_code.city,
                ),
                price=Decimal("12000.0"),
                old_ruleset=sale_old.apartment.housing_company.hitas_type.old_hitas_ruleset,
                completion_date=regulation_month.isoformat(),
                property_manager=PropertyManagerInfo(
                    id=sale_old.apartment.housing_company.property_manager.uuid.hex,
                    name=sale_old.apartment.housing_company.property_manager.name,
                    email=sale_old.apartment.housing_company.property_manager.email,
                    last_modified=this_month.isoformat(),
                ),
                letter_fetched=False,
                current_regulation_status=RegulationStatus.RELEASED_BY_HITAS.value,
            )
        ],
        stays_regulated=[],
        skipped=[],
        # The owner is not obfuscated, since they still own the new apartment
        obfuscated_owners=[],
    )

    # When the old apartment is released from regulation, the condition of sale is fulfilled.
    condition_of_sale.refresh_from_db()
    assert condition_of_sale.fulfilled is not None


@pytest.mark.django_db
def test__api__regulation__owner_still_owns_half_hitas_apartment(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    previous_year_last_month = this_month - relativedelta(months=2)
    regulation_month = this_month - relativedelta(years=30)
    less_than_two_years_ago = this_month - relativedelta(years=2) + relativedelta(days=1)

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

    create_no_external_sales_data(this_month, previous_year_last_month)

    url = reverse("hitas:thirty-year-regulation-list")

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
                    last_modified=this_month.isoformat(),
                ),
                letter_fetched=False,
                current_regulation_status=RegulationStatus.RELEASED_BY_HITAS.value,
            )
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
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    previous_year_last_month = this_month - relativedelta(months=2)
    regulation_month = this_month - relativedelta(years=30)
    two_years_ago = this_month - relativedelta(years=2)

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

    create_no_external_sales_data(this_month, previous_year_last_month)

    url = reverse("hitas:thirty-year-regulation-list")

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
                    last_modified=this_month.isoformat(),
                ),
                letter_fetched=False,
                current_regulation_status=RegulationStatus.RELEASED_BY_HITAS.value,
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
    assert sale.apartment.housing_company.regulation_status == RegulationStatus.RELEASED_BY_HITAS
