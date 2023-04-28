from auditlog.registry import auditlog
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from hitas.models._base import ExternalHitasModel


# Postinumero
class HitasPostalCode(ExternalHitasModel):
    value = models.CharField(max_length=5, unique=True)
    city = models.CharField(max_length=1024, default="Helsinki")
    cost_area = models.PositiveIntegerField(validators=[MaxValueValidator(4), MinValueValidator(1)])

    class Meta:
        verbose_name = _("Postal code")
        verbose_name_plural = _("Postal codes")

    def __str__(self):
        return self.value

    def __repr__(self) -> str:
        return f"<{type(self).__name__}:{self.pk}:{self.value}>"


auditlog.register(HitasPostalCode)
