import datetime
import json
import logging
from decimal import Decimal
from itertools import chain
from typing import Iterable, Literal, NamedTuple, Optional, TypedDict
from uuid import UUID

from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import Count, F, Max, Min, OuterRef, Prefetch, Q, Subquery
from django.db.models.functions import TruncMonth
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet.worksheet import Worksheet

from hitas.exceptions import HitasModelNotFound, get_hitas_object_or_404
from hitas.models.apartment_sale import ApartmentSale
from hitas.models.external_sales_data import ExternalSalesData, SaleData
from hitas.models.housing_company import HousingCompany, HousingCompanyState, HousingCompanyWithAnnotations
from hitas.models.indices import SurfaceAreaPriceCeiling
from hitas.models.thirty_year_regulation import (
    FullSalesData,
    HousingCompanyNameT,
    HousingCompanyUUIDHex,
    PostalCodeT,
    QuarterT,
    RegulationResult,
    ThirtyYearRegulationResults,
    ThirtyYearRegulationResultsRow,
    ThirtyYearRegulationResultsRowWithAnnotations,
)
from hitas.services.housing_company import get_completed_housing_companies, make_index_adjustment_for_housing_companies
from hitas.services.indices import subquery_appropriate_cpi
from hitas.utils import (
    business_quarter,
    format_sheet,
    hitas_calculation_quarter,
    humanize_relativedelta,
    resize_columns,
    roundup,
    subquery_count,
    to_quarter,
)

logger = logging.getLogger()


class ComparisonData(TypedDict):
    id: HousingCompanyUUIDHex
    display_name: HousingCompanyNameT
    price: Decimal
    old_ruleset: bool


class RegulationResults(TypedDict):
    automatically_released: list[ComparisonData]
    released_from_regulation: list[ComparisonData]
    stays_regulated: list[ComparisonData]
    skipped: list[ComparisonData]


class ReportColumns(NamedTuple):
    display_name: str
    acquisition_price: Decimal | str
    apartment_count: int | str
    indices: str
    change: Decimal | str
    adjusted_acquisition_price: Decimal | str
    surface_area: Decimal | str
    price_per_square_meter: Decimal | str
    postal_code_price: Decimal | str
    state: str
    completion_date: datetime.date | str
    age: str


