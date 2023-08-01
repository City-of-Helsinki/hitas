import datetime
from typing import Collection, Optional, overload
from uuid import UUID

from django.db import models
from django.db.models import F, OuterRef, Prefetch, QuerySet, Subquery, Sum, Value
from django.db.models.functions import Cast, Coalesce, TruncMonth

from hitas.models import (
    ConstructionPriceIndex,
    ConstructionPriceIndex2005Equal100,
    HousingCompany,
    MarketPriceIndex,
    MarketPriceIndex2005Equal100,
)
from hitas.models._base import HitasModelDecimalField
from hitas.models.apartment import Apartment
from hitas.models.apartment_sale import ApartmentSale
from hitas.utils import SQSum, monthify, subquery_first_id


def prefetch_first_sale(lookup_prefix: str = "", ignore: Collection = ()) -> Prefetch:
    return Prefetch(f"{lookup_prefix}sales", first_sale_qs("apartment_id", ignore=ignore))


def prefetch_latest_sale(lookup_prefix: str = "", *, include_first_sale: bool = False) -> Prefetch:
    return Prefetch(f"{lookup_prefix}sales", latest_sale_qs("apartment_id", include_first_sale=include_first_sale))


def first_sale_qs(apartment_id: str | int, ignore: Collection = ()) -> QuerySet[ApartmentSale]:
    ref: OuterRef | int = OuterRef(apartment_id) if isinstance(apartment_id, str) else apartment_id
    queryset = ApartmentSale.objects.filter(apartment_id=ref).exclude(id__in=ignore).order_by("purchase_date", "id")
    return ApartmentSale.objects.filter(id__in=Subquery(queryset.values_list("id", flat=True)[:1]))


def latest_sale_qs(apartment_id: str | int, include_first_sale: bool = False) -> QuerySet[ApartmentSale]:
    ref: OuterRef | int = OuterRef(apartment_id) if isinstance(apartment_id, str) else apartment_id
    queryset = (
        ApartmentSale.objects.filter(apartment_id=ref)
        .exclude(
            id__in=(
                ()
                if include_first_sale
                # First sale should not be the latest sale in some cases
                else subquery_first_id(ApartmentSale, "apartment_id", order_by=["purchase_date", "id"])
            ),
        )
        .order_by("-purchase_date", "-id")
    )
    return ApartmentSale.objects.filter(id__in=Subquery(queryset.values_list("id", flat=True)[:1]))


@overload
def get_first_sale_acquisition_price(apartment_id: str) -> Subquery:
    ...


@overload
def get_first_sale_acquisition_price(apartment_id: int) -> Optional[datetime.date]:
    ...


def get_first_sale_acquisition_price(apartment_id: str | int):
    subquery = isinstance(apartment_id, str)
    queryset: QuerySet[ApartmentSale] = (
        ApartmentSale.objects.filter(apartment_id=OuterRef(apartment_id) if subquery else apartment_id)
        .order_by("purchase_date", "id")
        .annotate(_first_sale_price=Sum(F("purchase_price") + F("apartment_share_of_housing_company_loans")))
        .values_list("_first_sale_price", flat=True)
    )
    if subquery:
        return Subquery(queryset=queryset[:1], output_field=HitasModelDecimalField(null=True))
    return queryset.first()


@overload
def get_first_sale_purchase_price(apartment_id: str) -> Subquery:
    ...


@overload
def get_first_sale_purchase_price(apartment_id: int) -> Optional[datetime.date]:
    ...


def get_first_sale_purchase_price(apartment_id: str | int):
    subquery = isinstance(apartment_id, str)
    queryset: QuerySet[ApartmentSale] = (
        ApartmentSale.objects.filter(apartment_id=OuterRef(apartment_id) if subquery else apartment_id)
        .order_by("purchase_date", "id")
        .values_list("purchase_price", flat=True)
    )
    if subquery:
        return Subquery(queryset=queryset[:1], output_field=HitasModelDecimalField(null=True))
    return queryset.first()


@overload
def get_first_sale_loan_amount(apartment_id: str) -> Subquery:
    ...


@overload
def get_first_sale_loan_amount(apartment_id: int) -> Optional[datetime.date]:
    ...


def get_first_sale_loan_amount(apartment_id: str | int):
    subquery = isinstance(apartment_id, str)
    queryset: QuerySet[ApartmentSale] = (
        ApartmentSale.objects.filter(apartment_id=OuterRef(apartment_id) if subquery else apartment_id)
        .order_by("purchase_date", "id")
        .values_list("apartment_share_of_housing_company_loans", flat=True)
    )
    if subquery:
        return Subquery(queryset=queryset[:1], output_field=HitasModelDecimalField(null=True))
    return queryset.first()


@overload
def get_latest_sale_purchase_price(apartment_id: str, *, include_first_sale: bool = False) -> Subquery:
    ...


@overload
def get_latest_sale_purchase_price(apartment_id: int, *, include_first_sale: bool = False) -> Optional[datetime.date]:
    ...


