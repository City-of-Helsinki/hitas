from typing import TYPE_CHECKING, Literal, Optional

from hitas.models.external_sales_data import CostAreaData, ExternalSalesData, ExternalSalesDataType, QuarterData
from hitas.models.postal_code import HitasPostalCode

if TYPE_CHECKING:
    from hitas.views.external_sales_data import CostAreaSalesCatalogData


def remove_unused_areas(data: "CostAreaSalesCatalogData") -> None:
    """Remove all areas from the Excel sheet that do not have any hitas housing companies for them."""
    postal_codes: set[str] = set(
        HitasPostalCode.objects.exclude(housing_companies__isnull=True).values_list("value", flat=True)
    )

    data["areas"][:] = [area for area in data["areas"] if area["postal_code"] in postal_codes]


def create_external_sales_data(data: "CostAreaSalesCatalogData") -> ExternalSalesData:
    sales_data = ExternalSalesDataType(
        quarter_1=QuarterData(quarter="", areas=[]),
        quarter_2=QuarterData(quarter="", areas=[]),
        quarter_3=QuarterData(quarter="", areas=[]),
        quarter_4=QuarterData(quarter="", areas=[]),
    )

    quarter: Literal["quarter_1", "quarter_2", "quarter_3", "quarter_4"]
    for quarter in sales_data:
        sales_data[quarter]["quarter"] = data[quarter]
        for cost_area in data["areas"]:
            # Do not add cost area to quarter if values don't exist
            sale_count: Optional[int] = cost_area[f"{quarter}_sale_count"]
            price: Optional[int] = cost_area[f"{quarter}_price"]
            if sale_count is None or price is None:
                continue

            sales_data[quarter]["areas"].append(
                CostAreaData(
                    postal_code=cost_area["postal_code"],
                    sale_count=sale_count,
                    price=price,
                )
            )

    return ExternalSalesData.objects.update_or_create(calculation_quarter=data["quarter_4"], defaults=sales_data)[0]
