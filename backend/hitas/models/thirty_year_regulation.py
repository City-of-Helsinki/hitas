import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, TypeAlias, TypedDict

from django.db import models
from django.utils.translation import gettext_lazy as _
from enumfields import Enum, EnumField

from hitas.models._base import HitasModelDecimalField

if TYPE_CHECKING:
    from hitas.models.external_sales_data import SaleData


HousingCompanyUUIDHex: TypeAlias = str  # e.g. 'dccd2cbc98264f28b097da8209441bbf'
HousingCompanyNameT: TypeAlias = str  # e.g. 'Helsingin Rumpupolun palvelutalo'
PostalCodeT: TypeAlias = str  # e.g. '33850'
QuarterT: TypeAlias = str  # e.g. '2022Q1'


class RegulationResult(Enum):
    AUTOMATICALLY_RELEASED = "automatically_released"
    RELEASED_FROM_REGULATION = "released_from_regulation"
    STAYS_REGULATED = "stays_regulated"


class FullSalesData(TypedDict):
    internal: dict[PostalCodeT, dict[QuarterT, "SaleData"]]
    external: dict[PostalCodeT, dict[QuarterT, "SaleData"]]
    price_by_area: dict[PostalCodeT, float]


class ThirtyYearRegulationResultsRow(models.Model):
    parent = models.ForeignKey("ThirtyYearRegulationResults", on_delete=models.CASCADE, related_name="rows")
    housing_company = models.ForeignKey("HousingCompany", on_delete=models.CASCADE, related_name="+")
    completion_date = models.DateField()
    surface_area = HitasModelDecimalField()
    postal_code = models.CharField(max_length=5)
    realized_acquisition_price = HitasModelDecimalField()
    unadjusted_average_price_per_square_meter = HitasModelDecimalField(null=True)
    adjusted_average_price_per_square_meter = HitasModelDecimalField(null=True)
    completion_month_index = HitasModelDecimalField(null=True)
    calculation_month_index = HitasModelDecimalField(null=True)
    regulation_result = EnumField(RegulationResult, max_length=24)

    class Meta:
        verbose_name = _("Thirty Year Regulation Results Row")
        verbose_name_plural = _("Thirty Year Regulation Results Rows")


class ThirtyYearRegulationResultsRowWithAnnotations(ThirtyYearRegulationResultsRow):
    check_count: int
    min_share: int
    max_share: int
    share_count: int
    apartment_count: int
    completion_month: datetime.date
    completion_month_index_cpi: Decimal
    calculation_month_index_cpi: Decimal
    average_price_per_square_meter_cpi: Decimal
    turned_30: datetime.date
    difference: Decimal

    class Meta:
        abstract = True


class ThirtyYearRegulationResults(models.Model):
    calculation_month = models.DateField(unique=True)
    regulation_month = models.DateField()
    surface_area_price_ceiling = HitasModelDecimalField(null=True)
    sales_data: FullSalesData = models.JSONField()

    class Meta:
        verbose_name = _("Thirty Year Regulation Results")
        verbose_name_plural = _("Thirty Year Regulation Results")

    def __str__(self) -> str:
        return f"Thirty-year regulation results for {self.calculation_month.isoformat()!r}"