def perform_thirty_year_regulation(calculation_date: datetime.date) -> RegulationResults:
    """Check housing companies over 30 years old whether they should be released from hitas regulation or not.

    :param calculation_date: Date to check regulation from.
    """

    this_quarter = business_quarter(calculation_date)
    this_quarter_previous_year = this_quarter - relativedelta(years=1)
    previous_quarter = this_quarter - relativedelta(months=3)

    calculation_month = hitas_calculation_quarter(calculation_date)
    regulation_month = calculation_month - relativedelta(years=30)

    logger.info(f"Checking regulation need for housing companies completed before {regulation_month.isoformat()!r}...")

    logger.info("Fetching housing companies...")
    housing_companies = get_completed_housing_companies(
        completion_month=regulation_month,
        states=[
            HousingCompanyState.LESS_THAN_30_YEARS,
            HousingCompanyState.GREATER_THAN_30_YEARS_NOT_FREE,
            HousingCompanyState.READY_NO_STATISTICS,
        ],
    )
    if not housing_companies:
        logger.info("No housing companies to check regulation for.")
        logger.info("Regulation check complete!")
        return RegulationResults(
            automatically_released=[],
            released_from_regulation=[],
            stays_regulated=[],
            skipped=[],
        )

    split_housing_companies, automatically_released = _split_automatically_released(housing_companies)
    if not housing_companies:
        logger.info("All housing companies qualify for automatic release.")
        results = RegulationResults(
            automatically_released=automatically_released,
            released_from_regulation=[],
            stays_regulated=[],
            skipped=[],
        )

        logger.info("Updating housing company states...")
        _free_housing_companies_from_regulation(split_housing_companies, results)

        logger.info("Saving regulation results for reporting...")
        _save_regulation_results(
            results=results,
            calculation_month=calculation_month,
            regulation_month=regulation_month,
            housing_companies=split_housing_companies,
            surface_area_price_ceiling=None,
            unadjusted_prices=None,
            indices=None,
            sales_data=None,
            external_sales_data=None,
            price_by_area=None,
        )

        logger.info("Regulation check complete!")
        return results

    logger.info(
        f"{len(split_housing_companies)} housing companies qualify for automatic release. "
        f"Proceeding with regulation checks for remaining {len(housing_companies)} housing companies..."
    )

    unadjusted_prices: dict[HousingCompanyUUIDHex, Decimal] = {
        housing_company.uuid.hex: housing_company.avg_price_per_square_meter for housing_company in housing_companies
    }

    logger.info("Making index adjustments...")
    indices = make_index_adjustment_for_housing_companies(housing_companies, calculation_month)

    logger.info(f"Fetching surface area price ceiling for {calculation_month.isoformat()!r}...")
    surface_area_price_ceiling = get_hitas_object_or_404(SurfaceAreaPriceCeiling, month=calculation_month)

    logger.info("Determining comparison values for housing companies...")
    comparison_values = _get_comparison_values(housing_companies, surface_area_price_ceiling.value)

    postal_codes: list[PostalCodeT] = list(comparison_values)

    logger.info(
        f"Fetching HITAS sales data between {this_quarter_previous_year.isoformat()} (inclusive) "
        f"and {this_quarter.isoformat()} (exclusive)..."
    )
    sales_data = _get_sales_data(this_quarter_previous_year, this_quarter, postal_codes)

    logger.info("Fetching external sales data for the last four quarters...")
    external_sales_data = _get_external_sales_data(to_quarter(previous_quarter), postal_codes)

    logger.info("Combining HITAS and external sales data for each postal code...")
    price_by_area = _combine_sales_data(sales_data, external_sales_data)

    logger.info("Determining regulation need for housing companies...")
    results = _determine_regulation_need(comparison_values, price_by_area)
    results["automatically_released"] += automatically_released

    logger.info(
        f"{len(results['automatically_released'])} housing companies are released from regulation automatically, "
        f"{len(results['released_from_regulation'])} are released after regulation checks, "
        f"{len(results['stays_regulated'])} stay regulated, "
        f"{len(results['skipped'])} could not be checked."
    )

    housing_companies += split_housing_companies

    logger.info("Updating housing company states...")
    _free_housing_companies_from_regulation(housing_companies, results)

    logger.info("Saving regulation results for reporting...")
    _save_regulation_results(
        results=results,
        calculation_month=calculation_month,
        regulation_month=regulation_month,
        housing_companies=housing_companies,
        surface_area_price_ceiling=surface_area_price_ceiling.value,
        unadjusted_prices=unadjusted_prices,
        indices=indices,
        sales_data=sales_data,
        external_sales_data=external_sales_data,
        price_by_area=price_by_area,
    )

    logger.info("Regulation check complete!")
    return results


def _split_automatically_released(
    housing_companies: list[HousingCompanyWithAnnotations],
) -> tuple[list[HousingCompanyWithAnnotations], list[ComparisonData]]:
    """
    Separate out housing companies that are automatically released from regulation.
    """
    split_housing_companies: list[HousingCompanyWithAnnotations] = []
    automatically_released: list[ComparisonData] = []
    for i, housing_company in enumerate(housing_companies):
        if not housing_company.financing_method.old_hitas_ruleset:
            logger.info(
                f"Housing company {housing_company.display_name!r} uses new hitas ruleset. "
                f"Automatically qualified for release from regulation."
            )
            split_housing_companies.append(housing_company)
            automatically_released.append(
                ComparisonData(
                    id=housing_company.uuid.hex,
                    display_name=housing_company.display_name,
                    price=Decimal("0"),  # Index adjusted price not calculate yet
                    old_ruleset=housing_company.financing_method.old_hitas_ruleset,
                )
            )
            housing_companies[i] = None

    housing_companies[:] = [housing_company for housing_company in housing_companies if housing_company is not None]
    return split_housing_companies, automatically_released


