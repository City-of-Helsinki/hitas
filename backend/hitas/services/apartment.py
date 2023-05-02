import datetime
from typing import Collection, Optional, overload

from django.db import models
from django.db.models import F, OuterRef, Prefetch, QuerySet, Subquery, Sum
from django.db.models.functions import Coalesce

from hitas.models._base import HitasModelDecimalField
from hitas.models.apartment import Apartment
from hitas.models.apartment_sale import ApartmentSale
from hitas.utils import SQSum, subquery_first_id


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
