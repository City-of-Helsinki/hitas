from django.db import models
from django.utils.translation import gettext_lazy as _

from hitas.models._base import ExternalHitasModel


class Person(ExternalHitasModel):
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    social_security_number = models.CharField(max_length=11, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")
        ordering = ["id"]

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"
