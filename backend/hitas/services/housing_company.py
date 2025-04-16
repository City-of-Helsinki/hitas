import datetime
import logging
from decimal import Decimal
from typing import Literal, Optional, TypeAlias, overload

from django.db import models
from django.db.models import Count, ExpressionWrapper, F, OuterRef, Q, QuerySet, Subquery, Sum
from django.db.models.functions import Coalesce, NullIf, Round, TruncMonth
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings

from hitas.exceptions import MissingValues
from hitas.models._base import HitasModelDecimalField
from hitas.models.apartment import Apartment
from hitas.models.housing_company import (
    HitasType,
    HousingCompany,
    HousingCompanyWithAnnotations,
    HousingCompanyWithRegulatedReportAnnotations,
    HousingCompanyWithStateReportAnnotations,
    HousingCompanyWithUnregulatedReportAnnotations,
    RegulationStatus,
)
from hitas.models.indices import MarketPriceIndex, MarketPriceIndex2005Equal100
from hitas.models.thirty_year_regulation import RegulationResult, ThirtyYearRegulationResultsRow
from hitas.services.apartment import (
    aggregate_catalog_prices_where_no_sales,
    get_first_sale_acquisition_price,
    get_first_sale_purchase_date,
)
from hitas.services.audit_log import last_modified
from hitas.utils import max_date_if_all_not_null, roundup

logger = logging.getLogger()


HousingCompanyNameT: TypeAlias = str
ApartmentAddressT: TypeAlias = str


def get_completed_housing_companies(
    completion_month: datetime.date,
    include_excluded_from_statistics: bool,
    include_rental_hitas: bool,
    select_half_hitas: bool,
) -> list[HousingCompanyWithAnnotations]:
    """
    Get all housing companies completed before the given month (YYYY-MM-01) which are in the given states.

    :param completion_month: The month to use as the upper bound for completion dates.
    :param include_excluded_from_statistics: Whether to include housing companies excluded from statistics.
    :param include_rental_hitas: Whether to include rental Hitas housing companies.
    :param select_half_hitas: Whether to include only Half-Hitas companies or completely exclude them
    """
    non_deleted = Q(real_estates__buildings__apartments__deleted__isnull=True)
    housing_company_queryset: QuerySet[HousingCompanyWithAnnotations] = (
        HousingCompany.objects.select_related(
            "postal_code",
            "property_manager",
        )
        .prefetch_related(
            "real_estates",
            "real_estates__buildings",
            "real_estates__buildings__apartments",
        )
        .alias(
            _first_sale_prices=get_first_sale_acquisition_price("real_estates__buildings__apartments__id"),
            _catalog_prices=aggregate_catalog_prices_where_no_sales(),
        )
        .annotate(
            realized_acquisition_price=ExpressionWrapper(
                Coalesce(Sum("_first_sale_prices"), 0) + F("_catalog_prices"),
                output_field=HitasModelDecimalField(),
            ),
            surface_area=Round(Sum("real_estates__buildings__apartments__surface_area", filter=non_deleted)),
            _completion_date=max_date_if_all_not_null("real_estates__buildings__apartments__completion_date"),
            completion_month=TruncMonth("_completion_date"),
            avg_price_per_square_meter=(
                F("realized_acquisition_price")
                # Prevent zero-division errors
                / (NullIf(F("surface_area"), 0, output_field=HitasModelDecimalField()))
            ),
            property_manager_last_edited=last_modified(
                model=HousingCompany,
                model_id="id",
                hint='"property_manager": ',
            ),
        )
        .filter(
            _completion_date__lte=completion_month,
            regulation_status=RegulationStatus.REGULATED,
        )
    )

    if not include_excluded_from_statistics:
        housing_company_queryset = housing_company_queryset.filter(exclude_from_statistics=False)

    if not include_rental_hitas:
        housing_company_queryset = housing_company_queryset.filter(
            ~Q(hitas_type__in=[HitasType.RENTAL_HITAS_I, HitasType.RENTAL_HITAS_II]),
        )

    if select_half_hitas:
        housing_company_queryset = housing_company_queryset.filter(hitas_type=HitasType.HALF_HITAS)
    else:
        housing_company_queryset = housing_company_queryset.exclude(hitas_type=HitasType.HALF_HITAS)

    housing_companies = list(housing_company_queryset)
    if not housing_companies:
        return []

    logger.info(f"{len(housing_companies)} housing companies found!")
    logger.info("Validating housing company apartment prices and surface areas...")
    _validate_prices_and_surface_areas(housing_companies)

    return housing_companies


def make_index_adjustment_for_housing_companies(
    housing_companies: list[HousingCompanyWithAnnotations],
    calculation_month: datetime.date,
) -> dict[Literal["old", "new"], dict[datetime.date, Decimal]]:
    """
    Make index adjustments for housing company prices.
    """
    logger.info("Looking for indices...")
    indices = _get_indices_for_adjustment(housing_companies, calculation_month)

    logger.info("All indices found, continuing adjustments...")
    missing_prices: list[HousingCompanyNameT] = []
    for housing_company in housing_companies:
        if housing_company.hitas_type.old_hitas_ruleset:
            calculation_month_index = indices["old"][calculation_month]
            completion_month_index = indices["old"][housing_company.completion_month]
        else:
            calculation_month_index = indices["new"][calculation_month]
            completion_month_index = indices["new"][housing_company.completion_month]

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

    return indices


