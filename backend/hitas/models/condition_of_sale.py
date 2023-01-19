from django.core.exceptions import ValidationError
from django.db import models
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

    def save(self, keep_deleted=False, **kwargs) -> None:
        self.clean()
        super().save(keep_deleted=keep_deleted, **kwargs)

    def clean(self) -> None:
        if self.new_ownership.owner != self.old_ownership.owner:
            raise ValidationError("Owners must be the same.")

    def __str__(self) -> str:
        return f"{self.new_ownership.owner}: {self.new_ownership.apartment} -> {self.old_ownership.apartment}"
