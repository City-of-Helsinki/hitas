from django.db import models
from django.db.models import Count, OuterRef, QuerySet
from django.db.models.functions import Coalesce

from hitas.models.housing_company import RegulationStatus
from hitas.models.owner import Owner, OwnerT
from hitas.models.ownership import Ownership
from hitas.utils import SQSum


def obfuscate_owners_without_regulated_apartments() -> list[OwnerT]:
    """Remove any personal information from owners which do not own any regulated hitas apartments."""
    owners: QuerySet[Owner] = Owner.objects.annotate(
        owned_regulated_housing_companies=Coalesce(
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
        )
    ).filter(owned_regulated_housing_companies=0)

    obfuscated_owners: list[OwnerT] = list(owners.values("name", "identifier", "email"))

    if obfuscated_owners:
        owners.update(
            name=None,
            identifier=None,
            valid_identifier=False,
            email=None,
            bypass_conditions_of_sale=True,
        )

    return obfuscated_owners


def log_access_if_owner_has_non_disclosure(owner: Owner) -> None:
    """Log access to owner info if they have a non-disclosure agreement."""
    # TODO: This will be implemented later.
    #  if owner.non_disclosure:
    #      accessed.send(owner.__class__, instance=owner)
