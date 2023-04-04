import dataclasses
import datetime
import uuid
from typing import Any, Dict, Optional

from django.db.models import Case, F, OuterRef, Prefetch, Q, Subquery, Sum, When
from django.db.models.functions import Coalesce, Round, TruncMonth
from django.utils import timezone

from hitas.calculations.exceptions import InvalidCalculationResultException
from hitas.calculations.max_prices.rules_2011_onwards import Rules2011Onwards
from hitas.calculations.max_prices.rules_pre_2011 import RulesPre2011
from hitas.models import (
    Apartment,
    ApartmentConstructionPriceImprovement,
    ApartmentMarketPriceImprovement,
    ApartmentMaximumPriceCalculation,
    ConstructionPriceIndex,
    ConstructionPriceIndex2005Equal100,
    HousingCompany,
    HousingCompanyConstructionPriceImprovement,
    HousingCompanyMarketPriceImprovement,
    MarketPriceIndex,
    MarketPriceIndex2005Equal100,
    Ownership,
    SurfaceAreaPriceCeiling,
)
from hitas.models._base import HitasModelDecimalField
from hitas.models.apartment import ApartmentWithAnnotationsMaxPrice
from hitas.services.apartment import (
    subquery_first_sale_acquisition_price,
    subquery_first_sale_loan_amount,
    subquery_first_sale_purchase_price,
)
from hitas.utils import SQSum, monthify, safe_attrgetter


def create_max_price_calculation(
    housing_company_uuid: uuid.UUID,
    apartment_uuid: uuid.UUID,
    calculation_date: Optional[datetime.date],
    apartment_share_of_housing_company_loans: int,
    apartment_share_of_housing_company_loans_date: Optional[datetime.date],
    additional_info: Optional[str],
) -> Dict[str, Any]:
    #
    # Fetch apartment
    #
    apartment = fetch_apartment(housing_company_uuid, apartment_uuid, calculation_date)

    raise_missing_value_errors(apartment)

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


def raise_missing_value_errors(apartment: ApartmentWithAnnotationsMaxPrice):
    if apartment.completion_date is None:
        raise InvalidCalculationResultException(error_code="missing_completion_date")

    if not apartment.surface_area:
        raise InvalidCalculationResultException(error_code="missing_surface_area")


def calculate_max_price(
    apartment: ApartmentWithAnnotationsMaxPrice,
    calculation_date: Optional[datetime.date],
    apartment_share_of_housing_company_loans: int,
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
    if (
        apartment.completion_date >= datetime.date(2011, 1, 1)
        and not apartment.housing_company.hitas_type.old_hitas_ruleset
    ):
        max_price_calculator = Rules2011Onwards()
        new_hitas_rules = True
    else:
        max_price_calculator = RulesPre2011()
        new_hitas_rules = False

    #
    # Check we found the necessary indices
    #
    max_price_calculator.validate_indices(apartment, calculation_date)

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
        "maximum_price_per_square": max_price / apartment.surface_area,
        "index": max_index,
        "new_hitas": new_hitas_rules,
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
                "name": safe_attrgetter(
                    apartment.housing_company,
                    "property_manager.name",
                    default="",
                ),
                "street_address": safe_attrgetter(
                    apartment.housing_company,
                    "property_manager.street_address",
                    default="",
                ),
            },
        },
        "additional_info": additional_info,
    }


