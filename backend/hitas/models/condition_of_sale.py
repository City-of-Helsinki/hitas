import datetime
from typing import Optional

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from enumfields import Enum, EnumField

from hitas.models._base import ExternalHitasModel


class GracePeriod(Enum):
    NOT_GIVEN = "not_given"
    THREE_MONTHS = "three_months"
    SIX_MONTHS = "six_months"

    class Labels:
        NOT_GIVEN = _("Not given")
        THREE_MONTHS = _("Three months")
        SIX_MONTHS = _("Six months")


# 'Myyntiehto'
class ConditionOfSale(ExternalHitasModel):
    new_ownership = models.ForeignKey(
        "Ownership",
        related_name="conditions_of_sale_new",
        on_delete=models.CASCADE,
        editable=False,
    )
    old_ownership = models.ForeignKey(
        "Ownership",
        related_name="conditions_of_sale_old",
        on_delete=models.CASCADE,
        editable=False,
    )
    grace_period = EnumField(GracePeriod, default=GracePeriod.NOT_GIVEN, max_length=12)

    class Meta:
        verbose_name = _("Condition of Sale")
        verbose_name_plural = _("Conditions of Sale")
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_no_circular_reference",
                check=~models.Q(new_ownership=models.F("old_ownership")),
            ),
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_only_one_valid_condition_of_sale",
                fields=("new_ownership", "old_ownership"),
                condition=models.Q(deleted__isnull=True),
            ),
        ]

    @property
    def fulfilled(self) -> Optional[datetime.datetime]:
        return self.deleted  # noqa

    def __str__(self) -> str:
        return (
            f"{self.old_ownership.owner}: {self.old_ownership.apartment} "
            f"-> {self.new_ownership.owner}: {self.new_ownership.apartment}"
        )


def condition_of_sale_queryset() -> models.QuerySet[ConditionOfSale]:
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
            # New stuff
            "new_ownership__apartment__building",
            "old_ownership__apartment__building",
            "new_ownership__apartment__building__real_estate",
            "old_ownership__apartment__building__real_estate",
            "new_ownership__apartment__building__real_estate__housing_company",
            "old_ownership__apartment__building__real_estate__housing_company",
            "new_ownership__apartment__building__real_estate__housing_company__postal_code",
            "old_ownership__apartment__building__real_estate__housing_company__postal_code",
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
