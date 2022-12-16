from django.db import models
from django.utils.translation import gettext_lazy as _

from hitas.models._base import ExternalHitasModel
from hitas.models.utils import check_business_id, check_social_security_number


class Owner(ExternalHitasModel):
    name = models.CharField(max_length=256, blank=True, null=True)
    identifier = models.CharField(max_length=11, blank=True, null=True)
    valid_identifier = models.BooleanField(default=False)
    email = models.EmailField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.valid_identifier = check_social_security_number(self.identifier) or check_business_id(self.identifier)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Owner")
        verbose_name_plural = _("Owners")
        ordering = ["id"]

    def __str__(self):
        return self.name
