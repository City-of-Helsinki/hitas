from auditlog.registry import auditlog
from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete import SOFT_DELETE_CASCADE

from hitas.models._base import ExternalHitasModel
from hitas.models.postal_code import HitasPostalCode
from hitas.models.utils import validate_building_id


# Rakennus
class Building(ExternalHitasModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    real_estate = models.ForeignKey("RealEstate", on_delete=models.PROTECT, related_name="buildings")

    street_address = models.CharField(max_length=1024)

    # 'rakennustunnus'
    building_identifier = models.CharField(
        blank=True,
        null=True,
        max_length=25,
        validators=[validate_building_id],
        help_text=_("Format: 100012345A or 91-17-16-1 S 001"),
    )

    @property
    def postal_code(self) -> HitasPostalCode:
        return self.real_estate.postal_code

    @property
    def city(self) -> str:
        return self.postal_code.city

    class Meta:
        verbose_name = _("Building")
        verbose_name_plural = _("Buildings")
        ordering = ["id"]

    def __str__(self):
        return str(self.street_address)


auditlog.register(Building)
