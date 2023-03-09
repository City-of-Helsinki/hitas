import datetime
import logging
from decimal import Decimal
from itertools import chain
from typing import Literal, Optional, TypeAlias, TypedDict

from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import ExpressionWrapper, F, OuterRef, Q, Subquery, Sum
from django.db.models.functions import Coalesce, NullIf, TruncMonth
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings

from hitas.exceptions import get_hitas_object_or_404
from hitas.models import Apartment
from hitas.models._base import HitasModelDecimalField
from hitas.models.apartment_sale import ApartmentSale
from hitas.models.external_sales_data import ExternalSalesData, SaleData
from hitas.models.housing_company import HousingCompany, HousingCompanyState, HousingCompanyWithAnnotations
from hitas.models.indices import MarketPriceIndex, MarketPriceIndex2005Equal100, SurfaceAreaPriceCeiling
from hitas.services.apartment import aggregate_catalog_prices_where_no_sales, subquery_first_sale_acquisition_price
from hitas.utils import business_quarter, hitas_calculation_quarter, max_if_all_not_null, roundup, to_quarter

logger = logging.getLogger()

PostalCodeT: TypeAlias = str
QuarterT: TypeAlias = str
HousingCompanyUUID: TypeAlias = str
HousingCompanyNameT: TypeAlias = str
ApartmentAddressT: TypeAlias = str


class ComparisonData(TypedDict):
    id: HousingCompanyUUID
    display_name: HousingCompanyNameT
    price: Decimal
    old_ruleset: bool


class RegulationResults(TypedDict):
    automatically_released: list[ComparisonData]
    released_from_regulation: list[ComparisonData]
    stays_regulated: list[ComparisonData]


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
    housing_companies = _get_housing_companies_to_check(regulation_month)
    if not housing_companies:
        logger.info("No housing companies to check regulation for.")
        logger.info("Regulation check complete!")
        return RegulationResults(
            automatically_released=[],
            released_from_regulation=[],
            stays_regulated=[],
        )

    automatically_released = _check_automatic_release(housing_companies)
    if not housing_companies:
        logger.info("All housing companies qualify for automatic release.")
        results = RegulationResults(
            automatically_released=automatically_released,
            released_from_regulation=[],
            stays_regulated=[],
        )
        _free_housing_companies_from_regulation(housing_companies, results)
        logger.info("Regulation check complete!")
        return results

    logger.info(
        f"{len(automatically_released)} housing companies qualify for automatic release. "
        f"Proceeding with regulation checks for remaining {len(housing_companies)} housing companies..."
    )

    logger.info("Making index adjustments...")
    _index_adjustment(housing_companies, calculation_month)

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
        f"{len(results['stays_regulated'])} stay regulated."
    )

    _free_housing_companies_from_regulation(housing_companies, results)

    logger.info("Regulation check complete!")
    return results


def _get_housing_companies_to_check(regulation_month: datetime.date) -> list[HousingCompanyWithAnnotations]:
    """Get all housing companies that should be checked for regulation continuation.

    :param regulation_month: Fetch only housing companies that have been
                             completed on or before this month (YYYY-MM-01).
    """
    housing_companies: list[HousingCompanyWithAnnotations] = list(
        HousingCompany.objects.select_related(
            "postal_code",
            "financing_method",
        )
        .prefetch_related(
            "real_estates",
            "real_estates__buildings",
            "real_estates__buildings__apartments",
        )
        .alias(
            _first_sale_prices=subquery_first_sale_acquisition_price("real_estates__buildings__apartments__id"),
            _catalog_prices=aggregate_catalog_prices_where_no_sales("real_estates__buildings__apartments__"),
            _realized_acquisition_price=ExpressionWrapper(
                Coalesce(Sum("_first_sale_prices"), 0) + F("_catalog_prices"),
                output_field=HitasModelDecimalField(),
            ),
            _total_surface_area=Sum("real_estates__buildings__apartments__surface_area"),
        )
        .annotate(
            completion_date=max_if_all_not_null(
                ref="real_estates__buildings__apartments__completion_date",
                inf=datetime.date.max,
            ),
            completion_month=TruncMonth("completion_date"),
            avg_price_per_square_meter=(
                F("_realized_acquisition_price")
                # Prevent zero-division errors
                / (NullIf(F("_total_surface_area"), 0, output_field=HitasModelDecimalField()))
            ),
        )
        .filter(
            completion_date__lte=regulation_month,
            state__in=[
                HousingCompanyState.LESS_THAN_30_YEARS,
                HousingCompanyState.GREATER_THAN_30_YEARS_NOT_FREE,
                # TODO: This should not be taken in 'surface area price ceiling 'calculation!
                HousingCompanyState.READY_NO_STATISTICS,
            ],
        )
        .all()
    )

    if not housing_companies:
        return []

    logger.info(f"- {len(housing_companies)} housing companies found!")
    logger.info("- Validating housing company apartment prices and surface areas...")
    _validate_prices_and_surface_areas(housing_companies)

    return housing_companies


