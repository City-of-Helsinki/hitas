import datetime
import string
from decimal import Decimal
from enum import Enum
from functools import cache
from statistics import mean
from typing import Any, Callable, Iterable, NamedTuple, TypedDict, TypeVar

from openpyxl.styles import Alignment, Border, Side
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings

from hitas.models import ApartmentSale
from hitas.models.housing_company import (
    HitasType,
    HousingCompanyWithRegulatedReportAnnotations,
    HousingCompanyWithStateReportAnnotations,
    HousingCompanyWithUnregulatedReportAnnotations,
    RegulationStatus,
)
from hitas.utils import format_sheet, resize_columns


class SalesReportColumns(NamedTuple):
    cost_area: int | str
    postal_code: str
    apartment_address: str
    notification_date: datetime.date | str
    purchase_date: datetime.date | str
    purchase_price_per_square_meter: Decimal | str
    total_price_per_square_meter: Decimal | str


class RegulatedHousingCompaniesReportColumns(NamedTuple):
    cost_area: int | str
    postal_code: str
    housing_company_name: str
    address: str
    completion_date: datetime.date | str
    apartment_count: int | str
    average_price_per_square_meter: Decimal | str


class UnregulatedHousingCompaniesReportColumns(NamedTuple):
    housing_company_name: str
    postal_code: str | int
    completion_date: datetime.date | str
    release_date: datetime.date | str
    released_by_ploy_department: str
    apartment_count: int | str


class HousingCompanyStatesCount(TypedDict):
    housing_company_count: int
    apartment_count: int


class HousingCompanyStatesReportColumns(NamedTuple):
    state: str
    housing_company_count: int | str
    apartment_count: int | str


T = TypeVar("T")


class SalesReportSummaryDefinition(NamedTuple):
    func: Callable[[Iterable[T]], T]
    title: str = ""
    subtitle: str = ""


class ReportState(str, Enum):
    NOT_READY = "Ei valmis"
    REGULATED = "Sääntelyn piirissä"
    RELEASED_BY_HITAS = "Sääntelystä vapautuneet"
    RELEASED_BY_PLOT_DEPARTMENT = "Vapautuneet tontit-yksikön päätöksellä"
    HALF_HITAS = "Puoli-Hitas yhtiöt"


