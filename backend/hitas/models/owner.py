from typing import Optional, TypedDict

from auditlog.registry import auditlog
from django.db import models
from django.utils.translation import gettext_lazy as _

from hitas.models._base import ExternalSafeDeleteHitasModel
from hitas.models.utils import check_business_id, check_social_security_number


class OwnerT(TypedDict):
    name: Optional[str]
    identifier: Optional[str]
    email: Optional[str]


class Owner(ExternalSafeDeleteHitasModel):
    name = models.CharField(max_length=256, blank=True, null=True)
    identifier = models.CharField(max_length=11, blank=True, null=True)
    valid_identifier = models.BooleanField(default=False)
    email = models.EmailField(blank=True, null=True)
    bypass_conditions_of_sale = models.BooleanField(default=False)
    non_disclosure = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.valid_identifier = check_social_security_number(self.identifier) or check_business_id(self.identifier)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Owner")
        verbose_name_plural = _("Owners")
        ordering = ["id"]

    def __str__(self):
        return str(self.name)

    def __repr__(self) -> str:
        return f"<{type(self).__name__}:{self.pk} ({str(self)})>"


auditlog.register(Owner)
