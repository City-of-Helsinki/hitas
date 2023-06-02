from datetime import datetime

from hitas.models import ApartmentSale


def find_sales_on_interval_for_reporting(start_date: datetime.date, end_date: datetime.date) -> list[ApartmentSale]:
    return list(
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
        )
    )