def _get_comparison_values(
    housing_companies: list[HousingCompanyWithAnnotations],
    surface_area_price_ceiling: Decimal,
) -> dict[PostalCodeT, dict[HousingCompanyUUIDHex, ComparisonData]]:
    """
    Determine the value, for each housing company, which shall be compared against
    the housing company's postal area's final average price per square meter.
    """
    comparison_values: dict[PostalCodeT, dict[HousingCompanyUUIDHex, ComparisonData]] = {}
    for housing_company in housing_companies:
        postal_code = housing_company.postal_code.value
        comparison_values.setdefault(postal_code, {})
        comparison_values[postal_code][housing_company.uuid.hex] = ComparisonData(
            id=housing_company.uuid.hex,
            display_name=housing_company.display_name,
            price=max((housing_company.avg_price_per_square_meter, surface_area_price_ceiling)),
            old_ruleset=housing_company.financing_method.old_hitas_ruleset,
        )

    return comparison_values


def _get_sales_data(
    from_: datetime.date,
    to_: datetime.date,
    postal_codes: list[PostalCodeT],
) -> dict[PostalCodeT, dict[QuarterT, SaleData]]:
    """
    Find all sales for apartments in the given postal codes between the given dates
    ('from_' is inclusive, 'to_' is exclusive) for use in regulation check.
    """

    sales_by_quarter: dict[PostalCodeT, dict[QuarterT, SaleData]] = {}
    sales_in_previous_year = (
        ApartmentSale.objects.select_related(
            "apartment",
            "apartment__building",
            "apartment__building__real_estate",
            "apartment__building__real_estate__housing_company",
            "apartment__building__real_estate__housing_company__postal_code",
        )
        .alias(
            _first_sale_id=Subquery(
                queryset=(
                    ApartmentSale.objects.filter(apartment_id=OuterRef("apartment_id"))
                    .order_by("purchase_date")
                    .values_list("id", flat=True)[:1]
                ),
                output_field=models.IntegerField(null=True),
            ),
        )
        .filter(
            ~Q(id__in=F("_first_sale_id")),
            purchase_date__gte=from_,
            purchase_date__lt=to_,
            exclude_from_statistics=False,
            # TODO: apartment__building__real_estate__housing_company__exclude_from_statistics=False,
            apartment__building__real_estate__housing_company__postal_code__value__in=postal_codes,
            apartment__building__real_estate__housing_company__state__in=[
                HousingCompanyState.LESS_THAN_30_YEARS,
                HousingCompanyState.GREATER_THAN_30_YEARS_NOT_FREE,
                HousingCompanyState.GREATER_THAN_30_YEARS_FREE,
                HousingCompanyState.GREATER_THAN_30_YEARS_PLOT_DEPARTMENT_NOTIFICATION,
            ],
        )
        .all()
    )

    for sale in sales_in_previous_year:
        quarter = to_quarter(sale.purchase_date)
        postal_code = sale.apartment.postal_code.value
        if postal_code not in postal_codes:
            continue

        sales_by_quarter.setdefault(postal_code, {})
        sales_by_quarter[postal_code].setdefault(quarter, SaleData(sale_count=0, price=0))
        sales_by_quarter[postal_code][quarter]["sale_count"] += 1
        sales_by_quarter[postal_code][quarter]["price"] += sale.total_price

    return sales_by_quarter


def _get_external_sales_data(
    quarter: QuarterT,
    postal_codes: list[PostalCodeT],
) -> dict[PostalCodeT, dict[QuarterT, SaleData]]:
    """
    Get all external sales data for the given quarter,
    filtering the results to include only the given postal codes.
    """
    sales_data = get_hitas_object_or_404(ExternalSalesData, calculation_quarter=quarter)

    sales_by_quarter: dict[PostalCodeT, dict[QuarterT, SaleData]] = {}
    for quarter_data in (sales_data.quarter_1, sales_data.quarter_2, sales_data.quarter_3, sales_data.quarter_4):
        for area in quarter_data["areas"]:
            quarter_ = quarter_data["quarter"]
            postal_code = area["postal_code"]
            if postal_code not in postal_codes:
                continue

            sales_by_quarter.setdefault(postal_code, {})
            sales_by_quarter[postal_code][quarter_] = SaleData(sale_count=area["sale_count"], price=area["price"])

    return sales_by_quarter


