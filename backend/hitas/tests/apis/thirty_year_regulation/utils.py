import datetime

from dateutil.relativedelta import relativedelta

from hitas.models import ApartmentSale, ExternalSalesData
from hitas.models.external_sales_data import QuarterData
from hitas.models.housing_company import HitasType, RegulationStatus
from hitas.tests.factories import ApartmentSaleFactory
from hitas.tests.factories.indices import MarketPriceIndexFactory, SurfaceAreaPriceCeilingFactory
from hitas.utils import to_quarter


def create_no_external_sales_data(this_month, previous_year_last_month):
    """Create necessary external sales data (no external sales)"""

    ExternalSalesData.objects.create(
        calculation_quarter=to_quarter(this_month),
        quarter_1=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=9)), areas=[]),
        quarter_2=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=6)), areas=[]),
        quarter_3=QuarterData(quarter=to_quarter(previous_year_last_month - relativedelta(months=3)), areas=[]),
        quarter_4=QuarterData(quarter=to_quarter(previous_year_last_month), areas=[]),
    )


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
