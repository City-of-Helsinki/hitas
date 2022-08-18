from django.db import models
from django.utils.translation import gettext_lazy as _

from hitas.models._base import ExternalHitasModel


# Isännöitsijä
class PropertyManager(ExternalHitasModel):
    name = models.CharField(max_length=1024)
    email = models.EmailField()
    street_address = models.CharField(max_length=1024)
    postal_code = models.CharField(max_length=5)
    city = models.CharField(max_length=1024)

    class Meta:
        verbose_name = _("Property manager")
        verbose_name_plural = _("Property managers")
        ordering = ["id"]

    def __str__(self):
        return self.name
