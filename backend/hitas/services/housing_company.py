import datetime
import logging
from typing import Literal

from _decimal import Decimal
from django.db import models
from django.db.models import ExpressionWrapper, F, Q, QuerySet, Sum
from django.db.models.functions import Coalesce, NullIf, Round, TruncMonth
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings
from typing_extensions import TypeAlias

from hitas.exceptions import MissingValues
from hitas.models import Apartment, HousingCompany, MarketPriceIndex, MarketPriceIndex2005Equal100
from hitas.models._base import HitasModelDecimalField
from hitas.models.housing_company import HousingCompanyWithAnnotations, RegulationStatus
from hitas.services.apartment import aggregate_catalog_prices_where_no_sales, subquery_first_sale_acquisition_price
from hitas.utils import max_if_all_not_null, roundup

logger = logging.getLogger()


HousingCompanyNameT: TypeAlias = str
ApartmentAddressT: TypeAlias = str


def get_completed_housing_companies(
    completion_month: datetime.date,
    include_excluded_from_statistics: bool = False,
) -> list[HousingCompanyWithAnnotations]:
    """
    Get all housing companies completed before the given month (YYYY-MM-01) which are in the given states.
    """
    housing_company_queryset: QuerySet[HousingCompanyWithAnnotations] = (
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
            _catalog_prices=aggregate_catalog_prices_where_no_sales(),
        )
        .annotate(
            realized_acquisition_price=ExpressionWrapper(
                Coalesce(Sum("_first_sale_prices"), 0) + F("_catalog_prices"),
                output_field=HitasModelDecimalField(),
            ),
            surface_area=Round(Sum("real_estates__buildings__apartments__surface_area")),
            completion_date=max_if_all_not_null(
                ref="real_estates__buildings__apartments__completion_date",
                max=datetime.date.max,
                min=datetime.date.min,
            ),
            completion_month=TruncMonth("completion_date"),
            avg_price_per_square_meter=(
                F("realized_acquisition_price")
                # Prevent zero-division errors
                / (NullIf(F("surface_area"), 0, output_field=HitasModelDecimalField()))
            ),
        )
        .filter(
            completion_date__lte=completion_month,
            regulation_status=RegulationStatus.REGULATED,
        )
    )

    if not include_excluded_from_statistics:
        housing_company_queryset = housing_company_queryset.filter(exclude_from_statistics=False)

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


def _get_indices_for_adjustment(
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

        raise MissingValues(missing=errors, message="Missing apartment details")
