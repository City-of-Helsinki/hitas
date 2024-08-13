from datetime import datetime

from django.db.models import Window
from django.db.models.functions import RowNumber

from hitas.models import ApartmentSale


def find_sales_on_interval_for_reporting(
    start_date: datetime.date, end_date: datetime.date, sales_filter="all"
) -> list[ApartmentSale]:
    queryset = (
        ApartmentSale.objects.select_related("apartment__building__real_estate__housing_company__postal_code")
        .filter(
            purchase_date__gte=start_date,
            purchase_date__lte=end_date,
            exclude_from_statistics=False,
            apartment__building__real_estate__housing_company__exclude_from_statistics=False,
        )
        .order_by(
            "apartment__building__real_estate__housing_company__postal_code__cost_area",
            "apartment__building__real_estate__housing_company__postal_code__value",
            "apartment__rooms",
        )
    )
    if sales_filter in ["resale", "firstsale"]:
        queryset = queryset.annotate(
            sale_number_in_order=Window(
                expression=RowNumber(),
                partition_by="apartment",
                order_by=["purchase_date", "id"],
            ),
        )
    if sales_filter == "resale":
        queryset = queryset.filter(sale_number_in_order__gt=1)
    elif sales_filter == "firstsale":
        queryset = queryset.filter(sale_number_in_order=1)
    return list(queryset)