def _get_indices_for_adjustment(  # NOSONAR
    housing_companies: list[HousingCompanyWithAnnotations],
    calculation_month: datetime.date,
) -> dict[Literal["old", "new"], dict[datetime.date, Decimal]]:
    """
    Fetch indices for index adjustment. Raise an error if not all indices are found.
    """
    months_old: set[datetime.date] = set()
    months_new: set[datetime.date] = set()

    for housing_company in housing_companies:
        if housing_company.hitas_type.old_hitas_ruleset:
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

        raise MissingValues(missing=errors, message="Missing required indices")

    return {"old": old_indexes, "new": new_indexes}


def _validate_prices_and_surface_areas(housing_companies: list[HousingCompanyWithAnnotations]) -> None:  # NOSONAR
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

        raise MissingValues(missing=errors, message="Missing apartment details")


@overload
def get_regulation_release_date(apartment_id: str) -> Subquery: ...


@overload
def get_regulation_release_date(apartment_id: int) -> Optional[datetime.date]: ...


def get_regulation_release_date(housing_company_id: str | int):
    """
    Get the date the housing company was released from regulation in a 30-year regulation.
    Does not include release date for legacy or manually released housing companies.
    """
    subquery = isinstance(housing_company_id, str)
    queryset: QuerySet[Optional[datetime.date]] = (
        ThirtyYearRegulationResultsRow.objects.filter(
            housing_company=OuterRef(housing_company_id) if subquery else housing_company_id,
            regulation_result__in=(
                RegulationResult.AUTOMATICALLY_RELEASED,
                RegulationResult.RELEASED_FROM_REGULATION,
            ),
        )
        .select_related("parent")
        .order_by("-parent__calculation_month")
        .values_list("parent__calculation_month", flat=True)
    )
    if subquery:
        return Subquery(queryset=queryset[:1], output_field=models.DateField(null=True))
    return queryset.first()


def get_number_of_unsold_apartments(housing_company: HousingCompany) -> int:
    return (
        Apartment.objects.alias(
            _first_purchase_date=get_first_sale_purchase_date("id"),
        )
        .annotate(
            _unsold=ExpressionWrapper(
                expression=Q(_first_purchase_date__isnull=True),
                output_field=models.BooleanField(),
            ),
        )
        .filter(
            building__real_estate__housing_company=housing_company,
            _unsold=True,
        )
        .count()
    )


def find_regulated_housing_companies_for_reporting() -> list[HousingCompanyWithRegulatedReportAnnotations]:
    non_deleted = Q(real_estates__buildings__apartments__deleted__isnull=True)
    return list(
        HousingCompany.objects.select_related("postal_code")
        .prefetch_related(
            "real_estates__buildings__apartments",
        )
        .filter(
            regulation_status=RegulationStatus.REGULATED,
        )
        .exclude(
            hitas_type=HitasType.HALF_HITAS,
        )
        .alias(
            _acquisition_price=get_first_sale_acquisition_price("real_estates__buildings__apartments__id"),
        )
        .annotate(
            _completion_date=max_date_if_all_not_null("real_estates__buildings__apartments__completion_date"),
            surface_area=Round(Sum("real_estates__buildings__apartments__surface_area", filter=non_deleted)),
            realized_acquisition_price=Sum("_acquisition_price"),
            avg_price_per_square_meter=Round(
                F("realized_acquisition_price") / F("surface_area"),
                precision=2,
            ),
            apartment_count=Count("real_estates__buildings__apartments", filter=non_deleted),
        )
        .order_by(
            "postal_code__value",
            "_completion_date",
        )
    )


def find_half_hitas_housing_companies_for_reporting() -> list[HousingCompanyWithRegulatedReportAnnotations]:
    non_deleted = Q(real_estates__buildings__apartments__deleted__isnull=True)
    return list(
        HousingCompany.objects.select_related("postal_code")
        .prefetch_related(
            "real_estates__buildings__apartments",
        )
        .filter(
            hitas_type=HitasType.HALF_HITAS,
        )
        .alias(
            _acquisition_price=get_first_sale_acquisition_price("real_estates__buildings__apartments__id"),
        )
        .annotate(
            _completion_date=max_date_if_all_not_null("real_estates__buildings__apartments__completion_date"),
            surface_area=Round(Sum("real_estates__buildings__apartments__surface_area", filter=non_deleted)),
            realized_acquisition_price=Sum("_acquisition_price"),
            avg_price_per_square_meter=Round(
                F("realized_acquisition_price") / F("surface_area"),
                precision=2,
            ),
            apartment_count=Count("real_estates__buildings__apartments", filter=non_deleted),
        )
        .order_by(
            "postal_code__value",
            "_completion_date",
        )
    )


def find_unregulated_housing_companies_for_reporting() -> list[HousingCompanyWithUnregulatedReportAnnotations]:
    non_deleted = Q(real_estates__buildings__apartments__deleted__isnull=True)
    return list(
        HousingCompany.objects.select_related("postal_code")
        .prefetch_related("real_estates__buildings__apartments")
        .exclude(regulation_status=RegulationStatus.REGULATED)
        .exclude(hitas_type=HitasType.HALF_HITAS)
        .annotate(
            _completion_date=max_date_if_all_not_null("real_estates__buildings__apartments__completion_date"),
            apartment_count=Count("real_estates__buildings__apartments", filter=non_deleted),
            _release_date=get_regulation_release_date("id"),
        )
        .order_by("-_completion_date")
    )


def find_housing_companies_for_state_reporting() -> list[HousingCompanyWithStateReportAnnotations]:
    non_deleted = Q(real_estates__buildings__apartments__deleted__isnull=True)
    return list(
        HousingCompany.objects.annotate(
            _completion_date=max_date_if_all_not_null(ref="real_estates__buildings__apartments__completion_date"),
            apartment_count=Count("real_estates__buildings__apartments", filter=non_deleted),
        )
    )
