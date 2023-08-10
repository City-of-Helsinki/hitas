import datetime
from decimal import Decimal
from typing import Optional

from dateutil.relativedelta import relativedelta
from django.utils import timezone

from hitas.models import ApartmentSale, ExternalSalesData
from hitas.models.external_sales_data import CostAreaData, QuarterData
from hitas.models.housing_company import HitasType, RegulationStatus
from hitas.services.thirty_year_regulation import AddressInfo, ComparisonData, PropertyManagerInfo
from hitas.tests.factories import ApartmentFactory, ApartmentSaleFactory
from hitas.tests.factories.indices import MarketPriceIndexFactory, SurfaceAreaPriceCeilingFactory
from hitas.utils import to_quarter


def get_relevant_dates(freezer=None):
    """Set date to 2023-02-01 and return relevant dates for the test"""
    day = datetime.datetime(2023, 2, 1)
    if freezer is not None:
        freezer.move_to(day)

    this_month = day.date()
    two_months_ago = this_month - relativedelta(months=2)
    regulation_month = this_month - relativedelta(years=30)

    return this_month, two_months_ago, regulation_month


def create_necessary_indices(skip_surface_area_price_ceiling=False):
    """Create common necessary indices for the tests"""
    this_month, _, regulation_month = get_relevant_dates()

    MarketPriceIndexFactory.create(month=regulation_month, value=100)
    MarketPriceIndexFactory.create(month=this_month, value=200)
    if not skip_surface_area_price_ceiling:
        SurfaceAreaPriceCeilingFactory.create(month=this_month, value=5000)


def create_apartment_sale_for_date(date, postal_code="00001", hitas_type=HitasType.HITAS_I, **kwargs) -> ApartmentSale:
    """
    Sale for the apartment in a housing company that will be under regulation checking
    Index adjusted price/m² for the apartment will be: (50_000 + 10_000) / 10 * (200 / 100) = 12_000
    """
    return ApartmentSaleFactory.create(
        purchase_date=date,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=date,
        apartment__building__real_estate__housing_company__postal_code__value=postal_code,
        apartment__building__real_estate__housing_company__hitas_type=hitas_type,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        **kwargs,
    )


def create_new_apartment(
    completion_date: Optional[datetime.date] = None, postal_code="00001", hitas_type=HitasType.HITAS_I, **kwargs
) -> ApartmentSale:
    """
    Create a new apartment that will be under regulation checking.
    By default, the apartment is completed two months ago and has a first sale on the same date
    The first sale is not counted in the regulation checking, but is needed to count any later sales for the apartment
    """
    if completion_date is None:
        _, two_months_ago, _ = get_relevant_dates()
        completion_date = two_months_ago

    return ApartmentFactory.create(
        completion_date=completion_date,
        sales__purchase_date=completion_date,  # First sale for the apartment is not counted
        building__real_estate__housing_company__postal_code__value=postal_code,
        building__real_estate__housing_company__hitas_type=hitas_type,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        **kwargs,
    )


def get_comparison_data_for_single_housing_company(
    housing_company,
    regulation_month,
    price="12000.0",
    current_regulation_status=RegulationStatus.REGULATED,
    letter_fetched=False,
):
    """Util to remove boilerplate code from the tests"""
    return ComparisonData(
        # Housing Company data
        id=housing_company.uuid.hex,
        display_name=housing_company.display_name,
        address=AddressInfo(
            street_address=housing_company.street_address,
            postal_code=housing_company.postal_code.value,
            city=housing_company.postal_code.city,
        ),
        old_ruleset=housing_company.hitas_type.old_hitas_ruleset,
        property_manager=PropertyManagerInfo(
            id=housing_company.property_manager.uuid.hex,
            name=housing_company.property_manager.name,
            email=housing_company.property_manager.email,
            last_modified=timezone.now().date().isoformat(),
        ),
        # Comparison data
        completion_date=regulation_month.isoformat(),
        price=Decimal(price),
        current_regulation_status=current_regulation_status.value,
        letter_fetched=letter_fetched,
    )


def create_no_external_sales_data() -> ExternalSalesData:
    """
    Create an empty external sales data object (no external sales)
    This is needed to run the regulation
    """
    this_month, two_months_ago, _ = get_relevant_dates()

    return ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(this_month),
        quarter_1=QuarterData(quarter=to_quarter(two_months_ago - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(two_months_ago - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(quarter=to_quarter(two_months_ago - relativedelta(months=3)), areas=[]),
        quarter_4=QuarterData(quarter=to_quarter(two_months_ago), areas=[]),
    )


def create_external_sales_data_for_postal_code(postal_code):
    """Create some external sales data for a given postal code"""
    external_sales_data = create_no_external_sales_data()

    # Average sales price will be: (15_000 + 30_000) / (1 + 2) = 15_000
    external_sales_data.quarter_3["areas"] = [CostAreaData(postal_code=postal_code, sale_count=1, price=15_000)]
    external_sales_data.quarter_4["areas"] = [CostAreaData(postal_code=postal_code, sale_count=2, price=30_000)]
    external_sales_data.save()
