from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from hitas.models import ConditionOfSale, Owner, Ownership
from hitas.models.condition_of_sale import ConditionOfSaleAnnotated
from hitas.services.apartment import subquery_first_purchase_date


def condition_of_sale_queryset() -> models.QuerySet[ConditionOfSaleAnnotated]:
    return (
        ConditionOfSale.all_objects.filter(
            models.Q(deleted__isnull=True)
            | models.Q(deleted__gte=timezone.now() - settings.SHOW_FULFILLED_CONDITIONS_OF_SALE_FOR_MONTHS)
        )
        .select_related(
            "new_ownership__owner",
            "new_ownership__apartment",
            "old_ownership__owner",
            "old_ownership__apartment",
            "new_ownership__apartment__building",
            "old_ownership__apartment__building",
            "new_ownership__apartment__building__real_estate",
            "old_ownership__apartment__building__real_estate",
            "new_ownership__apartment__building__real_estate__housing_company",
            "old_ownership__apartment__building__real_estate__housing_company",
            "new_ownership__apartment__building__real_estate__housing_company__postal_code",
            "old_ownership__apartment__building__real_estate__housing_company__postal_code",
        )
        .annotate(
            first_purchase_date=subquery_first_purchase_date("new_ownership__apartment__id"),
        )
        .only(
            "id",
            "uuid",
            "grace_period",
            "deleted",
            "new_ownership__id",
            "new_ownership__percentage",
            "old_ownership__id",
            "old_ownership__percentage",
            # New ownership apartment
            "new_ownership__apartment__id",
            "new_ownership__apartment__uuid",
            "new_ownership__apartment__street_address",
            "new_ownership__apartment__apartment_number",
            "new_ownership__apartment__floor",
            "new_ownership__apartment__stair",
            "new_ownership__apartment__completion_date",
            # Old ownership apartment
            "old_ownership__apartment__id",
            "old_ownership__apartment__uuid",
            "old_ownership__apartment__street_address",
            "old_ownership__apartment__apartment_number",
            "old_ownership__apartment__floor",
            "old_ownership__apartment__stair",
            "old_ownership__apartment__completion_date",
            # New ownership owner
            "new_ownership__owner__id",
            "new_ownership__owner__uuid",
            "new_ownership__owner__name",
            "new_ownership__owner__identifier",
            "new_ownership__owner__email",
            # Old ownership owner
            "old_ownership__owner__id",
            "old_ownership__owner__uuid",
            "old_ownership__owner__name",
            "old_ownership__owner__identifier",
            "old_ownership__owner__email",
            # Housing company info
            "new_ownership__apartment__building__real_estate__housing_company__uuid",
            "old_ownership__apartment__building__real_estate__housing_company__uuid",
            "new_ownership__apartment__building__real_estate__housing_company__display_name",
            "old_ownership__apartment__building__real_estate__housing_company__display_name",
            # Address info
            "new_ownership__apartment__building__real_estate__housing_company__postal_code__value",
            "old_ownership__apartment__building__real_estate__housing_company__postal_code__value",
            "new_ownership__apartment__building__real_estate__housing_company__postal_code__city",
            "old_ownership__apartment__building__real_estate__housing_company__postal_code__city",
        )
    )


def create_conditions_of_sale(owners: list["Owner"]) -> list[ConditionOfSale]:
    ownerships: list[Ownership] = [
        ownership for owner in owners for ownership in owner.ownerships.all() if not owner.bypass_conditions_of_sale
    ]

    to_save: dict[tuple[int, int], ConditionOfSale] = {}

    # Create conditions of sale for all ownerships to new apartments this owner has,
    # and all the additional ownerships given (if they are for new apartments)
    for ownership in ownerships:
        apartment = ownership.apartment

        if apartment.is_new:
            for other_ownership in ownerships:
                # Don't create circular conditions of sale
                if ownership.id == other_ownership.id:
                    continue

                # Only one condition of sale between two new apartments
                key: tuple[int, int] = tuple(sorted([ownership.id, other_ownership.id]))  # type: ignore
                if key in to_save:
                    continue

                to_save[key] = ConditionOfSale(new_ownership=ownership, old_ownership=other_ownership)

    if not to_save:
        return []

    # 'ignore_conflicts' so that we can create all missing conditions of sale if some already exist
    ConditionOfSale.objects.bulk_create(to_save.values(), ignore_conflicts=True)

    # We have to fetch ownerships separately, since if only some conditions of sale in 'to_save' were created,
    # the ids or conditions of sale in the returned list from 'bulk_create' are not correct.
    return list(
        condition_of_sale_queryset()
        .filter(Q(new_ownership__owner__in=owners) | Q(old_ownership__owner__in=owners))
        .all()
    )
