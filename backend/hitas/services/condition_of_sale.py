from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from hitas.models import ConditionOfSale, Owner, Ownership
from hitas.models.condition_of_sale import ConditionOfSaleAnnotated
from hitas.models.housing_company import RegulationStatus
from hitas.services.apartment import get_first_sale_purchase_date


def condition_of_sale_queryset() -> models.QuerySet[ConditionOfSaleAnnotated]:
    return (
        ConditionOfSale.all_objects.filter(
            models.Q(deleted__isnull=True)
            | models.Q(deleted__gte=timezone.now() - settings.SHOW_FULFILLED_CONDITIONS_OF_SALE_FOR_MONTHS)
        )
        .select_related(
            "new_ownership__owner",
            "new_ownership__sale",
            "old_ownership__owner",
            "old_ownership__sale",
            "new_ownership__sale__apartment",
            "old_ownership__sale__apartment",
            "new_ownership__sale__apartment__building",
            "old_ownership__sale__apartment__building",
            "new_ownership__sale__apartment__building__real_estate",
            "old_ownership__sale__apartment__building__real_estate",
            "new_ownership__sale__apartment__building__real_estate__housing_company",
            "old_ownership__sale__apartment__building__real_estate__housing_company",
            "new_ownership__sale__apartment__building__real_estate__housing_company__postal_code",
            "old_ownership__sale__apartment__building__real_estate__housing_company__postal_code",
        )
        .annotate(
            first_purchase_date=get_first_sale_purchase_date("new_ownership__sale__apartment__id"),
        )
    )


def create_conditions_of_sale(owners: list["Owner"]) -> list[ConditionOfSale]:
    ownerships: list[Ownership] = [
        ownership for owner in owners for ownership in owner.ownerships.all() if not owner.bypass_conditions_of_sale
    ]

    conditions_of_sale = determine_conditions_of_sale(ownerships)
    if not conditions_of_sale:
        return []

    # 'ignore_conflicts' so that we can create all missing conditions of sale if some already exist
    ConditionOfSale.objects.bulk_create(conditions_of_sale, ignore_conflicts=True)

    # We have to fetch ownerships separately, since if only some conditions of sale in 'to_save' were created,
    # the ids or conditions of sale in the returned list from 'bulk_create' are not correct.
    return list(
        condition_of_sale_queryset()
        .filter(Q(new_ownership__owner__in=owners) | Q(old_ownership__owner__in=owners))
        .all()
    )


def determine_conditions_of_sale(ownerships: list[Ownership]) -> list[ConditionOfSale]:
    to_save: dict[tuple[int, int], ConditionOfSale] = {}
    # Create conditions of sale for all ownerships to new apartments this owner has,
    # and all the additional ownerships given (if they are for new apartments).
    # Don't create conditions of sale to unregulated housing companies.
    for ownership in ownerships:
        apartment = ownership.apartment
        if apartment.housing_company.regulation_status != RegulationStatus.REGULATED or not apartment.is_new:
            continue

        for other_ownership in ownerships:
            if (
                other_ownership.apartment.housing_company.regulation_status != RegulationStatus.REGULATED
                # Don't create circular conditions of sale
                or ownership.id == other_ownership.id
            ):
                continue

            # Only one condition of sale between two new apartments
            key: tuple[int, int] = tuple(sorted([ownership.id, other_ownership.id]))  # type: ignore
            if key in to_save:
                continue

            to_save[key] = ConditionOfSale(new_ownership=ownership, old_ownership=other_ownership)

    return list(to_save.values())


def fulfill_conditions_of_sales_for_housing_companies(housing_companies: list[int]) -> None:
    ConditionOfSale.objects.filter(
        (
            Q(new_ownership__sale__apartment__building__real_estate__housing_company__id__in=housing_companies)
            | Q(old_ownership__sale__apartment__building__real_estate__housing_company__id__in=housing_companies)
        ),
    ).delete()
