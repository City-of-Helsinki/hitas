import dataclasses
import datetime
import uuid
from decimal import Decimal
from typing import Any, Dict, Optional

from django.db.models import Prefetch, Sum
from django.utils import timezone

from hitas.calculations.max_prices.rules_2011_onwards import Rules2011Onwards
from hitas.calculations.max_prices.rules_pre_2011 import RulesPre2011
from hitas.models import (
    Apartment,
    ApartmentConstructionPriceImprovement,
    ApartmentMarketPriceImprovement,
    ApartmentMaximumPriceCalculation,
    HousingCompany,
    HousingCompanyConstructionPriceImprovement,
    HousingCompanyMarketPriceImprovement,
    Ownership,
)


def create_max_price_calculation(
    housing_company_uuid: str,
    apartment_uuid: str,
    calculation_date: Optional[datetime.date],
    apartment_share_of_housing_company_loans: Decimal,
    apartment_share_of_housing_company_loans_date: Optional[datetime.date],
    additional_info: Optional[str],
) -> Dict[str, Any]:
    #
    # Fetch apartment
    #
    apartment = fetch_apartment(housing_company_uuid, apartment_uuid, calculation_date)

    # Do the calculation
    calculation = calculate_max_price(
        apartment,
        calculation_date,
        apartment_share_of_housing_company_loans,
        apartment_share_of_housing_company_loans_date,
        additional_info,
    )

    #
    # Save the calculation
    #
    ApartmentMaximumPriceCalculation.objects.create(
        uuid=calculation["id"],
        apartment=apartment,
        maximum_price=calculation["maximum_price"],
        created_at=calculation["created_at"],
        valid_until=calculation["valid_until"],
        calculation_date=calculation_date,
        json=calculation,
    )

    # Don't save this to calculation json
    calculation["confirmed_at"] = None

    return calculation


def calculate_max_price(
    apartment: Apartment,
    calculation_date: Optional[datetime.date],
    apartment_share_of_housing_company_loans: Decimal,
    apartment_share_of_housing_company_loans_date: Optional[datetime.date],
    additional_info: str = "",
) -> Dict[str, Any]:
    if calculation_date is None:
        calculation_date = timezone.now().today()

    if apartment_share_of_housing_company_loans_date is None:
        calculation_date = timezone.now().today()

    #
    # Fetch housing company's total surface area
    #
    total_surface_area = (
        HousingCompany.objects.annotate(sum_surface_area=Sum("real_estates__buildings__apartments__surface_area"))
        .only("id")
        .get(id=apartment.housing_company.id)
        .sum_surface_area
    )

    # Select calculator
    if apartment.completion_date >= datetime.date(2011, 1, 1) and apartment.notes != "FIXME: old rules":
        max_price_calculator = Rules2011Onwards()
    else:
        max_price_calculator = RulesPre2011()

    #
    # Check we found the necessary indices
    #
    max_price_calculator.validate_indices(apartment)

    #
    # Do the max price calculations for each index and surface area price ceiling
    #
    construction_price_index = max_price_calculator.calculate_construction_price_index_max_price(
        apartment,
        total_surface_area,
        apartment_share_of_housing_company_loans,
        apartment_share_of_housing_company_loans_date,
        apartment.construction_price_improvements.all(),
        apartment.housing_company.construction_price_improvements.all(),
        calculation_date,
    )
    market_price_index = max_price_calculator.calculate_market_price_index_max_price(
        apartment,
        total_surface_area,
        apartment_share_of_housing_company_loans,
        apartment_share_of_housing_company_loans_date,
        apartment.market_price_improvements.all(),
        apartment.housing_company.market_price_improvements.all(),
        calculation_date,
    )
    surface_area_price_ceiling = max_price_calculator.calculate_surface_area_price_ceiling(
        apartment,
        apartment_share_of_housing_company_loans,
        apartment_share_of_housing_company_loans_date,
        calculation_date,
    )

    #
    # Find and mark the maximum
    #
    max_price = max(
        construction_price_index.maximum_price,
        market_price_index.maximum_price,
        surface_area_price_ceiling.maximum_price,
    )

    surface_area_price_ceiling.maximum = max_price == surface_area_price_ceiling.maximum_price
    market_price_index.maximum = max_price == market_price_index.maximum_price
    construction_price_index.maximum = max_price == construction_price_index.maximum_price

    if market_price_index.maximum:
        max_index = "market_price_index"
        valid_until = market_price_index.valid_until
    elif construction_price_index.maximum:
        max_index = "construction_price_index"
        valid_until = construction_price_index.valid_until
    else:
        max_index = "surface_area_price_ceiling"
        valid_until = surface_area_price_ceiling.valid_until

    #
    # Create calculation json object
    #
    return {
        "id": uuid.uuid4().hex,
        "created_at": timezone.now(),
        "calculation_date": calculation_date,
        "valid_until": valid_until,
        "maximum_price": max_price,
        "index": max_index,
        "calculations": {
            "construction_price_index": dataclasses.asdict(construction_price_index),
            "market_price_index": dataclasses.asdict(market_price_index),
            "surface_area_price_ceiling": dataclasses.asdict(surface_area_price_ceiling),
        },
        "apartment": {
            "shares": {
                "start": apartment.share_number_start,
                "end": apartment.share_number_end,
                "total": apartment.share_number_end - apartment.share_number_start + 1,
            },
            "rooms": apartment.rooms,
            "type": apartment.apartment_type.value,
            "surface_area": apartment.surface_area,
            "address": {
                "street_address": apartment.street_address,
                "floor": apartment.floor,
                "stair": apartment.stair,
                "apartment_number": apartment.apartment_number,
                "postal_code": apartment.postal_code.value,
                "city": apartment.postal_code.city,
            },
            "ownerships": [
                {"percentage": ownership.percentage, "name": ownership.owner.name}
                for ownership in apartment.ownerships.all()
            ],
        },
        "housing_company": {
            "official_name": apartment.housing_company.official_name,
            "archive_id": apartment.housing_company.id,
            "property_manager": {
                "name": apartment.housing_company.property_manager.name,
                "street_address": apartment.housing_company.property_manager.street_address,
            },
        },
        "additional_info": additional_info,
    }


