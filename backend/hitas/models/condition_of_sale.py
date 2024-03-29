import datetime
from typing import Optional

from auditlog.registry import auditlog
from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils.translation import gettext_lazy as _
from enumfields import Enum, EnumField

from hitas.models._base import ExternalSafeDeleteHitasModel


class GracePeriod(Enum):
    NOT_GIVEN = "not_given"
    THREE_MONTHS = "three_months"
    SIX_MONTHS = "six_months"

    class Labels:
        NOT_GIVEN = _("Not given")
        THREE_MONTHS = _("Three months")
        SIX_MONTHS = _("Six months")


# 'Myyntiehto'
class ConditionOfSale(ExternalSafeDeleteHitasModel):
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
    grace_period: GracePeriod = EnumField(GracePeriod, default=GracePeriod.NOT_GIVEN, max_length=12)

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

    @property
    def sell_by_date(self) -> Optional[datetime.date]:
        if self.fulfilled:
            return None

        # If the apartment has not been completed, there is no sell by date yet.
        sell_by_date = self.new_ownership.apartment.completion_date
        if sell_by_date is None:
            return None

        # If apartment was sold after it was completed, the sell by date is calculated based on first sale date.
        if hasattr(self, "first_purchase_date"):
            first_purchase_date = self.first_purchase_date
        else:
            from hitas.services.apartment import get_first_sale_purchase_date

            first_purchase_date = get_first_sale_purchase_date(self.new_ownership.apartment.id)

        if first_purchase_date is not None and first_purchase_date > sell_by_date:
            sell_by_date = first_purchase_date

        # If grace period has been given, it should be included
        if self.grace_period == GracePeriod.THREE_MONTHS:
            sell_by_date += relativedelta(months=3)
        elif self.grace_period == GracePeriod.SIX_MONTHS:
            sell_by_date += relativedelta(months=6)

        return sell_by_date

    def __str__(self) -> str:
        return (
            f"{self.old_ownership.owner}: {self.old_ownership.apartment} "
            f"-> {self.new_ownership.owner}: {self.new_ownership.apartment}"
        )


# this is only for typing
class ConditionOfSaleAnnotated(ConditionOfSale):
    first_purchase_date: Optional[datetime.date]

    class Meta:
        abstract = True


auditlog.register(ConditionOfSale)