def fetch_apartment(
    housing_company_uuid: uuid.UUID,
    apartment_uuid: uuid.UUID,
    calculation_date: Optional[datetime.date],
) -> ApartmentWithAnnotationsMaxPrice:
    return (
        Apartment.objects.select_related(
            "apartment_type",
            "building",
            "building__real_estate",
            "building__real_estate__housing_company",
            "building__real_estate__housing_company__property_manager",
            "building__real_estate__housing_company__postal_code",
        )
        .prefetch_related(
            Prefetch(
                "ownerships",
                Ownership.objects.select_related("owner"),
            ),
            Prefetch(
                "construction_price_improvements",
                ApartmentConstructionPriceImprovement.objects.annotate(
                    completion_month=TruncMonth("completion_date"),
                    completion_date_index=Subquery(
                        queryset=(
                            ConstructionPriceIndex.objects.filter(
                                month=OuterRef("completion_month"),
                            ).values("value")
                        ),
                        output_field=HitasModelDecimalField(null=True),
                    ),
                ),
            ),
            Prefetch(
                "market_price_improvements",
                ApartmentMarketPriceImprovement.objects.annotate(
                    completion_month=TruncMonth("completion_date"),
                    completion_date_index=Subquery(
                        queryset=(
                            MarketPriceIndex.objects.filter(
                                month=OuterRef("completion_month"),
                            ).values("value")
                        ),
                        output_field=HitasModelDecimalField(null=True),
                    ),
                ),
            ),
            Prefetch(
                "building__real_estate__housing_company__construction_price_improvements",
                HousingCompanyConstructionPriceImprovement.objects.annotate(
                    completion_month=TruncMonth("completion_date"),
                    completion_date_index=Subquery(
                        queryset=(
                            ConstructionPriceIndex.objects.filter(
                                month=OuterRef("completion_month"),
                            ).values("value")
                        ),
                        output_field=HitasModelDecimalField(null=True),
                    ),
                    completion_date_index_2005eq100=Subquery(
                        queryset=(
                            ConstructionPriceIndex2005Equal100.objects.filter(
                                month=OuterRef("completion_month"),
                            ).values("value")
                        ),
                        output_field=HitasModelDecimalField(null=True),
                    ),
                ),
            ),
            Prefetch(
                "building__real_estate__housing_company__market_price_improvements",
                HousingCompanyMarketPriceImprovement.objects.annotate(
                    completion_month=TruncMonth("completion_date"),
                    completion_date_index=Subquery(
                        queryset=(
                            MarketPriceIndex.objects.filter(
                                month=OuterRef("completion_month"),
                            ).values("value")
                        ),
                        output_field=HitasModelDecimalField(null=True),
                    ),
                    completion_date_index_2005eq100=Subquery(
                        queryset=(
                            MarketPriceIndex2005Equal100.objects.filter(
                                month=OuterRef("completion_month"),
                            ).values("value")
                        ),
                        output_field=HitasModelDecimalField(null=True),
                    ),
                ),
            ),
        )
        .annotate(
            _first_sale_purchase_price=subquery_first_sale_purchase_price("id"),
            _first_sale_share_of_housing_company_loans=subquery_first_sale_loan_amount("id"),
            completion_month=TruncMonth("completion_date"),
            calculation_date_cpi=Subquery(
                queryset=(
                    ConstructionPriceIndex.objects.filter(
                        month=monthify(calculation_date),
                    ).values("value")
                ),
                output_field=HitasModelDecimalField(null=True),
            ),
            calculation_date_cpi_2005eq100=Subquery(
                queryset=(
                    ConstructionPriceIndex2005Equal100.objects.filter(
                        month=monthify(calculation_date),
                    ).values("value")
                ),
                output_field=HitasModelDecimalField(null=True),
            ),
            completion_date_cpi=Subquery(
                queryset=(
                    ConstructionPriceIndex.objects.filter(
                        month=OuterRef("completion_month"),
                    ).values("value")
                ),
                output_field=HitasModelDecimalField(null=True),
            ),
            completion_date_cpi_2005eq100=Subquery(
                queryset=(
                    ConstructionPriceIndex2005Equal100.objects.filter(
                        month=OuterRef("completion_month"),
                    ).values("value")
                ),
                output_field=HitasModelDecimalField(null=True),
            ),
            calculation_date_mpi=Subquery(
                queryset=(
                    MarketPriceIndex.objects.filter(
                        month=monthify(calculation_date),
                    ).values("value")
                ),
                output_field=HitasModelDecimalField(null=True),
            ),
            calculation_date_mpi_2005eq100=Subquery(
                queryset=(
                    MarketPriceIndex2005Equal100.objects.filter(
                        month=monthify(calculation_date),
                    ).values("value")
                ),
                output_field=HitasModelDecimalField(null=True),
            ),
            completion_date_mpi=Subquery(
                queryset=(
                    MarketPriceIndex.objects.filter(
                        month=OuterRef("completion_month"),
                    ).values("value")
                ),
                output_field=HitasModelDecimalField(null=True),
            ),
            completion_date_mpi_2005eq100=Subquery(
                queryset=(
                    MarketPriceIndex2005Equal100.objects.filter(
                        month=OuterRef("completion_month"),
                    ).values("value")
                ),
                output_field=HitasModelDecimalField(null=True),
            ),
            surface_area_price_ceiling_m2=Subquery(
                queryset=(
                    SurfaceAreaPriceCeiling.objects.filter(
                        month=monthify(calculation_date),
                    ).values("value")
                ),
                output_field=HitasModelDecimalField(null=True),
            ),
            surface_area_price_ceiling=Round(F("surface_area_price_ceiling_m2") * F("surface_area")),
            realized_housing_company_acquisition_price=(
                Coalesce(
                    SQSum(
                        queryset=(
                            Apartment.objects.filter(
                                building__real_estate__housing_company__uuid=housing_company_uuid,
                            ).annotate(
                                _price=Case(
                                    When(
                                        condition=Q(sales__isnull=True),
                                        then=Sum(F("catalog_purchase_price") + F("catalog_primary_loan_amount")),
                                    ),
                                    default=subquery_first_sale_acquisition_price("id"),
                                    output_field=HitasModelDecimalField(),
                                ),
                            )
                        ),
                        sum_field="_price",
                    ),
                    0.0,
                    output_field=HitasModelDecimalField(),
                )
            ),
            completion_date_realized_housing_company_acquisition_price=(
                Coalesce(
                    SQSum(
                        queryset=(
                            Apartment.objects.filter(
                                building__real_estate__housing_company__uuid=housing_company_uuid,
                                completion_date=OuterRef("completion_date"),
                            ).annotate(
                                _price=Case(
                                    When(
                                        condition=Q(sales__isnull=True),
                                        then=Sum(F("catalog_purchase_price") + F("catalog_primary_loan_amount")),
                                    ),
                                    default=subquery_first_sale_acquisition_price("id"),
                                    output_field=HitasModelDecimalField(),
                                ),
                            )
                        ),
                        sum_field="_price",
                    ),
                    0.0,
                    output_field=HitasModelDecimalField(),
                )
            ),
        )
        .get(uuid=apartment_uuid, building__real_estate__housing_company__uuid=housing_company_uuid)
    )