def build_sales_report_excel(sales: list[ApartmentSale]) -> Workbook:
    workbook = Workbook()
    worksheet: Worksheet = workbook.active

    column_headers = SalesReportColumns(
        cost_area="Kalleusalue",
        postal_code="Postinumero",
        apartment_address="Osoite",
        notification_date="Ilmoituspäivä",
        purchase_date="Kauppapäivä",
        purchase_price_per_square_meter="Kaupan neliöhinta",
        total_price_per_square_meter="Velaton neliöhinta",
    )
    worksheet.append(column_headers)

    for sale in sales:
        if not sale.apartment.surface_area:
            raise ValidationError(
                detail={
                    api_settings.NON_FIELD_ERRORS_KEY: (
                        f"Surface are zero or missing for apartment {sale.apartment.address!r}. "
                        f"Cannot calculate price per square meter."
                    )
                },
            )

        worksheet.append(
            SalesReportColumns(
                cost_area=sale.apartment.postal_code.cost_area,
                postal_code=sale.apartment.postal_code.value,
                apartment_address=sale.apartment.address,
                notification_date=sale.notification_date,
                purchase_date=sale.purchase_date,
                purchase_price_per_square_meter=sale.purchase_price / sale.apartment.surface_area,
                total_price_per_square_meter=sale.total_price / sale.apartment.surface_area,
            )
        )

    last_row = worksheet.max_row
    worksheet.auto_filter.ref = worksheet.dimensions

    empty_row = SalesReportColumns(
        cost_area="",
        postal_code="",
        apartment_address="",
        notification_date="",
        purchase_date="",
        purchase_price_per_square_meter="",
        total_price_per_square_meter="",
    )

    # There needs to be an empty row for sorting and filtering to work properly
    worksheet.append(empty_row)

    @cache
    def unwrap_range(cell_range: str) -> list[Any]:
        return [cell.value for row in worksheet[cell_range] for cell in row]

    @cache
    def conditional_range(value_range: str, **comparison_ranges_to_values: Any) -> list[Any]:
        """
        Returns values from `value_range` where the given comparison ranges
        contain all values as indicated by the mapping.
        """
        comparison_values: list[Any] = list(comparison_ranges_to_values.values())
        unwrapped_comparison_ranges = zip(*(unwrap_range(rang) for rang in comparison_ranges_to_values))
        zipped_ranges = zip(unwrap_range(value_range), unwrapped_comparison_ranges, strict=True)
        return [
            value
            for value, range_values in zipped_ranges
            if all(range_value == comparison_values[i] for i, range_value in enumerate(range_values))
        ]

    summary_start = worksheet.max_row + 1

    summary_rows: list[SalesReportSummaryDefinition] = [
        SalesReportSummaryDefinition(
            title="Kaikki kaupat",
            subtitle="Lukumäärä",
            func=lambda x: len(unwrap_range(x)),
        ),
        SalesReportSummaryDefinition(
            subtitle="Summa",
            func=lambda x: sum(unwrap_range(x)),
        ),
        SalesReportSummaryDefinition(
            subtitle="Keskiarvo",
            func=lambda x: mean(unwrap_range(x) or [0]),
        ),
        SalesReportSummaryDefinition(
            subtitle="Maksimi",
            func=lambda x: max(unwrap_range(x), default=0),
        ),
        SalesReportSummaryDefinition(
            subtitle="Minimi",
            func=lambda x: min(unwrap_range(x), default=0),
        ),
    ]

    for cost_area in range(1, 5):
        summary_rows += [
            None,  # empty row
            SalesReportSummaryDefinition(
                title=f"Kalleusalue {cost_area}",
                subtitle="Lukumäärä",
                func=lambda x, y=cost_area: len(conditional_range(x, **{f"A2:A{last_row}": y})),
            ),
            SalesReportSummaryDefinition(
                subtitle="Summa",
                func=lambda x, y=cost_area: sum(conditional_range(x, **{f"A2:A{last_row}": y})),
            ),
            SalesReportSummaryDefinition(
                subtitle="Keskiarvo",
                func=lambda x, y=cost_area: mean(conditional_range(x, **{f"A2:A{last_row}": y}) or [0]),
            ),
            SalesReportSummaryDefinition(
                subtitle="Maksimi",
                func=lambda x, y=cost_area: max(conditional_range(x, **{f"A2:A{last_row}": y}), default=0),
            ),
            SalesReportSummaryDefinition(
                subtitle="Minimi",
                func=lambda x, y=cost_area: min(conditional_range(x, **{f"A2:A{last_row}": y}), default=0),
            ),
        ]

    sales_count_rows: list[int] = []

    for definition in summary_rows:
        if definition is None:
            worksheet.append(empty_row)
            continue

        if definition.subtitle == "Lukumäärä":
            sales_count_rows.append(worksheet.max_row + 1)

        worksheet.append(
            SalesReportColumns(
                cost_area="",
                postal_code="",
                apartment_address="",
                notification_date=definition.title,
                purchase_date=definition.subtitle,
                purchase_price_per_square_meter=definition.func(f"F2:F{last_row}"),
                total_price_per_square_meter=definition.func(f"G2:G{last_row}"),
            ),
        )

    euro_per_square_meter_format = "#,##0.00\\ \\€\\/\\m²"
    date_format = "DD.MM.YYYY"
    column_letters = string.ascii_uppercase[: len(column_headers)]

    format_sheet(
        worksheet,
        formatting_rules={
            # Add a border to the header row
            **{f"{letter}1": {"border": Border(bottom=Side(style="thin"))} for letter in column_letters},
            # Add a border to the last data row
            **{f"{letter}{last_row}": {"border": Border(bottom=Side(style="thin"))} for letter in column_letters},
            # Align the summary titles to the right
            **{
                f"E{summary_start + i}": {"alignment": Alignment(horizontal="right")}
                for i in range(0, len(summary_rows))
            },
            "B": {"alignment": Alignment(horizontal="right")},
            "D": {"number_format": date_format},
            "E": {"number_format": date_format},
            "F": {"number_format": euro_per_square_meter_format},
            "G": {"number_format": euro_per_square_meter_format},
            # Reset number format for sales count cells
            **{f"{letter}{row}": {"number_format": "General"} for row in sales_count_rows for letter in "FG"},
        },
    )

    resize_columns(worksheet)
    worksheet.protection.sheet = True
    return workbook


