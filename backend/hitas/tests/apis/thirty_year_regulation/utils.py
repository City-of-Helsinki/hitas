import datetime

from dateutil.relativedelta import relativedelta

from hitas.models import ExternalSalesData
from hitas.models.external_sales_data import QuarterData
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
