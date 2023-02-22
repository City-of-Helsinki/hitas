from typing import TypedDict

from django.db import models
from django.utils.translation import gettext_lazy as _


class CostAreaData(TypedDict):
    postal_code: str
    sale_count: int
    price: int


class QuarterData(TypedDict):
    quarter: str
    areas: list[CostAreaData]


class ExternalSalesDataType(TypedDict):
    calculation_quarter: str
    quarter_1: QuarterData
    quarter_2: QuarterData
    quarter_3: QuarterData
    quarter_4: QuarterData


class ExternalSalesData(models.Model):
    """Data pulled from tilastokeskus excel for surface area price ceiling calculation"""

    calculation_quarter = models.CharField(primary_key=True, max_length=6)
    quarter_1: QuarterData = models.JSONField()  # previous-previous-previous quarter
    quarter_2: QuarterData = models.JSONField()  # previous-previous quarter
    quarter_3: QuarterData = models.JSONField()  # previous quarter
    quarter_4: QuarterData = models.JSONField()  # most recent quarter = calculation quarter data

    def __str__(self):
        return f"{self.calculation_quarter} external sales data"

    class Meta:
        verbose_name = _("External sales data")
        verbose_name_plural = _("External sales datas")