def build_regulated_housing_companies_report_excel(
    housing_companies: list[HousingCompanyWithRegulatedReportAnnotations],
) -> Workbook:
    workbook = Workbook()
    worksheet: Worksheet = workbook.active

    column_headers = RegulatedHousingCompaniesReportColumns(
        cost_area="Kalleusalue",
        postal_code="Postinumero",
        housing_company_name="Yhtiö",
        address="Osoite",
        completion_date="Valmistumispäivä",
        apartment_count="Asuntojen lukumäärä",
        average_price_per_square_meter="Keskineliöhinta",
    )
    worksheet.append(column_headers)

    for housing_company in housing_companies:
        worksheet.append(
            RegulatedHousingCompaniesReportColumns(
                cost_area=housing_company.postal_code.cost_area,
                postal_code=housing_company.postal_code.value,
                housing_company_name=housing_company.display_name,
                address=housing_company.street_address,
                completion_date=housing_company.completion_date,
                apartment_count=housing_company.apartment_count,
                average_price_per_square_meter=housing_company.avg_price_per_square_meter,
            ),
        )

    last_row = worksheet.max_row
    worksheet.auto_filter.ref = worksheet.dimensions

    empty_row = RegulatedHousingCompaniesReportColumns(
        cost_area="",
        postal_code="",
        housing_company_name="",
        address="",
        completion_date="",
        apartment_count="",
        average_price_per_square_meter="",
    )

    # There needs to be an empty row for sorting and filtering to work properly
    worksheet.append(empty_row)

    euro_per_square_meter_format = "#,##0.00\\ \\€\\/\\m²"
    date_format = "DD.MM.YYYY"
    column_letters = string.ascii_uppercase[: len(column_headers)]

    format_sheet(
        worksheet,
        formatting_rules={
            # Add a border to the header row
            **{f"{letter}1": {"border": Border(bottom=Side(style="thin"))} for letter in column_letters},
            # Add a border to the last data row
            **{f"{letter}{last_row}": {"border": Border(bottom=Side(style="thin"))} for letter in column_letters},
            "B": {"alignment": Alignment(horizontal="right")},
            "E": {"number_format": date_format},
            "G": {"number_format": euro_per_square_meter_format},
        },
    )

    resize_columns(worksheet)
    worksheet.protection.sheet = True
    return workbook


def build_unregulated_housing_companies_report_excel(
    housing_companies: list[HousingCompanyWithUnregulatedReportAnnotations],
) -> Workbook:
    workbook = Workbook()
    worksheet: Worksheet = workbook.active

    column_headers = UnregulatedHousingCompaniesReportColumns(
        housing_company_name="Yhtiö",
        postal_code="Postinumero",
        completion_date="Valmistumispäivä",
        release_date="Vapautumispäivä",
        released_by_ploy_department="Vapautettu tontit yksikön toimesta?",
        apartment_count="Asuntojen lukumäärä",
    )
    worksheet.append(column_headers)

    for housing_company in housing_companies:
        worksheet.append(
            UnregulatedHousingCompaniesReportColumns(
                housing_company_name=housing_company.display_name,
                postal_code=housing_company.postal_code.value,
                completion_date=housing_company.completion_date,
                release_date=housing_company.release_date,
                released_by_ploy_department=(
                    "X" if housing_company.regulation_status == RegulationStatus.RELEASED_BY_PLOT_DEPARTMENT else ""
                ),
                apartment_count=housing_company.apartment_count,
            )
        )

    last_row = worksheet.max_row
    worksheet.auto_filter.ref = worksheet.dimensions

    empty_row = UnregulatedHousingCompaniesReportColumns(
        housing_company_name="",
        postal_code="",
        completion_date="",
        release_date="",
        released_by_ploy_department="",
        apartment_count="",
    )

    # There needs to be an empty row for sorting and filtering to work properly
    worksheet.append(empty_row)

    # Add summary rows
    worksheet.append(
        UnregulatedHousingCompaniesReportColumns(
            housing_company_name="Taloyhtiötä yhteensä",
            postal_code=len(housing_companies),
            completion_date="",
            release_date="",
            released_by_ploy_department="",
            apartment_count="",
        ),
    )
    worksheet.append(
        UnregulatedHousingCompaniesReportColumns(
            housing_company_name="Asuntoja yhteensä",
            postal_code=sum(housing_company.apartment_count for housing_company in housing_companies),
            completion_date="",
            release_date="",
            released_by_ploy_department="",
            apartment_count="",
        ),
    )

    date_format = "DD.MM.YYYY"
    column_letters = string.ascii_uppercase[: len(column_headers)]

    format_sheet(
        worksheet,
        formatting_rules={
            # Add a border to the header row
            **{f"{letter}1": {"border": Border(bottom=Side(style="thin"))} for letter in column_letters},
            # Add a border to the last data row
            **{f"{letter}{last_row}": {"border": Border(bottom=Side(style="thin"))} for letter in column_letters},
            "B": {"alignment": Alignment(horizontal="right")},
            "C": {"number_format": date_format},
            "D": {"number_format": date_format},
        },
    )

    resize_columns(worksheet)
    worksheet.protection.sheet = True
    return workbook


