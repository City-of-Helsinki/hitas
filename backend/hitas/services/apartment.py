from typing import Collection

from django.db import models
from django.db.models import F, OuterRef, Prefetch, Subquery, Sum
from django.db.models.functions import Coalesce

from hitas.models import Apartment
from hitas.models._base import HitasModelDecimalField
from hitas.models.apartment_sale import ApartmentSale
from hitas.utils import SQSum, subquery_first_id


def prefetch_first_sale(lookup_prefix: str = "", ignore: Collection[int] = ()) -> Prefetch:
    """Prefetch only the first sale of an apartment.

    :param lookup_prefix: Add prefix to lookup, e.g. 'ownerships__apartment__'
                          depending on the prefix context. Should end with '__'.
    :param ignore: These sale ID's should be ignored.
    """
    return Prefetch(
        f"{lookup_prefix}sales",
        ApartmentSale.objects.filter(
            id__in=Subquery(
                ApartmentSale.objects.filter(apartment_id=OuterRef("apartment_id"))
                .exclude(id__in=ignore)
                .order_by("purchase_date")
                .values_list("id", flat=True)[:1]
            )
        ),
    )


def subquery_first_sale_acquisition_price(outer_ref: str) -> Subquery:
    return Subquery(
        queryset=(
            ApartmentSale.objects.filter(apartment_id=OuterRef(outer_ref))
            .order_by("purchase_date")
            .annotate(_first_sale_price=Sum(F("purchase_price") + F("apartment_share_of_housing_company_loans")))
            .values_list("_first_sale_price", flat=True)[:1]
        ),
        output_field=HitasModelDecimalField(null=True),
    )


def subquery_first_sale_purchase_price(outer_ref: str) -> Subquery:
    return Subquery(
        queryset=(
            ApartmentSale.objects.filter(apartment_id=OuterRef(outer_ref))
            .order_by("purchase_date")
            .values_list("purchase_price", flat=True)[:1]
        ),
        output_field=HitasModelDecimalField(null=True),
    )


def subquery_first_sale_loan_amount(outer_ref: str) -> Subquery:
    return Subquery(
        queryset=(
            ApartmentSale.objects.filter(apartment_id=OuterRef(outer_ref))
            .order_by("purchase_date")
            .values_list("apartment_share_of_housing_company_loans", flat=True)[:1]
        ),
        output_field=HitasModelDecimalField(null=True),
    )


def subquery_latest_sale_purchase_price(outer_ref: str) -> Subquery:
    return Subquery(
        queryset=(
            ApartmentSale.objects.filter(apartment_id=OuterRef(outer_ref))
            .exclude(
                id__in=subquery_first_id(ApartmentSale, "apartment_id", order_by="-purchase_date"),
            )
            .order_by("-purchase_date")
            .values_list("purchase_price", flat=True)[:1]
        ),
        output_field=HitasModelDecimalField(null=True),
    )


def subquery_first_purchase_date(outer_ref: str) -> Subquery:
    return Subquery(
        queryset=(
            ApartmentSale.objects.filter(apartment_id=OuterRef(outer_ref))
            .order_by("purchase_date")
            .values_list("purchase_date", flat=True)[:1]
        ),
        output_field=models.DateField(null=True),
    )


def subquery_latest_purchase_date(outer_ref: str) -> Subquery:
    return Subquery(
        queryset=(
            ApartmentSale.objects.filter(apartment_id=OuterRef(outer_ref))
            .exclude(
                id__in=subquery_first_id(ApartmentSale, "apartment_id", order_by="-purchase_date"),
            )
            .order_by("-purchase_date")
            .values_list("purchase_date", flat=True)[:1]
        ),
        output_field=models.DateField(null=True),
    )


def aggregate_catalog_prices_where_no_sales():
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
