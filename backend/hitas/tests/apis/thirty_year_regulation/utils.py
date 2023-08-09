import datetime
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.utils import timezone

from hitas.models import ApartmentSale, ExternalSalesData
from hitas.models.external_sales_data import CostAreaData, QuarterData
from hitas.models.housing_company import HitasType, RegulationStatus
from hitas.services.thirty_year_regulation import AddressInfo, ComparisonData, PropertyManagerInfo
from hitas.tests.factories import ApartmentFactory, ApartmentSaleFactory
from hitas.tests.factories.indices import MarketPriceIndexFactory, SurfaceAreaPriceCeilingFactory
from hitas.utils import to_quarter


def get_relevant_dates(freezer):
    """Set date to 2023-02-01 and return relevant dates for the test"""
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    this_month = day.date()
    previous_year_last_month = this_month - relativedelta(months=2)
    regulation_month = this_month - relativedelta(years=30)

    return this_month, previous_year_last_month, regulation_month


def create_necessary_indices(this_month, regulation_month, skip_surface_area_price_ceiling=False):
    """Create common necessary indices for the tests"""
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


def create_new_apartment(date, postal_code="00001", hitas_type=HitasType.HITAS_I, **kwargs) -> ApartmentSale:
    return ApartmentFactory.create(
        completion_date=date,
        sales__purchase_date=date,  # First sale for the apartment is not counted
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


def create_no_external_sales_data(calculation_quarter_date, previous_year_last_month):
    """Create necessary external sales data (no external sales)"""

    return ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(calculation_quarter_date),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=3)), areas=[]),
        quarter_4=QuarterData(quarter=to_quarter(previous_year_last_month), areas=[]),
    )


def create_external_sales_data_for_postal_code(calculation_quarter, previous_year_last_month, postal_code):
    external_sales_data = create_no_external_sales_data(calculation_quarter, previous_year_last_month)

    # Average sales price will be: (15_000 + 30_000) / (1 + 2) = 15_000
    external_sales_data.quarter_3["areas"] = [CostAreaData(postal_code=postal_code, sale_count=1, price=15_000)]
    external_sales_data.quarter_4["areas"] = [CostAreaData(postal_code=postal_code, sale_count=2, price=30_000)]
    external_sales_data.save()
