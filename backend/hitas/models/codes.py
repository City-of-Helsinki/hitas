import datetime
from typing import Optional

from auditlog.registry import auditlog
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hitas.models._base import ExternalSafeDeleteHitasModel


class AbstractCode(ExternalSafeDeleteHitasModel):
    value: str = models.CharField(max_length=1024)
    description: str = models.TextField(blank=True)

    in_use: bool = models.BooleanField(default=True)
    order: Optional[int] = models.PositiveSmallIntegerField(null=True, blank=True)
    legacy_code_number: Optional[str] = models.CharField(null=True, max_length=12)
    legacy_start_date: datetime.datetime = models.DateTimeField(default=timezone.now)
    legacy_end_date: Optional[datetime.datetime] = models.DateTimeField(null=True, blank=True)

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


auditlog.register(BuildingType)
auditlog.register(Developer)
auditlog.register(ApartmentType)
