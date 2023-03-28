import datetime
import logging
from decimal import Decimal
from typing import Literal, NamedTuple, Optional

from dateutil.relativedelta import relativedelta
from django.db.models import Case, OuterRef, Q, Subquery, When
from openpyxl.styles import Alignment, Border, Side
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from hitas.exceptions import HitasModelNotFound, ModelConflict
from hitas.models import (
    ConstructionPriceIndex,
    ConstructionPriceIndex2005Equal100,
    HousingCompanyState,
    SurfaceAreaPriceCeiling,
)
from hitas.models._base import HitasModelDecimalField
from hitas.models.housing_company import HousingCompanyWithAnnotations
from hitas.models.indices import (
    CalculationData,
    HousingCompanyData,
    SurfaceAreaPriceCeilingCalculationData,
    SurfaceAreaPriceCeilingResult,
)
from hitas.services.housing_company import get_completed_housing_companies, make_index_adjustment_for_housing_companies
from hitas.utils import format_sheet, hitas_calculation_quarter, resize_columns, roundup

logger = logging.getLogger()


class ReportColumns(NamedTuple):
    display_name: str
    acquisition_price: Decimal | str
    indices: str
    change: Decimal | str
    adjusted_acquisition_price: Decimal | str
    surface_area: Decimal | str
    price_per_square_meter: Decimal | str


def calculate_surface_area_price_ceiling(calculation_date: datetime.date) -> list[SurfaceAreaPriceCeilingResult]:
    calculation_month = hitas_calculation_quarter(calculation_date)

    logger.info(f"Calculating surface area price ceiling for {calculation_month.isoformat()!r}...")

    logger.info("Fetching housing companies...")
    housing_companies = get_completed_housing_companies(
        completion_month=calculation_month,
        states=[
            HousingCompanyState.LESS_THAN_30_YEARS,
            HousingCompanyState.GREATER_THAN_30_YEARS_NOT_FREE,
        ],
    )

    if not housing_companies:
        raise ModelConflict(
            f"No housing companies completed before {calculation_date.isoformat()!r} or all have wrong state.",
            error_code="missing",
        )

    unadjusted_prices: dict[str, Optional[Decimal]] = {
        housing_company.uuid.hex: housing_company.avg_price_per_square_meter for housing_company in housing_companies
    }

    logger.info("Making index adjustments...")
    indices = make_index_adjustment_for_housing_companies(housing_companies, calculation_month)

    logger.info(
        f"Setting surface area price ceiling for the next three months "
        f"starting from {calculation_month.isoformat()!r}..."
    )
    total = _calculate_surface_area_price_ceiling_for_housing_companies(housing_companies)
    results = _create_surface_area_price_ceiling_for_next_three_months(calculation_month, total)

    logger.info("Saving calculation data for later use...")
    _save_calculation_data(calculation_month, housing_companies, indices, unadjusted_prices, results)

    logger.info("Surface area price ceiling calculation complete!")
    return results


def _calculate_surface_area_price_ceiling_for_housing_companies(
    housing_companies: list[HousingCompanyWithAnnotations],
) -> Decimal:
    total: Decimal = sum((housing_company.avg_price_per_square_meter for housing_company in housing_companies))
    return roundup(total / len(housing_companies), precision=0)


def _create_surface_area_price_ceiling_for_next_three_months(
    from_: datetime.date,
    value: Decimal,
) -> list[SurfaceAreaPriceCeilingResult]:
    results: list[SurfaceAreaPriceCeilingResult] = []
    for month in range(3):
        surface_area_price_ceiling, _ = SurfaceAreaPriceCeiling.objects.update_or_create(
            month=from_ + relativedelta(months=month),
            defaults={"value": value},
        )
        results.append(
            SurfaceAreaPriceCeilingResult(
                month=surface_area_price_ceiling.month.isoformat()[:-3],
                value=float(surface_area_price_ceiling.value),
            )
        )
    return results


def _save_calculation_data(
    calculation_month: datetime.date,
    housing_companies: list[HousingCompanyWithAnnotations],
    indices: dict[Literal["old", "new"], dict[datetime.date, Decimal]],
    unadjusted_prices: dict[str, Optional[Decimal]],
    surface_area_price_ceilings: list[SurfaceAreaPriceCeilingResult],
) -> tuple[SurfaceAreaPriceCeilingCalculationData, bool]:
    data = CalculationData(
        housing_company_data=[
            HousingCompanyData(
                name=housing_company.display_name,
                completion_date=housing_company.completion_date.isoformat(),
                surface_area=float(housing_company.surface_area),
                realized_acquisition_price=float(housing_company.realized_acquisition_price),
                unadjusted_average_price_per_square_meter=float(unadjusted_prices[housing_company.uuid.hex]),
                adjusted_average_price_per_square_meter=float(housing_company.avg_price_per_square_meter),
                completion_month_index=float(indices[key][housing_company.completion_month]),
                calculation_month_index=float(indices[key][calculation_month]),
            )
            for housing_company in housing_companies
            if (key := "old" if housing_company.financing_method.old_hitas_ruleset else "new")
        ],
        created_surface_area_price_ceilings=surface_area_price_ceilings,
    )
    return SurfaceAreaPriceCeilingCalculationData.objects.update_or_create(
        calculation_month=calculation_month,
        defaults={"data": data},
    )


