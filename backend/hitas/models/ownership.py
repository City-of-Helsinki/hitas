import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Iterable, Optional, TypedDict, Union

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from hitas.models._base import ExternalHitasModel, HitasModelDecimalField

if TYPE_CHECKING:
    from hitas.models import Owner


# 'Omistajuus'
class Ownership(ExternalHitasModel):
    apartment = models.ForeignKey(
        "Apartment",
        on_delete=models.CASCADE,
        related_name="ownerships",
        editable=False,
    )
    owner = models.ForeignKey(
        "Owner",
        on_delete=models.PROTECT,
        related_name="ownerships",
        editable=False,
    )
    sale = models.ForeignKey(
        "ApartmentSale",
        on_delete=models.SET_NULL,
        related_name="ownerships",
        default=None,
        null=True,
    )

    percentage = HitasModelDecimalField(
        validators=[
            MinValueValidator(Decimal("0")),
            MaxValueValidator(Decimal("100")),
        ],
        editable=False,
    )
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = _("Ownership")
        verbose_name_plural = _("Ownerships")
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_single_ownership_for_apartment_per_owner",
                fields=("apartment", "owner"),
                condition=models.Q(deleted__isnull=True),
            )
        ]

    def __str__(self):
        return f"{self.owner}, {self.apartment}"


class _OwnershipLike(TypedDict, total=False):
    start_date: Optional[datetime.date]
    end_date: Optional[datetime.date]


class OwnershipLike(_OwnershipLike):
    percentage: Decimal
    owner: "Owner"


def check_ownership_percentages(ownerships: Iterable[Union[Ownership, OwnershipLike]]) -> None:
    percentage_sum = 0
    for ownership in ownerships:
        percentage = ownership.percentage if isinstance(ownership, Ownership) else ownership["percentage"]
        percentage_sum += percentage
        if not 0 < percentage <= 100:
            raise ValidationError(
                {
                    "percentage": (
                        f"Ownership percentage must be greater than 0 and less than or equal to 100. "
                        f"Given value was {percentage}."
                    )
                },
            )

    if percentage_sum != 100:
        raise ValidationError(
            {
                "percentage": (
                    f"Ownership percentage of all ownerships combined must be equal to 100. "
                    f"Given sum was {percentage_sum}."
                )
            }
        )
