from auditlog.registry import auditlog
from django.db import models
from django.utils.translation import gettext_lazy as _

from hitas.models._base import ExternalSafeDeleteHitasModel


# Isännöitsijä
class PropertyManager(ExternalSafeDeleteHitasModel):
    name: str = models.CharField(max_length=1024)
    email: str = models.EmailField()
    street_address: str = models.CharField(max_length=1024)
    postal_code: str = models.CharField(max_length=5)
    city: str = models.CharField(max_length=1024)

    class Meta:
        verbose_name = _("Property manager")
        verbose_name_plural = _("Property managers")
        ordering = ["id"]

    def __str__(self):
        return self.name


auditlog.register(PropertyManager)
