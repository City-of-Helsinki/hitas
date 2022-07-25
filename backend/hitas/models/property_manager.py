from django.db import models
from django.utils.translation import gettext_lazy as _

from hitas.models._base import ExternalHitasModel
from hitas.models.codes import PostalCode
from hitas.models.utils import hitas_city


# Isännöitsijä
class PropertyManager(ExternalHitasModel):
    name = models.CharField(max_length=1024)
    email = models.EmailField()
    street_address = models.CharField(max_length=1024)
    postal_code = models.ForeignKey(PostalCode, on_delete=models.PROTECT, related_name="property_managers")

    @property
    def city(self):
        return hitas_city(self.postal_code.value)

    class Meta:
        verbose_name = _("Property manager")
        verbose_name_plural = _("Property managers")
        ordering = ["id"]

    def __str__(self):
        return self.name