def _validate_prices_and_surface_areas(housing_companies: list[HousingCompanyWithAnnotations]) -> None:
    """
    Validate that all apartments in the housing company have sales prices or sales catalog prices and surface areas.
    Raise an error in case they don't.
    """
    missing: dict[HousingCompanyNameT, dict[ApartmentAddressT, dict[Literal["price", "surface_area"], bool]]] = {}

    apartments_with_data = Apartment.objects.annotate(
        missing_prices=ExpressionWrapper(
            (
                Q(sales__isnull=True)
                & (Q(catalog_purchase_price__isnull=True) | Q(catalog_primary_loan_amount__isnull=True))
            ),
            output_field=models.BooleanField(),
        )
    ).filter(
        Q(missing_prices=True) | Q(surface_area=None),
        building__real_estate__housing_company__in=housing_companies,
    )

    for apartment in apartments_with_data:
        housing_company_name: HousingCompanyNameT = apartment.housing_company.display_name
        apartment_address: ApartmentAddressT = apartment.address

        if apartment.missing_prices:  # annotated attribute
            missing.setdefault(housing_company_name, {})
            missing[housing_company_name].setdefault(apartment_address, {})
            missing[housing_company_name][apartment_address]["price"] = True

        if apartment.surface_area is None:
            missing.setdefault(housing_company_name, {})
            missing[housing_company_name].setdefault(apartment_address, {})
            missing[housing_company_name][apartment_address]["surface_area"] = True

    if missing:
        errors: list[str] = []

        for housing_company_name, apartments_with_data in missing.items():
            msg = f"Average price per square meter could not be calculated for {housing_company_name!r}:"
            for apartment_address, flags in apartments_with_data.items():
                msg += f" Apartment {apartment_address!r} does not have"
                if flags.get("price"):
                    msg += " any sales or sales catalog prices"
                if flags.get("surface_area"):
                    if flags.get("price"):
                        msg += " or"
                    msg += " surface area set"
                msg += "."

            errors.append(msg)

        raise ValidationError(detail={api_settings.NON_FIELD_ERRORS_KEY: errors})


def _check_automatic_release(housing_companies: list[HousingCompanyWithAnnotations]) -> list[ComparisonData]:
    """
    Separate out housing companies that are automatically released from regulation.
    """
    automatically_released: list[ComparisonData] = []
    for i, housing_company in enumerate(housing_companies):
        if not housing_company.financing_method.old_hitas_ruleset:
            logger.info(
                f"- Housing company {housing_company.display_name!r} uses new hitas ruleset. "
                f"Automatically qualified for release from regulation."
            )
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
    return automatically_released


def _index_adjustment(
    housing_companies: list[HousingCompanyWithAnnotations],
    calculation_month: datetime.date,
) -> None:
    """
    Make index adjustments for housing company prices.
    """
    logger.info("- Looking for indices...")
    indexes = _get_indexes(housing_companies, calculation_month)

    logger.info("- All indices found, continuing adjustments...")
    missing_prices: list[HousingCompanyNameT] = []
    for housing_company in housing_companies:
        if housing_company.financing_method.old_hitas_ruleset:
            calculation_month_index = indexes["old"][calculation_month]
            completion_month_index = indexes["old"][housing_company.completion_month]
        else:
            calculation_month_index = indexes["new"][calculation_month]
            completion_month_index = indexes["new"][housing_company.completion_month]

        if housing_company.avg_price_per_square_meter in (None, Decimal("0")):
            missing_prices.append(housing_company.display_name)
            continue

        housing_company.avg_price_per_square_meter = roundup(
            housing_company.avg_price_per_square_meter * (calculation_month_index / completion_month_index)
        )

    if missing_prices:
        names = ", ".join(f"{housing_company_name!r}" for housing_company_name in missing_prices)
        raise ValidationError(
            detail={
                api_settings.NON_FIELD_ERRORS_KEY: (
                    f"Average price per square meter zero or missing for these housing companies: {names}. "
                    f"Index adjustments cannot be made."
                )
            },
        )


