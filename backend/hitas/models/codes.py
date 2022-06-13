import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hitas.models._base import HitasModel


def validate_code_number(value: str) -> None:
    # Example valid value: '012'
    match = re.search(r"^\d{3}$", value)

    if match is None:
        raise ValidationError(
            _("%(value)s is not an valid code number"),
            params={"value": value},
        )


class AbstractCode(HitasModel):
    value = models.CharField(max_length=1024)
    description = models.TextField(blank=True)

    in_use = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(null=True, blank=True)
    legacy_code_number = models.CharField(
        max_length=3, unique=True, validators=[validate_code_number], help_text=_("Format: 000")
    )
    legacy_start_date = models.DateTimeField(default=timezone.now)
    legacy_end_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ["order"]

    def __str__(self):
        return self.value


# Talotyyppi
class BuildingType(AbstractCode):
    class Meta(AbstractCode.Meta):
        verbose_name = _("Building type")
        verbose_name_plural = _("Building types")


# Rahoitusmuoto
class FinancingMethod(AbstractCode):
    class Meta(AbstractCode.Meta):
        verbose_name = _("Financing methods")
        verbose_name_plural = _("Financing methods")


class PostalCode(AbstractCode):
    class Meta(AbstractCode.Meta):
        verbose_name = _("Postal code")
        verbose_name_plural = _("Postal codes")


# Rakennuttaja
class Developer(AbstractCode):
    class Meta(AbstractCode.Meta):
        verbose_name = _("Developer")
        verbose_name_plural = _("Developers")
