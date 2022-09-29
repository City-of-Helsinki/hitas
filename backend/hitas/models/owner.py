from django.db import models
from django.utils.translation import gettext_lazy as _

from hitas.models._base import ExternalHitasModel


class Owner(ExternalHitasModel):
    name = models.CharField(max_length=256, blank=True, null=True)
    identifier = models.CharField(max_length=11, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        verbose_name = _("Owner")
        verbose_name_plural = _("Owners")
        ordering = ["id"]

    def __str__(self):
        return self.name
