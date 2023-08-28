import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, TypeAlias, TypedDict

from auditlog.registry import auditlog
from django.db import models
from django.utils.translation import gettext_lazy as _
from enumfields import Enum, EnumField

from hitas.models._base import HitasModel, HitasModelDecimalField

if TYPE_CHECKING:
    from hitas.models.external_sales_data import SaleData


HousingCompanyUUIDHex: TypeAlias = str  # e.g. 'dccd2cbc98264f28b097da8209441bbf'
HousingCompanyNameT: TypeAlias = str  # e.g. 'Helsingin Rumpupolun palvelutalo'
PostalCodeT: TypeAlias = str  # e.g. '33850'
QuarterT: TypeAlias = str  # e.g. '2022Q1'


class RegulationResult(Enum):
    # Housing companies that use the New Hitas ruleset.
    # Companies are automatically released after 30 years from completion
    # or Half-Hitas housing companies, which are released after 2 years from completion
    AUTOMATICALLY_RELEASED = "automatically_released"

    # Housing companies that use the Old Hitas ruleset
    # Companies are released after 30 years from completion if their €/m² is above the price for the postal code
    RELEASED_FROM_REGULATION = "released_from_regulation"

    # Housing companies that use the Old Hitas ruleset
    # Companies are not released after regulation checks, since their €/m² is below the price for the postal code
    # These may be manually released if
    STAYS_REGULATED = "stays_regulated"


class FullSalesData(TypedDict):
    internal: dict[PostalCodeT, dict[QuarterT, "SaleData"]]
    external: dict[PostalCodeT, dict[QuarterT, "SaleData"]]
    price_by_area: dict[PostalCodeT, float]


class ReplacementPostalCodes(TypedDict):
    postal_code: PostalCodeT
    replacements: list[PostalCodeT]


class ReplacementPostalCodesWithPrice(ReplacementPostalCodes):
    price_by_area: float


class ThirtyYearRegulationResultsRow(HitasModel):
    parent = models.ForeignKey("ThirtyYearRegulationResults", on_delete=models.CASCADE, related_name="rows")
    housing_company = models.ForeignKey("HousingCompany", on_delete=models.CASCADE, related_name="+")
    completion_date: datetime.date = models.DateField()
    surface_area: Decimal = HitasModelDecimalField()
    postal_code: str = models.CharField(max_length=5)
    realized_acquisition_price: Decimal = HitasModelDecimalField()
    unadjusted_average_price_per_square_meter: Optional[Decimal] = HitasModelDecimalField(null=True)
    adjusted_average_price_per_square_meter: Optional[Decimal] = HitasModelDecimalField(null=True)
    completion_month_index: Optional[Decimal] = HitasModelDecimalField(null=True)
    calculation_month_index: Optional[Decimal] = HitasModelDecimalField(null=True)
    regulation_result: RegulationResult = EnumField(RegulationResult, max_length=24)
    letter_fetched: bool = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Thirty Year Regulation Results Row")
        verbose_name_plural = _("Thirty Year Regulation Results Rows")


class ThirtyYearRegulationResultsRowPrefetched(ThirtyYearRegulationResultsRow):
    apartment_count: int
    last_modified: datetime.datetime

    class Meta:
        abstract = True


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


class ThirtyYearRegulationResults(HitasModel):
    calculation_month: datetime.date = models.DateField(unique=True)
    regulation_month: datetime.date = models.DateField()
    surface_area_price_ceiling: Optional[Decimal] = HitasModelDecimalField(null=True)
    sales_data: FullSalesData = models.JSONField()
    replacement_postal_codes: list[ReplacementPostalCodesWithPrice] = models.JSONField()

    class Meta:
        verbose_name = _("Thirty Year Regulation Results")
        verbose_name_plural = _("Thirty Year Regulation Results")

    def __str__(self) -> str:
        return f"Thirty-year regulation results for {self.calculation_month.isoformat()!r}"


auditlog.register(ThirtyYearRegulationResultsRow)
auditlog.register(ThirtyYearRegulationResults)