def _get_indexes(
    housing_companies: list[HousingCompanyWithAnnotations],
    calculation_month: datetime.date,
) -> dict[Literal["old", "new"], dict[datetime.date, Decimal]]:
    """
    Fetch indices for index adjustment. Raise an error if not all indices are found.
    """
    months_old: set[datetime.date] = set()
    months_new: set[datetime.date] = set()

    for housing_company in housing_companies:
        if housing_company.financing_method.old_hitas_ruleset:
            months_old.add(housing_company.completion_month)
        else:
            months_new.add(housing_company.completion_month)

    old_indexes: dict[datetime.date, Decimal] = {}
    new_indexes: dict[datetime.date, Decimal] = {}

    if months_old:
        months_old.add(calculation_month)
        for index in MarketPriceIndex.objects.filter(month__in=months_old).all():
            old_indexes[index.month] = index.value
    if months_new:
        months_new.add(calculation_month)
        for index in MarketPriceIndex2005Equal100.objects.filter(month__in=months_new).all():
            new_indexes[index.month] = index.value

    missing_old_indexes = set(months_old).difference(old_indexes) if months_old else set()
    missing_new_indexes = set(months_new).difference(new_indexes) if months_new else set()

    if missing_old_indexes or missing_new_indexes:
        errors: list[str] = []
        if missing_old_indexes:
            missing_old = ", ".join(f"'{month.strftime('%Y-%m')}'" for month in sorted(missing_old_indexes))
            errors.append(f"Pre 2011 market price indices missing for months: {missing_old}.")
        if missing_new_indexes:
            missing_new = ", ".join(f"'{month.strftime('%Y-%m')}'" for month in sorted(missing_new_indexes))
            errors.append(f"Post 2011 market price indices missing for months: {missing_new}.")

        raise ValidationError(detail={api_settings.NON_FIELD_ERRORS_KEY: errors})

    return {"old": old_indexes, "new": new_indexes}


def _get_comparison_values(
    housing_companies: list[HousingCompanyWithAnnotations],
    surface_area_price_ceiling: Decimal,
) -> dict[PostalCodeT, dict[HousingCompanyUUID, ComparisonData]]:
    """
    Determine the value, for each housing company, which shall be compared against
    the housing company's postal area's final average price per square meter.
    """
    comparison_values: dict[PostalCodeT, dict[HousingCompanyUUID, ComparisonData]] = {}
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
            exclude_in_statistics=False,
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
    comparison_values: dict[PostalCodeT, dict[HousingCompanyUUID, ComparisonData]],
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
    )

    for postal_code, comparison_data_by_housing_company in comparison_values.items():
        postal_code_average_price_per_square_meter = price_by_area.get(postal_code)

        if postal_code_average_price_per_square_meter is None:
            postal_code_average_price_per_square_meter = _find_average_of_nearest(postal_code, price_by_area)

            if postal_code_average_price_per_square_meter is None:
                # TODO: What here?
                companies = ", ".join(
                    (f"{data['display_name']!r}" for data in comparison_data_by_housing_company.values())
                )
                logger.error(
                    f"No average price per square meter found for postal code {postal_code!r}, "
                    f"cannot determine regulation need for the following housing companies: {companies}"
                )
                continue

        for _housing_company_id, comparison_data in comparison_data_by_housing_company.items():
            display_name = comparison_data["display_name"]
            comparison_value = comparison_data["price"]
            # TODO: Is this off by one?
            if comparison_value <= postal_code_average_price_per_square_meter:
                logger.info(
                    f"- Housing company {display_name!r} should be released from regulation since: "
                    f"{comparison_value} <= {postal_code_average_price_per_square_meter}."
                )
                results["released_from_regulation"].append(comparison_data)
            else:
                logger.info(
                    f"- Housing company {display_name!r} should stay regulated since: "
                    f"{comparison_value} > {postal_code_average_price_per_square_meter}."
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
