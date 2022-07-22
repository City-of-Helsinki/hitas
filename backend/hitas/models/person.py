from django.db import models
from django.utils.translation import gettext_lazy as _

from hitas.models._base import ExternalHitasModel


class Person(ExternalHitasModel):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    # 'Henkilötunnus'
    social_security_number = models.CharField(max_length=128, blank=True, null=True)

    email = models.EmailField(blank=True, null=True)
    street_address = models.CharField(max_length=128)
    postal_code = models.ForeignKey("PostalCode", on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")
        ordering = ["id"]

    def __str__(self):
        return f"{self.last_name}, {self.first_name} ({self.social_security_number})"