def _combine_sales_data(*args: dict[PostalCodeT, dict[QuarterT, SaleData]]) -> dict[PostalCodeT, Decimal]:
    """
    Combine multiple sources of sales data (e.g. Hitas sales and External sales data),
    and calculate the average per postal code.
    """
    sales_data: dict[PostalCodeT, SaleData] = {}
    for data in args:
        for postal_code, quarter_data in data.items():
            for sale_data in quarter_data.values():
                sales_data.setdefault(postal_code, SaleData(sale_count=0, price=0))
                sales_data[postal_code]["sale_count"] += sale_data["sale_count"]
                sales_data[postal_code]["price"] += sale_data["price"]

    total_by_postal_code: dict[PostalCodeT, Decimal] = {}
    for postal_code, sale_data in sales_data.items():
        total_by_postal_code[postal_code] = roundup(Decimal(sale_data["price"]) / Decimal(sale_data["sale_count"]))

    return total_by_postal_code


def _determine_regulation_need(
    comparison_values: dict[PostalCodeT, dict[HousingCompanyUUIDHex, ComparisonData]],
    price_by_area: dict[PostalCodeT, Decimal],
) -> RegulationResults:
    """
    Determine id a given housing company should stay regulated or be released from regulation
    based on its "comparison value" (determined separately).
    """
    results = RegulationResults(
        automatically_released=[],
        released_from_regulation=[],
        stays_regulated=[],
        skipped=[],
    )

    for postal_code, comparison_data_by_housing_company in comparison_values.items():
        postal_code_average_price_per_square_meter = price_by_area.get(postal_code)

        if postal_code_average_price_per_square_meter is None:
            postal_code_average_price_per_square_meter = _find_average_of_nearest(postal_code, price_by_area)

        for comparison_data in comparison_data_by_housing_company.values():
            display_name = comparison_data["display_name"]
            comparison_value = comparison_data["price"]

            if postal_code_average_price_per_square_meter is None:
                logger.info(
                    f"No average price per square meter found for postal code {postal_code!r}, "
                    f"cannot determine regulation need for {display_name!r}."
                )
                results["skipped"].append(comparison_data)
                continue

            if comparison_value >= postal_code_average_price_per_square_meter:
                logger.info(
                    f"Housing company {display_name!r} should be released from regulation since: "
                    f"{comparison_value} >= {postal_code_average_price_per_square_meter}."
                )
                results["released_from_regulation"].append(comparison_data)
            else:
                logger.info(
                    f"Housing company {display_name!r} should stay regulated since: "
                    f"{comparison_value} < {postal_code_average_price_per_square_meter}."
                )
                results["stays_regulated"].append(comparison_data)

    return results


def _find_average_of_nearest(postal_code: PostalCodeT, price_by_area: dict[PostalCodeT, Decimal]) -> Optional[Decimal]:
    """
    Find the average of the nearest two postal areas in the given prices by area.
    """
    # TODO: Determine nearest value somehow...
    return None


def _free_housing_companies_from_regulation(
    housing_companies: list[HousingCompanyWithAnnotations],
    regulation_results: RegulationResults,
) -> None:
    """
    Change housing company states according to regulation results.
    """
    housing_company_uuids: set[str] = {
        results["id"]
        for results in chain(
            regulation_results["automatically_released"], regulation_results["released_from_regulation"]
        )
    }
    for housing_company in housing_companies:
        if housing_company.uuid.hex not in housing_company_uuids:
            housing_company.state = HousingCompanyState.GREATER_THAN_30_YEARS_NOT_FREE
            continue

        housing_company.state = HousingCompanyState.GREATER_THAN_30_YEARS_FREE

    HousingCompany.objects.bulk_update(housing_companies, fields=["state"])


