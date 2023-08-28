from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import Count, Max, OuterRef, Q, QuerySet, Subquery
from django.db.models.functions import Coalesce
from django.utils import timezone

from hitas.models.housing_company import HitasType, RegulationStatus
from hitas.models.owner import Owner, OwnerT
from hitas.models.ownership import Ownership, OwnershipWithApartmentCount
from hitas.utils import SQSum, subquery_count


def exclude_obfuscated_owners(owners: QuerySet[Owner]) -> QuerySet[Owner]:
    """Exclude owners who have already been obfuscated"""
    return owners.exclude(
        name="",
        identifier=None,
        valid_identifier=False,
        email=None,
        bypass_conditions_of_sale=True,
        non_disclosure=False,
    )


def obfuscate_owners_without_regulated_apartments() -> list[OwnerT]:
    """Remove any personal information from owners which do not own any regulated hitas apartments."""
    owners: QuerySet[Owner] = Owner.objects.annotate(
        _owned_regulated_apartments=Coalesce(
            SQSum(
                queryset=(
                    Ownership.objects.select_related(
                        "owner",
                        "sale__apartment__building__real_estate__housing_company",
                    )
                    .filter(
                        owner__id=OuterRef("id"),
                        sale__apartment__building__real_estate__housing_company__regulation_status=(
                            RegulationStatus.REGULATED
                        ),
                    )
                    .annotate(__count=Count("*"))
                    .values_list("__count")
                ),
                output_field=models.IntegerField(),
                sum_field="__count",
            ),
            0,
        ),
        _latest_half_hitas_sale_purchase_date=Subquery(
            queryset=(
                Ownership.objects.select_related(
                    "owner",
                    "sale__apartment__building__real_estate__housing_company",
                )
                .filter(
                    owner__id=OuterRef("id"),
                    sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.HALF_HITAS,
                )
                .annotate(_latest_purchase_date=Max("sale__purchase_date"))
                .values_list("_latest_purchase_date", flat=True)
            ),
            output_field=models.DateField(null=True),
        ),
    ).filter(
        (
            # If owner owns any half-hitas apartments, they must have been purchased
            # at least 2 years ago so that the owner is allowed to be obfuscated
            Q(_latest_half_hitas_sale_purchase_date__isnull=True)
            | Q(_latest_half_hitas_sale_purchase_date__lte=timezone.now().date() - relativedelta(years=2))
        ),
        _owned_regulated_apartments=0,
    )
    owners = exclude_obfuscated_owners(owners)

    # 'non_disclosure' needs to be included temporarily so that we can determine
    # if obfuscation is needed in 'hitas.models.owner.Owner.post_fetch_values_hook'
    obfuscated_owners = list(owners.values("name", "identifier", "email", "non_disclosure"))

    if obfuscated_owners:
        for owner in obfuscated_owners:
            del owner["non_disclosure"]

        owners.update(
            name="",
            identifier=None,
            valid_identifier=False,
            email=None,
            bypass_conditions_of_sale=True,
            non_disclosure=False,
        )

    return obfuscated_owners


def find_owners_with_multiple_ownerships() -> list[OwnershipWithApartmentCount]:
    return list(
        Ownership.objects.select_related(
            "owner",
            "sale__apartment__building__real_estate__housing_company__postal_code",
        )
        .annotate(
            apartment_count=subquery_count(Ownership, "owner"),
        )
        .filter(
            sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
            apartment_count__gt=1,
        )
        .order_by(
            "owner__name",
            "sale__apartment__building__real_estate__housing_company__postal_code__value",
            "sale__apartment__street_address",
        )
    )
