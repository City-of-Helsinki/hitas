from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from hitas.models._base import HitasModel, HitasModelDecimalField


class Owner(HitasModel):
    apartment = models.ForeignKey("Apartment", on_delete=models.PROTECT, related_name="owners")
    person = models.ForeignKey("Person", on_delete=models.PROTECT, related_name="owners")

    ownership_percentage = HitasModelDecimalField(
        validators=[
            MinValueValidator(Decimal("0")),
            MaxValueValidator(Decimal("100")),
        ]
    )
    ownership_start_date = models.DateField(blank=True, null=True)
    ownership_end_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = _("Owner")
        verbose_name_plural = _("Owners")
        ordering = ["id"]

    def __str__(self):
        return f"{self.person}, {self.apartment}"