def _save_regulation_results(
    results: RegulationResults,
    calculation_month: datetime.date,
    regulation_month: datetime.date,
    housing_companies: Iterable[HousingCompanyWithAnnotations],
    surface_area_price_ceiling: Optional[Decimal],
    unadjusted_prices: Optional[dict[HousingCompanyUUIDHex, Decimal]],
    indices: Optional[dict[Literal["old", "new"], dict[datetime.date, Decimal]]],
    sales_data: Optional[dict[PostalCodeT, dict[QuarterT, SaleData]]],
    external_sales_data: Optional[dict[PostalCodeT, dict[QuarterT, SaleData]]],
    price_by_area: Optional[dict[PostalCodeT, Decimal]],
) -> ThirtyYearRegulationResults:
    """
    Save regulation results for reporting.
    """
    thirty_year_regulation_results = ThirtyYearRegulationResults.objects.create(
        calculation_month=calculation_month,
        regulation_month=regulation_month,
        surface_area_price_ceiling=surface_area_price_ceiling,
        sales_data=FullSalesData(
            # Convert decimals to floats
            internal=json.loads(json.dumps(sales_data, default=float)) or {},
            external=json.loads(json.dumps(external_sales_data, default=float)) or {},
            price_by_area=json.loads(json.dumps(price_by_area, default=float)) or {},
        ),
    )

    rows_to_save: list[ThirtyYearRegulationResultsRow] = []
    for housing_company in housing_companies:
        # If housing company was released automatically, its prices were never index adjusted.
        unadjusted_average_price_per_square_meter: Decimal = housing_company.avg_price_per_square_meter
        adjusted_average_price_per_square_meter: Optional[Decimal] = None
        if unadjusted_prices is not None and housing_company.uuid.hex in unadjusted_prices:
            unadjusted_average_price_per_square_meter = unadjusted_prices[housing_company.uuid.hex]
            adjusted_average_price_per_square_meter = housing_company.avg_price_per_square_meter

        # If housing company was released automatically, its prices were never index adjusted.
        completion_month_index: Optional[Decimal] = None
        calculation_month_index: Optional[Decimal] = None
        key: Literal["old", "new"]
        key = "old" if housing_company.financing_method.old_hitas_ruleset else "new"  # type: ignore
        if indices is not None and housing_company.completion_month in indices[key]:
            completion_month_index = indices[key][housing_company.completion_month]
            calculation_month_index = indices[key][calculation_month]

        if housing_company.uuid.hex in {result["id"] for result in results["automatically_released"]}:
            regulation_result = RegulationResult.AUTOMATICALLY_RELEASED
        elif housing_company.uuid.hex in {result["id"] for result in results["released_from_regulation"]}:
            regulation_result = RegulationResult.RELEASED_FROM_REGULATION
        elif housing_company.uuid.hex in {result["id"] for result in results["stays_regulated"]}:
            regulation_result = RegulationResult.STAYS_REGULATED
        else:
            regulation_result = RegulationResult.SKIPPED

        rows_to_save.append(
            ThirtyYearRegulationResultsRow(
                parent=thirty_year_regulation_results,
                housing_company=housing_company,
                completion_date=housing_company.completion_date,
                surface_area=housing_company.surface_area,
                postal_code=housing_company.postal_code.value,
                realized_acquisition_price=housing_company.realized_acquisition_price,
                unadjusted_average_price_per_square_meter=unadjusted_average_price_per_square_meter,
                adjusted_average_price_per_square_meter=adjusted_average_price_per_square_meter,
                completion_month_index=completion_month_index,
                calculation_month_index=calculation_month_index,
                regulation_result=regulation_result,
            )
        )

    ThirtyYearRegulationResultsRow.objects.bulk_create(objs=rows_to_save)

    return thirty_year_regulation_results


def get_thirty_year_regulation_results(calculation_date: datetime.date) -> ThirtyYearRegulationResults:
    try:
        return ThirtyYearRegulationResults.objects.prefetch_related(
            Prefetch(
                "rows",
                ThirtyYearRegulationResultsRow.objects.prefetch_related(
                    "housing_company",
                    "housing_company__postal_code",
                ).annotate(
                    apartment_count=Count("housing_company__real_estates__buildings__apartments"),
                ),
            ),
        ).get(calculation_month=hitas_calculation_quarter(calculation_date))
    except ThirtyYearRegulationResults.DoesNotExist as error:
        raise HitasModelNotFound(ThirtyYearRegulationResults) from error