def build_housing_company_state_report_excel(
    housing_companies: list[HousingCompanyWithStateReportAnnotations],
) -> Workbook:
    workbook = Workbook()
    worksheet: Worksheet = workbook.active

    column_headers = HousingCompanyStatesReportColumns(
        state="Taloyhtiön tila",
        housing_company_count="Taloyhtiöiden lukumäärä",
        apartment_count="Asuntojen lukumäärä",
    )
    worksheet.append(column_headers)

    states = sort_housing_companies_by_state(housing_companies)

    for state, counts in states.items():
        worksheet.append(
            HousingCompanyStatesReportColumns(
                state=state.value,
                housing_company_count=counts["housing_company_count"],
                apartment_count=counts["apartment_count"],
            )
        )

    last_row = worksheet.max_row
    worksheet.auto_filter.ref = worksheet.dimensions

    empty_row = HousingCompanyStatesReportColumns(
        state="",
        housing_company_count="",
        apartment_count="",
    )

    # There needs to be an empty row for sorting and filtering to work properly
    worksheet.append(empty_row)

    # Add summary rows
    worksheet.append(
        HousingCompanyStatesReportColumns(
            state="Yhtiöitä yhteensä",
            housing_company_count=len(housing_companies),
            apartment_count="",
        ),
    )
    worksheet.append(
        HousingCompanyStatesReportColumns(
            state="Asuntoja yhteensä",
            housing_company_count=sum(housing_company.apartment_count for housing_company in housing_companies),
            apartment_count="",
        ),
    )

    column_letters = string.ascii_uppercase[: len(column_headers)]

    format_sheet(
        worksheet,
        formatting_rules={
            # Add a border to the header row
            **{f"{letter}1": {"border": Border(bottom=Side(style="thin"))} for letter in column_letters},
            # Add a border to the last data row
            **{f"{letter}{last_row}": {"border": Border(bottom=Side(style="thin"))} for letter in column_letters},
        },
    )

    resize_columns(worksheet)
    worksheet.protection.sheet = True
    return workbook


def sort_housing_companies_by_state(
    housing_companies: list[HousingCompanyWithStateReportAnnotations],
) -> dict[ReportState, HousingCompanyStatesCount]:
    states: dict[ReportState, HousingCompanyStatesCount] = {
        name: HousingCompanyStatesCount(
            housing_company_count=0,
            apartment_count=0,
        )
        for name in ReportState
    }

    for housing_company in housing_companies:
        if housing_company.hitas_type == HitasType.HALF_HITAS:
            states[ReportState.HALF_HITAS]["housing_company_count"] += 1
            states[ReportState.HALF_HITAS]["apartment_count"] += housing_company.apartment_count

        elif housing_company.completion_date is None:
            states[ReportState.NOT_READY]["housing_company_count"] += 1
            states[ReportState.NOT_READY]["apartment_count"] += housing_company.apartment_count

        elif housing_company.regulation_status == RegulationStatus.REGULATED:
            states[ReportState.REGULATED]["housing_company_count"] += 1
            states[ReportState.REGULATED]["apartment_count"] += housing_company.apartment_count

        elif housing_company.regulation_status == RegulationStatus.RELEASED_BY_HITAS:
            states[ReportState.RELEASED_BY_HITAS]["housing_company_count"] += 1
            states[ReportState.RELEASED_BY_HITAS]["apartment_count"] += housing_company.apartment_count

        elif housing_company.regulation_status == RegulationStatus.RELEASED_BY_PLOT_DEPARTMENT:
            states[ReportState.RELEASED_BY_PLOT_DEPARTMENT]["housing_company_count"] += 1
            states[ReportState.RELEASED_BY_PLOT_DEPARTMENT]["apartment_count"] += housing_company.apartment_count

    return states