def subquery_appropriate_cpi(outer_ref: str, financing_method_ref: str) -> Case:
    """
    Make a subquery for appropriate construction price index based on housing company's financing method.
    """
    return Case(
        When(
            condition=Q(**{f"{financing_method_ref}__old_hitas_ruleset": True}),
            then=(
                Subquery(
                    queryset=(ConstructionPriceIndex.objects.filter(month=OuterRef(outer_ref)).values("value")[:1]),
                    output_field=HitasModelDecimalField(),
                )
            ),
        ),
        default=(
            Subquery(
                queryset=(
                    ConstructionPriceIndex2005Equal100.objects.filter(month=OuterRef(outer_ref)).values("value")[:1]
                ),
                output_field=HitasModelDecimalField(),
            )
        ),
    )


def get_surface_area_price_ceiling_results(calculation_date: datetime.date) -> SurfaceAreaPriceCeilingCalculationData:
    try:
        return SurfaceAreaPriceCeilingCalculationData.objects.get(
            calculation_month=hitas_calculation_quarter(calculation_date),
        )
    except SurfaceAreaPriceCeilingCalculationData.DoesNotExist as error:
        raise HitasModelNotFound(SurfaceAreaPriceCeilingCalculationData) from error


def build_surface_area_price_ceiling_report_excel(results: SurfaceAreaPriceCeilingCalculationData) -> Workbook:
    workbook = Workbook()
    worksheet: Worksheet = workbook.active

    columns = ReportColumns(
        display_name="Yhtiö",
        acquisition_price="Hankinta-arvo",
        indices="Indeksit",
        change="Muutos",
        adjusted_acquisition_price="Takistettu hinta",
        surface_area="Pinta-ala",
        price_per_square_meter="E-hinta/m²",
    )
    worksheet.append(columns)

    for housing_company in results.data["housing_company_data"]:
        unadjusted = Decimal(housing_company["unadjusted_average_price_per_square_meter"])
        adjusted = Decimal(housing_company["adjusted_average_price_per_square_meter"])
        surface_area = Decimal(housing_company["surface_area"])
        data = ReportColumns(
            display_name=housing_company["name"],
            acquisition_price=Decimal(housing_company["realized_acquisition_price"]),
            indices=f"{housing_company['completion_month_index']}/{housing_company['calculation_month_index']}",
            change=(adjusted * surface_area) - (unadjusted * surface_area),
            adjusted_acquisition_price=adjusted * surface_area,
            surface_area=surface_area,
            price_per_square_meter=adjusted,
        )
        worksheet.append(data)

    last_row = worksheet.max_row
    worksheet.auto_filter.ref = worksheet.dimensions

    # There needs to be an empty row for sorting and filtering to work properly
    worksheet.append(
        ReportColumns(
            display_name="",
            acquisition_price="",
            indices="",
            change="",
            adjusted_acquisition_price="",
            surface_area="",
            price_per_square_meter="",
        )
    )

    summary_start = worksheet.max_row + 1
    summary_rows = {"Summa": "SUM", "Keskiarvo": "AVERAGE", "Mediaani": "MEDIAN"}
    for title, formula in summary_rows.items():
        worksheet.append(
            ReportColumns(
                display_name=title,
                acquisition_price=f"={formula}(B2:B{last_row})",
                indices="",
                change=f"={formula}(D2:D{last_row})",
                adjusted_acquisition_price=f"={formula}(E2:E{last_row})",
                surface_area=f"={formula}(F2:F{last_row})",
                price_per_square_meter=f"={formula}(G2:G{last_row})",
            )
        )
    summary_end = worksheet.max_row

    worksheet.append(
        ReportColumns(
            display_name="Rajaneliöhinta",
            acquisition_price=Decimal(results.data["created_surface_area_price_ceilings"][0]["value"]),
            indices="",
            change="",
            adjusted_acquisition_price="",
            surface_area="",
            price_per_square_meter="",
        )
    )

    format_sheet(
        worksheet,
        formatting_rules={
            # Add a border to the header row
            **{f"{letter}1": {"border": Border(bottom=Side(style="thin"))} for letter in "ABCDEFG"},
            # Add a border to the last data row
            **{f"{letter}{last_row}": {"border": Border(bottom=Side(style="thin"))} for letter in "ABCDEFG"},
            # Align the summary titles to the right
            **{
                f"A{summary_start + i}": {"alignment": Alignment(horizontal="right")}
                for i in range(0, len(summary_rows) + 1)  # additional +1 for "Rajaneliöhinta" row
            },
            # Add border to the end of the summary row
            **{f"{letter}{summary_end}": {"border": Border(bottom=Side(style="thin"))} for letter in "BCDEFG"},
            # Last summary row needs both underline and alignment
            f"A{summary_end}": {
                "border": Border(bottom=Side(style="thin")),
                "alignment": Alignment(horizontal="right"),
            },
            "B": {"number_format": "#,##0.00\\ €"},
            "C": {"alignment": Alignment(horizontal="right")},
            "D": {"number_format": "#,##0.00\\ €"},
            "E": {"number_format": "#,##0.00\\ €"},
            "F": {"number_format": "#,##0.00\\ \\m\\²"},
            "G": {"number_format": "#,##0.00\\ €"},
        },
    )

    resize_columns(worksheet)
    worksheet.protection.sheet = True
    return workbook