def get_thirty_year_regulation_results_for_housing_company(
    housing_company_uuid: UUID,
    calculation_date: datetime.date,
) -> ThirtyYearRegulationResultsRowWithAnnotations:
    results = (
        ThirtyYearRegulationResultsRow.objects.select_related(
            "parent",
            "housing_company",
            "housing_company__postal_code",
        )
        .prefetch_related(
            "housing_company__real_estates",
        )
        .filter(
            housing_company__uuid=housing_company_uuid,
            parent__calculation_month=hitas_calculation_quarter(calculation_date),
        )
        .annotate(
            check_count=subquery_count(
                ThirtyYearRegulationResultsRow,
                "housing_company__uuid",
                parent__calculation_month__lte=hitas_calculation_quarter(calculation_date),
            ),
            min_share=Min("housing_company__real_estates__buildings__apartments__share_number_start"),
            max_share=Max("housing_company__real_estates__buildings__apartments__share_number_end"),
            share_count=F("max_share") - F("min_share") + 1,
            apartment_count=Count("housing_company__real_estates__buildings__apartments"),
            completion_month=TruncMonth("completion_date"),
            completion_month_index_cpi=subquery_appropriate_cpi(
                outer_ref="completion_month",
                financing_method_ref="housing_company__financing_method",
            ),
            calculation_month_index_cpi=subquery_appropriate_cpi(
                outer_ref="parent__calculation_month",
                financing_method_ref="housing_company__financing_method",
            ),
            average_price_per_square_meter_cpi=(
                F("calculation_month_index_cpi") / F("completion_month_index_cpi") * F("realized_acquisition_price")
            ),
        )
        .order_by("-parent__calculation_month")
        .first()
    )
    if results is None:
        raise HitasModelNotFound(ThirtyYearRegulationResultsRow)

    results.turned_30 = results.completion_date + relativedelta(years=30)
    results.difference = results.adjusted_average_price_per_square_meter - Decimal(
        results.parent.sales_data["price_by_area"][results.postal_code]
    )

    return results


def build_thirty_year_regulation_report_excel(results: ThirtyYearRegulationResults) -> Workbook:
    workbook = Workbook()
    worksheet: Worksheet = workbook.active

    columns = ReportColumns(
        display_name="Yhtiö",
        acquisition_price="Hankinta-arvo",
        apartment_count="Huoneistoja",
        indices="Indeksit",
        change="Muutos",
        adjusted_acquisition_price="Takistettu hinta",
        surface_area="Pinta-ala",
        price_per_square_meter="E-hinta/m²",
        postal_code_price="Postinumerohinta",
        state="Tila",
        completion_date="Valmistumispäivä",
        age="Yhtiön ikä",
    )
    worksheet.append(columns)

    for row in results.rows.all():
        data = ReportColumns(
            display_name=row.housing_company.display_name,
            acquisition_price=row.realized_acquisition_price,
            apartment_count=row.apartment_count,
            indices=f"{row.completion_month_index}/{row.calculation_month_index}",
            change=(
                (row.adjusted_average_price_per_square_meter * row.surface_area)
                - (row.unadjusted_average_price_per_square_meter * row.surface_area)
            ),
            adjusted_acquisition_price=row.adjusted_average_price_per_square_meter * row.surface_area,
            surface_area=row.surface_area,
            price_per_square_meter=row.adjusted_average_price_per_square_meter,
            postal_code_price=row.parent.sales_data["price_by_area"][row.postal_code],
            state=(
                "Ei vapaudu"
                if row.regulation_result == RegulationResult.STAYS_REGULATED
                else "Ei voitu määrittää"
                if row.regulation_result == RegulationResult.SKIPPED
                else "Vapautuu"
            ),
            completion_date=row.completion_date,
            age=humanize_relativedelta(relativedelta(results.calculation_month, row.completion_date)),
        )
        worksheet.append(data)

    format_sheet(
        worksheet,
        formatting_rules={
            "B": {"number_format": "#,##0.00\\ €"},
            "D": {"alignment": Alignment(horizontal="right")},
            "E": {"number_format": "#,##0.00\\ €"},
            "F": {"number_format": "#,##0.00\\ €"},
            "G": {"number_format": "#,##0.00\\ \\m\\²"},
            "H": {"number_format": "#,##0.00\\ €"},
            "I": {"number_format": "#,##0.00\\ €"},
            "J": {
                "alignment": Alignment(horizontal="right"),
                "font": {
                    "Ei vapaudu": Font(color="FF0000"),
                    "Ei voitu määrittää": Font(color="0000FF"),
                    "Vapautuu": Font(color="00FF00"),
                },
            },
            "K": {"number_format": "DD.MM.YYYY"},
            "L": {"alignment": Alignment(horizontal="right")},
        },
    )

    resize_columns(worksheet)
    worksheet.auto_filter.ref = worksheet.dimensions
    worksheet.protection.sheet = True
    return workbook
