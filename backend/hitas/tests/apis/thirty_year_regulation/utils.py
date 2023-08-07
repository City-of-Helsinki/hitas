from dateutil.relativedelta import relativedelta

from hitas.models import ExternalSalesData
from hitas.models.external_sales_data import QuarterData
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
