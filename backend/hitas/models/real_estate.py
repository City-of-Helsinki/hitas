from django.db import models
from django.utils.translation import gettext_lazy as _

from hitas.models._base import ExternalHitasModel
from hitas.models.utils import validate_property_id


# Kiinteistö
class RealEstate(ExternalHitasModel):
    housing_company = models.ForeignKey("HousingCompany", on_delete=models.CASCADE, related_name="real_estates")

    # 'kiinteistötunnus'
    property_identifier = models.CharField(
        max_length=19, validators=[validate_property_id], help_text=_("Format: 1234-1234-1234-1234")
    )

    street_address = models.CharField(max_length=1024)

    @property
    def postal_code(self):
        return self.housing_company.postal_code

    @property
    def city(self):
        return self.postal_code.city

    class Meta:
        verbose_name = _("Real estate")
        verbose_name_plural = _("Real estates")
        ordering = ["id"]

    def __str__(self):
        return self.property_identifier
