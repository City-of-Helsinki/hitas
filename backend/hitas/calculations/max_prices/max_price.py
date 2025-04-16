import dataclasses
import datetime
import uuid
from decimal import Decimal
from typing import Any, Dict, Optional

from django.db import models
from django.db.models import Case, F, Max, OuterRef, Prefetch, Q, Subquery, Sum, Value, When
from django.db.models.functions import Coalesce, Greatest, Round, TruncMonth
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
from hitas.models.housing_company import HitasType
from hitas.services.apartment import (
    get_first_sale_acquisition_price,
    get_first_sale_loan_amount,
    get_first_sale_purchase_date,
    get_first_sale_purchase_price,
    prefetch_latest_sale,
)
from hitas.utils import SQSum, max_date_if_all_not_null, monthify, safe_attrgetter


class HousingCompanyWithAnnotationsMaxPrice(HousingCompany):
    _completion_date: Optional[datetime.date]
    sum_surface_area: Optional[Decimal]

    class Meta:
        abstract = True


def create_max_price_calculation(
    housing_company_uuid: uuid.UUID,
    apartment_uuid: uuid.UUID,
    calculation_date: datetime.date,
    apartment_share_of_housing_company_loans: int,
    apartment_share_of_housing_company_loans_date: datetime.date,
    additional_info: Optional[str],
) -> Dict[str, Any]:
    non_deleted = Q(real_estates__buildings__apartments__deleted__isnull=True)
    housing_company = HousingCompany.objects.annotate(
        _completion_date=max_date_if_all_not_null("real_estates__buildings__apartments__completion_date"),
        _last_apartment_completion_date=Max("real_estates__buildings__apartments__completion_date", filter=non_deleted),
        sum_surface_area=Sum("real_estates__buildings__apartments__surface_area", filter=non_deleted),
    ).get(uuid=housing_company_uuid)

    # For RR_NEW_HITAS housing companies (Ryhmärakentamiskohde kohde), the completion date is the date of the last
    # completed apartment to allow for re-sale of completed apartments while some are still under construction
    if housing_company.hitas_type == HitasType.RR_NEW_HITAS:
        housing_company._completion_date = housing_company._last_apartment_completion_date
        validate_rr_housing_company_for_max_price_calculation(housing_company)

    if housing_company.completion_date is None:
        raise InvalidCalculationResultException(
            error_code="missing_housing_company_completion_date",
            message="Cannot create max price calculation for a housing company without completion date.",
        )
    elif housing_company.completion_date > timezone.now().date():
        raise InvalidCalculationResultException(
            error_code="completion_date_in_future",
            message="Cannot create max price calculation for a housing company with completion date in the future.",
        )

    apartment = fetch_apartment(
        housing_company=housing_company,
        apartment_uuid=apartment_uuid,
        calculation_month=monthify(calculation_date),
    )

    validate_apartment_for_max_price_calculation(apartment)

    #
    # Do the calculation
    #
    calculation = calculate_max_price(
        housing_company,
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


def validate_rr_housing_company_for_max_price_calculation(housing_company: HousingCompanyWithAnnotationsMaxPrice):
    # RR_NEW_HITAS housing companies are allowed to have apartments with completion date, but still need to have
    # surface area and share numbers for all apartments, as they affect the max price calculation
    apartment_missing_data = (
        Apartment.objects.filter(building__real_estate__housing_company=housing_company)
        .filter(Q(surface_area__isnull=True) | Q(share_number_start__isnull=True) | Q(share_number_end__isnull=True))
        .first()
    )
    if apartment_missing_data is not None:
        if apartment_missing_data.surface_area is None:
            raise InvalidCalculationResultException(
                error_code="missing_surface_area_for_apartment",
                message="Cannot create max price calculation as an apartment is missing surface area.",
            )
        elif apartment_missing_data.share_number_start is None or apartment_missing_data.share_number_end is None:
            raise InvalidCalculationResultException(
                error_code="missing_share_numbers_for_apartment",
                message="Cannot create max price calculation for as an apartment is missing share numbers.",
            )


def validate_apartment_for_max_price_calculation(apartment: ApartmentWithAnnotationsMaxPrice):
    if not apartment.surface_area:
        raise InvalidCalculationResultException(
            error_code="missing_surface_area",
            message="Cannot create max price calculation for an apartment without surface area.",
        )

    if apartment.first_sale_purchase_price is None:
        raise InvalidCalculationResultException(
            error_code="apartment_first_sale_purchase_price_missing",
            message="Cannot create max price calculation for an apartment without a first sale purchase price.",
        )
    if apartment.first_sale_share_of_housing_company_loans is None:
        raise InvalidCalculationResultException(
            error_code="apartment_first_sale_share_of_loans_missing",
            message="Cannot create max price calculation for an apartment without a first sale loan amount.",
        )

    if apartment.completion_date is None:
        raise InvalidCalculationResultException(
            error_code="missing_completion_date",
            message="Cannot create max price calculation for an apartment without completion date.",
        )

    if apartment.housing_company.release_date:
        raise InvalidCalculationResultException(
            error_code="unregulated_housing_company",
            message="Cannot create max price calculations for apartments in non-regulated housing companies.",
        )


def calculate_max_price(
    housing_company: HousingCompanyWithAnnotationsMaxPrice,
    apartment: ApartmentWithAnnotationsMaxPrice,
    calculation_date: datetime.date,
    apartment_share_of_housing_company_loans: int,
    apartment_share_of_housing_company_loans_date: datetime.date,
    additional_info: str = "",
) -> Dict[str, Any]:
    # Select calculator
    new_hitas_ruleset = housing_company.hitas_type.new_hitas_ruleset
    max_price_calculator = Rules2011Onwards() if new_hitas_ruleset else RulesPre2011()

    #
    # Check we found the necessary indices
    #
    max_price_calculator.validate_indices(apartment, calculation_date)

    #
    # Do the max price calculations for each index and surface area price ceiling
    #
    construction_price_index = max_price_calculator.calculate_construction_price_index_max_price(
        apartment,
        housing_company.sum_surface_area,
        apartment_share_of_housing_company_loans,
        apartment_share_of_housing_company_loans_date,
        apartment.construction_price_improvements.all(),
        apartment.housing_company.construction_price_improvements.all(),
        calculation_date,
        housing_company.completion_date,
    )
    market_price_index = max_price_calculator.calculate_market_price_index_max_price(
        apartment,
        housing_company.sum_surface_area,
        apartment_share_of_housing_company_loans,
        apartment_share_of_housing_company_loans_date,
        apartment.market_price_improvements.all(),
        apartment.housing_company.market_price_improvements.all(),
        calculation_date,
        housing_company.completion_date,
    )
    surface_area_price_ceiling = max_price_calculator.calculate_surface_area_price_ceiling_max_price(
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
        "new_hitas": new_hitas_ruleset,
        "calculations": {
            "construction_price_index": dataclasses.asdict(construction_price_index),
            "market_price_index": dataclasses.asdict(market_price_index),
            "surface_area_price_ceiling": dataclasses.asdict(surface_area_price_ceiling),
        },
        "apartment": {
            "shares": {
                "start": apartment.share_number_start,
                "end": apartment.share_number_end,
                "total": apartment.shares_count,
            },
            "rooms": apartment.rooms,
            "type": safe_attrgetter(apartment, "apartment_type.value", default=None),
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
                for sale in apartment.sales.all()  # only the latest sale prefetched, or empty if no sales
                for ownership in sale.ownerships.all()
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
            },
        },
        "additional_info": additional_info,
    }


