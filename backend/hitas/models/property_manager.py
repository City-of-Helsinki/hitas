from django.db import models
from django.utils.translation import gettext_lazy as _

from hitas.models._base import HitasModel
from hitas.models.areas import hitas_city
from hitas.models.codes import PostalCode


# Isännöitsijä
class PropertyManager(HitasModel):
    name = models.CharField(max_length=1024)
    email = models.EmailField()
    street_address = models.CharField(max_length=1024)
    postal_code = models.ForeignKey(PostalCode, on_delete=models.PROTECT)

    @property
    def city(self):
        return hitas_city(self.postal_code.value)

    class Meta:
        verbose_name = _("Property manager")
        verbose_name_plural = _("Property managers")

    def __str__(self):
        return self.name
