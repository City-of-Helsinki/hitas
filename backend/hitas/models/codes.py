from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hitas.models._base import ExternalHitasModel


class AbstractCode(ExternalHitasModel):
    value = models.CharField(max_length=1024)
    description = models.TextField(blank=True)

    in_use = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(null=True, blank=True)
    legacy_code_number = models.CharField(null=True, max_length=12)
    legacy_start_date = models.DateTimeField(default=timezone.now)
    legacy_end_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ["order", "id"]

    def __str__(self):
        return self.value

    def __repr__(self) -> str:
        return f"<{type(self).__name__}:{self.pk}:{self.value}>"


# Talotyyppi
class BuildingType(AbstractCode):
    class Meta(AbstractCode.Meta):
        verbose_name = _("Building type")
        verbose_name_plural = _("Building types")


# Rahoitusmuoto
class FinancingMethod(AbstractCode):
    class Meta(AbstractCode.Meta):
        verbose_name = _("Financing method")
        verbose_name_plural = _("Financing methods")


# Rakennuttaja
class Developer(AbstractCode):
    class Meta(AbstractCode.Meta):
        verbose_name = _("Developer")
        verbose_name_plural = _("Developers")


# Huoneistotyyppi
class ApartmentType(AbstractCode):
    class Meta(AbstractCode.Meta):
        verbose_name = _("Apartment type")
        verbose_name_plural = _("Apartment types")