def fetch_apartment(
    housing_company_uuid: str,
    apartment_uuid: str,
    calculation_date: Optional[datetime.date],
) -> Apartment:
    return (
        Apartment.objects.only(
            "additional_work_during_construction",
            "share_number_start",
            "share_number_end",
            "street_address",
            "floor",
            "stair",
            "apartment_number",
            "rooms",
            "apartment_type_id",
            "surface_area",
            "completion_date",
            "debt_free_purchase_price",
            "primary_loan_amount",
            "apartment_type__value",
            "building__real_estate__housing_company__id",
            "building__real_estate__housing_company__official_name",
            "building__real_estate__housing_company__postal_code__value",
            "building__real_estate__housing_company__postal_code__city",
            "building__real_estate__housing_company__property_manager__name",
            "building__real_estate__housing_company__property_manager__street_address",
        )
        .select_related(
            "apartment_type",
            "building__real_estate__housing_company",
            "building__real_estate__housing_company__property_manager",
            "building__real_estate__housing_company__postal_code",
        )
        .prefetch_related(
            Prefetch(
                "ownerships",
                Ownership.objects.only("apartment_id", "percentage", "owner__name").select_related("owner"),
            ),
            Prefetch(
                "construction_price_improvements",
                ApartmentConstructionPriceImprovement.objects.only(
                    "value", "apartment_id", "depreciation_percentage"
                ).extra(
                    select={
                        "completion_date_index": """
    SELECT completion_date_index.value
    FROM hitas_constructionpriceindex AS completion_date_index
    WHERE completion_date_index.month
         = DATE_TRUNC('month', hitas_apartmentconstructionpriceimprovement.completion_date)
    """,
                    },
                ),
            ),
            Prefetch(
                "market_price_improvements",
                ApartmentMarketPriceImprovement.objects.only("value", "apartment_id").extra(
                    select={
                        "completion_date_index": """
    SELECT completion_date_index.value
    FROM hitas_marketpriceindex AS completion_date_index
    WHERE completion_date_index.month
         = DATE_TRUNC('month', hitas_apartmentmarketpriceimprovement.completion_date)
    """,
                    },
                ),
            ),
            Prefetch(
                "building__real_estate__housing_company__construction_price_improvements",
                HousingCompanyConstructionPriceImprovement.objects.only("value", "housing_company_id",).extra(
                    select={
                        "completion_date_index_2005eq100": """
    SELECT completion_date_index.value
    FROM hitas_constructionpriceindex2005equal100 AS completion_date_index
    WHERE completion_date_index.month
         = DATE_TRUNC('month', hitas_housingcompanyconstructionpriceimprovement.completion_date)
    """,
                        "completion_date_index": """
    SELECT completion_date_index.value
    FROM hitas_constructionpriceindex AS completion_date_index
    WHERE completion_date_index.month
         = DATE_TRUNC('month', hitas_housingcompanyconstructionpriceimprovement.completion_date)
    """,
                    },
                ),
            ),
            Prefetch(
                "building__real_estate__housing_company__market_price_improvements",
                HousingCompanyMarketPriceImprovement.objects.only("value", "housing_company_id",).extra(
                    select={
                        "completion_date_index_2005eq100": """
    SELECT completion_date_index.value
    FROM hitas_marketpriceindex2005equal100 AS completion_date_index
    WHERE completion_date_index.month
         = DATE_TRUNC('month', hitas_housingcompanymarketpriceimprovement.completion_date)
    """,
                        "completion_date_index": """
    SELECT completion_date_index.value
    FROM hitas_marketpriceindex AS completion_date_index
    WHERE completion_date_index.month
         = DATE_TRUNC('month', hitas_housingcompanymarketpriceimprovement.completion_date)
    """,
                    },
                ),
            ),
        )
        .extra(
            select={
                "calculation_date_cpi": """
SELECT calculation_date_index.value
FROM hitas_constructionpriceindex AS calculation_date_index
WHERE calculation_date_index.month = DATE_TRUNC('month', %s)
""",
                "calculation_date_cpi_2005eq100": """
SELECT calculation_date_index.value
FROM hitas_constructionpriceindex2005equal100 AS calculation_date_index
WHERE calculation_date_index.month = DATE_TRUNC('month', %s)
""",
                "completion_date_cpi": """
SELECT completion_date_index.value
FROM hitas_apartment AS a
LEFT JOIN hitas_constructionpriceindex AS completion_date_index ON
    completion_date_index.month = DATE_TRUNC('month', a.completion_date)
WHERE a.id = hitas_apartment.id
""",
                "completion_date_cpi_2005eq100": """
SELECT completion_date_index.value
FROM hitas_apartment AS a
LEFT JOIN hitas_constructionpriceindex2005equal100 AS completion_date_index ON
    completion_date_index.month = DATE_TRUNC('month', a.completion_date)
WHERE a.id = hitas_apartment.id
""",
                "calculation_date_mpi": """
SELECT calculation_date_index.value
FROM hitas_marketpriceindex AS calculation_date_index
WHERE calculation_date_index.month = DATE_TRUNC('month', %s)
""",
                "calculation_date_mpi_2005eq100": """
SELECT calculation_date_index.value
FROM hitas_marketpriceindex2005equal100 AS calculation_date_index
WHERE calculation_date_index.month = DATE_TRUNC('month', %s)
""",
                "completion_date_mpi": """
SELECT completion_date_index.value
FROM hitas_apartment AS a
LEFT JOIN hitas_marketpriceindex AS completion_date_index ON
    completion_date_index.month = DATE_TRUNC('month', a.completion_date)
WHERE a.id = hitas_apartment.id
""",
                "completion_date_mpi_2005eq100": """
SELECT completion_date_index.value
FROM hitas_apartment AS a
LEFT JOIN hitas_marketpriceindex2005equal100 AS completion_date_index ON
    completion_date_index.month = DATE_TRUNC('month', a.completion_date)
WHERE a.id = hitas_apartment.id
""",
                "surface_area_price_ceiling": """
    SELECT ROUND(a.surface_area * sapc.value)
    FROM hitas_apartment AS a
    LEFT JOIN hitas_surfaceareapriceceiling AS sapc
        ON sapc.month = DATE_TRUNC('month', %s)
    WHERE a.id = hitas_apartment.id
""",
                "surface_area_price_ceiling_m2": """
    SELECT value
    FROM hitas_surfaceareapriceceiling
    WHERE month = DATE_TRUNC('month', %s)
""",
                "realized_housing_company_acquisition_price": """
    SELECT
        SUM(a.debt_free_purchase_price + a.primary_loan_amount)
    FROM hitas_apartment AS a
        LEFT JOIN hitas_building AS b ON a.building_id = b.id
        LEFT JOIN hitas_realestate AS r on r.id = b.real_estate_id
        LEFT JOIN hitas_housingcompany AS hc ON hc.id = r.housing_company_id
        WHERE hc.id = hitas_housingcompany.id
""",
                "completion_date_realized_housing_company_acquisition_price": """
    SELECT
        SUM(a.debt_free_purchase_price + a.primary_loan_amount)
    FROM hitas_apartment AS a
        LEFT JOIN hitas_building AS b ON a.building_id = b.id
        LEFT JOIN hitas_realestate AS r on r.id = b.real_estate_id
        LEFT JOIN hitas_housingcompany AS hc ON hc.id = r.housing_company_id
        WHERE hc.id = hitas_housingcompany.id
            AND a.completion_date = hitas_apartment.completion_date
""",
            },
            select_params=[calculation_date] * 6,
        )
        .get(uuid=apartment_uuid, building__real_estate__housing_company__uuid=housing_company_uuid)
    )
