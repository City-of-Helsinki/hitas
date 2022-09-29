from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from hitas.models._base import HitasModel, HitasModelDecimalField


class Ownership(HitasModel):
    apartment = models.ForeignKey("Apartment", on_delete=models.CASCADE, related_name="ownerships")
    owner = models.ForeignKey("Owner", on_delete=models.PROTECT, related_name="ownerships")

    percentage = HitasModelDecimalField(
        validators=[
            MinValueValidator(Decimal("0")),
            MaxValueValidator(Decimal("100")),
        ]
    )
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = _("Ownership")
        verbose_name_plural = _("Ownerships")
        ordering = ["id"]

    def __str__(self):
        return f"{self.owner}, {self.apartment}"