def fetch_apartment(
    housing_company: HousingCompany,
    apartment_uuid: uuid.UUID,
    calculation_month: datetime.date,
) -> ApartmentWithAnnotationsMaxPrice:
    is_new_hitas = housing_company.hitas_type.new_hitas_ruleset

    qs = (
        Apartment.objects.select_related(
            "apartment_type",
            "building",
            "building__real_estate",
            "building__real_estate__housing_company",
            "building__real_estate__housing_company__property_manager",
            "building__real_estate__housing_company__postal_code",
        )
        .prefetch_related(
            prefetch_latest_sale(include_first_sale=True),
            Prefetch(
                "sales__ownerships",
                Ownership.objects.select_related("owner"),
            ),
        )
        .annotate(
            _first_sale_purchase_date=get_first_sale_purchase_date("id"),
            _first_sale_purchase_price=get_first_sale_purchase_price("id"),
            _first_sale_share_of_housing_company_loans=get_first_sale_loan_amount("id"),
            surface_area_price_ceiling_m2=Subquery(
                queryset=(
                    SurfaceAreaPriceCeiling.objects.filter(
                        month=calculation_month,
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
                                building__real_estate__housing_company=housing_company,
                            )
                            .annotate(
                                _price=Case(
                                    When(
                                        condition=Q(sales__isnull=True),
                                        then=Sum(F("catalog_purchase_price") + F("catalog_primary_loan_amount")),
                                    ),
                                    default=get_first_sale_acquisition_price("id"),
                                    output_field=HitasModelDecimalField(),
                                ),
                            )
                            .distinct()
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
                                building__real_estate__housing_company=housing_company,
                                completion_date=OuterRef("completion_date"),
                            )
                            .annotate(
                                _price=Case(
                                    When(
                                        condition=Q(sales__isnull=True),
                                        then=Sum(F("catalog_purchase_price") + F("catalog_primary_loan_amount")),
                                    ),
                                    default=get_first_sale_acquisition_price("id"),
                                    output_field=HitasModelDecimalField(),
                                ),
                            )
                            .distinct()
                        ),
                        sum_field="_price",
                    ),
                    0.0,
                    output_field=HitasModelDecimalField(),
                )
            ),
        )
    )

    # New Hitas
    # Index date is selected by housing company completion date
    if is_new_hitas:
        qs = qs.prefetch_related(
            # New hitas apartment improvements are not counted, so we don't need to fetch them here
            Prefetch(
                "building__real_estate__housing_company__construction_price_improvements",
                # Intentionally use MarketPriceImprovements, as new hitas housing companies only use them,
                # but we still need to use the Construction Price Index for calculating max price
                HousingCompanyMarketPriceImprovement.objects.annotate(
                    completion_month=TruncMonth("completion_date"),
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
        ).annotate(
            completion_month=Value(
                housing_company.completion_date and monthify(housing_company.completion_date or None),
                output_field=models.DateField(),
            ),
            calculation_date_cpi_2005eq100=Subquery(
                queryset=(ConstructionPriceIndex2005Equal100.objects.filter(month=calculation_month).values("value")),
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
            calculation_date_mpi_2005eq100=Subquery(
                queryset=(MarketPriceIndex2005Equal100.objects.filter(month=calculation_month).values("value")),
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
        )

    # Old Hitas
    # Index date is selected by the apartment completion date
    else:
        qs = qs.prefetch_related(
            Prefetch(
                "construction_price_improvements",
                ApartmentConstructionPriceImprovement.objects.annotate(
                    completion_month=TruncMonth("completion_date"),
                    completion_date_index=Subquery(
                        queryset=(
                            ConstructionPriceIndex.objects.filter(month=OuterRef("completion_month")).values("value")
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
                        queryset=(MarketPriceIndex.objects.filter(month=OuterRef("completion_month")).values("value")),
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
                            ConstructionPriceIndex.objects.filter(month=OuterRef("completion_month")).values("value")
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
                        queryset=(MarketPriceIndex.objects.filter(month=OuterRef("completion_month")).values("value")),
                        output_field=HitasModelDecimalField(null=True),
                    ),
                ),
            ),
        ).annotate(
            completion_month=TruncMonth("completion_date"),
            cpi_completion_month=TruncMonth(Greatest("completion_month", "_first_sale_purchase_date")),
            calculation_date_cpi=Subquery(
                queryset=(ConstructionPriceIndex.objects.filter(month=calculation_month).values("value")),
                output_field=HitasModelDecimalField(null=True),
            ),
            completion_date_cpi=Subquery(
                queryset=(
                    ConstructionPriceIndex.objects.filter(
                        # Special rule for Old Hitas CPI:
                        # Index date is chosen by apartment completion date or the first sale date, whichever is latest
                        month=OuterRef("cpi_completion_month"),
                    ).values("value")
                ),
                output_field=HitasModelDecimalField(null=True),
            ),
            calculation_date_mpi=Subquery(
                queryset=(MarketPriceIndex.objects.filter(month=calculation_month).values("value")),
                output_field=HitasModelDecimalField(null=True),
            ),
            completion_date_mpi=Subquery(
                queryset=(MarketPriceIndex.objects.filter(month=OuterRef("completion_month")).values("value")),
                output_field=HitasModelDecimalField(null=True),
            ),
        )

    return qs.get(uuid=apartment_uuid, building__real_estate__housing_company=housing_company)
