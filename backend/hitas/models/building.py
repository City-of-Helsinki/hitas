from django.db import models
from django.utils.translation import gettext_lazy as _

from hitas.models._base import ExternalHitasModel
from hitas.models.utils import validate_building_id


# Rakennus
class Building(ExternalHitasModel):
    real_estate = models.ForeignKey("RealEstate", on_delete=models.PROTECT, related_name="buildings")

    street_address = models.CharField(max_length=1024)
    postal_code = models.ForeignKey("HitasPostalCode", on_delete=models.PROTECT, related_name="buildings")

    # 'rakennustunnus'
    building_identifier = models.CharField(
        blank=True,
        null=True,
        max_length=25,
        validators=[validate_building_id],
        help_text=_("Format: 100012345A or 91-17-16-1 S 001"),
    )

    @property
    def city(self):
        return self.postal_code.city

    class Meta:
        verbose_name = _("Building")
        verbose_name_plural = _("Buildings")
        ordering = ["id"]

    def __str__(self):
        return self.street_address
