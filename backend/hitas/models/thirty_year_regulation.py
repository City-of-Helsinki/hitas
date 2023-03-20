from typing import TYPE_CHECKING, TypeAlias, TypedDict

from django.db import models
from django.utils.translation import gettext_lazy as _
from enumfields import Enum, EnumField

from hitas.models._base import HitasModelDecimalField

if TYPE_CHECKING:
    from hitas.models.external_sales_data import SaleData

HousingCompanyUUID: TypeAlias = str
HousingCompanyNameT: TypeAlias = str
PostalCodeT: TypeAlias = str
QuarterT: TypeAlias = str


class RegulationResult(Enum):
    AUTOMATICALLY_RELEASED = "automatically_released"
    RELEASED_FROM_REGULATION = "released_from_regulation"
    STAYS_REGULATED = "stays_regulated"
    SKIPPED = "skipped"


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


class ThirtyYearRegulationResults(models.Model):
    calculation_month = models.DateField()
    regulation_month = models.DateField()
    surface_area_price_ceiling = HitasModelDecimalField(null=True)
    sales_data: FullSalesData = models.JSONField()

    class Meta:
        verbose_name = _("Thirty Year Regulation Results")
        verbose_name_plural = _("Thirty Year Regulation Results")

    def __str__(self) -> str:
        return f"Thirty year regulation results for {self.calculation_month.isoformat()!r}"