def get_latest_sale_purchase_price(apartment_id: str | int, *, include_first_sale: bool = False):
    subquery = isinstance(apartment_id, str)
    queryset: QuerySet[ApartmentSale] = (
        ApartmentSale.objects.filter(apartment_id=OuterRef(apartment_id) if subquery else apartment_id)
        .exclude(
            id__in=(
                ()
                if include_first_sale
                # First sale should not be the latest sale in some cases
                else subquery_first_id(ApartmentSale, "apartment_id", order_by=["purchase_date", "id"])
            ),
        )
        # .only("purchase_price", "id")
        .order_by("-purchase_date", "-id")
        .values_list("purchase_price", flat=True)
    )
    if subquery:
        return Subquery(queryset=queryset[:1], output_field=HitasModelDecimalField(null=True))
    return queryset.first()


@overload
def get_first_sale_purchase_date(apartment_id: str) -> Subquery:
    ...


@overload
def get_first_sale_purchase_date(apartment_id: int) -> Optional[datetime.date]:
    ...


def get_first_sale_purchase_date(apartment_id: str | int):
    subquery = isinstance(apartment_id, str)
    queryset: QuerySet[ApartmentSale] = (
        ApartmentSale.objects.filter(apartment_id=OuterRef(apartment_id) if subquery else apartment_id)
        .order_by("purchase_date", "id")
        .values_list("purchase_date", flat=True)
    )
    if subquery:
        return Subquery(queryset=queryset[:1], output_field=models.DateField(null=True))
    return queryset.first()


@overload
def get_latest_sale_purchase_date(apartment_id: str, *, include_first_sale: bool = False) -> Subquery:
    ...


@overload
def get_latest_sale_purchase_date(apartment_id: int, *, include_first_sale: bool = False) -> Optional[datetime.date]:
    ...


def get_latest_sale_purchase_date(apartment_id: str | int, *, include_first_sale: bool = False):
    subquery = isinstance(apartment_id, str)
    queryset: QuerySet[ApartmentSale] = (
        ApartmentSale.objects.filter(apartment_id=OuterRef(apartment_id) if subquery else apartment_id)
        .exclude(
            id__in=(
                ()
                if include_first_sale
                # First sale should not be the latest sale in some cases
                else subquery_first_id(ApartmentSale, "apartment_id", order_by=["purchase_date", "id"])
            ),
        )
        .order_by("-purchase_date", "-id")
        .values_list("purchase_date", flat=True)
    )
    if subquery:
        return Subquery(queryset=queryset[:1], output_field=models.DateField(null=True))
    return queryset.first()


def aggregate_catalog_prices_where_no_sales() -> Coalesce:
    """Add up catalog prices for apartments which do not have any sales."""
    return Coalesce(
        SQSum(
            Apartment.objects.filter(
                building__real_estate__housing_company=OuterRef("id"),
                sales__isnull=True,
            )
            .annotate(_catalog_price=Sum(F("catalog_purchase_price") + F("catalog_primary_loan_amount")))
            .values_list("_catalog_price"),
            sum_field="_catalog_price",
        ),
        0,
        output_field=HitasModelDecimalField(),
    )


def annotate_apartment_unconfirmed_prices(
    apartment_uuid: UUID,
    queryset: QuerySet[Apartment],
    housing_company: HousingCompany,
    calculation_date: datetime.date,
) -> QuerySet[Apartment]:
    """
    Annotate apartments with their unconfirmed maximum prices.
    Intended only for a single apartment at a time.
    """

    from hitas.services.indices import (
        subquery_apartment_current_surface_area_price,
        subquery_apartment_first_sale_acquisition_price_index_adjusted,
    )

    null_decimal_field = Cast(None, output_field=HitasModelDecimalField())

    if housing_company.hitas_type.new_hitas_ruleset:
        queryset = queryset.annotate(
            completion_month=Value(
                housing_company.completion_date and monthify(housing_company.completion_date or None),
                output_field=models.DateField(),
            ),
            cpi=null_decimal_field,
            mpi=null_decimal_field,
            cpi_2005_100=subquery_apartment_first_sale_acquisition_price_index_adjusted(
                ConstructionPriceIndex2005Equal100,
                completion_date=housing_company.completion_date,
                calculation_date=calculation_date,
            ),
            mpi_2005_100=subquery_apartment_first_sale_acquisition_price_index_adjusted(
                MarketPriceIndex2005Equal100,
                completion_date=housing_company.completion_date,
                calculation_date=calculation_date,
            ),
        )
    else:
        # Actual completion date value is required for deprecation calculations, and we can't use `OuterRef` for it here
        completion_date = Apartment.objects.only("completion_date").get(uuid=apartment_uuid).completion_date
        queryset = queryset.annotate(
            completion_month=TruncMonth("completion_date"),
            cpi=subquery_apartment_first_sale_acquisition_price_index_adjusted(
                ConstructionPriceIndex,
                completion_date=completion_date,
                calculation_date=calculation_date,
            ),
            mpi=subquery_apartment_first_sale_acquisition_price_index_adjusted(
                MarketPriceIndex,
                completion_date=completion_date,
                calculation_date=calculation_date,
            ),
            cpi_2005_100=null_decimal_field,
            mpi_2005_100=null_decimal_field,
        )

    queryset = queryset.annotate(
        sapc=subquery_apartment_current_surface_area_price(calculation_date=calculation_date),
    )

    return queryset
