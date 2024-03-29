from typing import Optional

from auditlog.registry import auditlog
from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete import SOFT_DELETE_CASCADE

from hitas.models import HitasPostalCode
from hitas.models._base import ExternalSafeDeleteHitasModel
from hitas.models.utils import validate_property_id


# Kiinteistö
class RealEstate(ExternalSafeDeleteHitasModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    # 'Taloyhtiö'
    housing_company = models.ForeignKey("HousingCompany", on_delete=models.PROTECT, related_name="real_estates")

    # 'Kiinteistötunnus'
    property_identifier: Optional[str] = models.CharField(
        max_length=19,
        null=True,
        validators=[validate_property_id],
        help_text=_("Format: 1234-1234-1234-1234"),
    )

    @property
    def street_address(self) -> str:
        return self.housing_company.street_address

    @property
    def postal_code(self) -> HitasPostalCode:
        return self.housing_company.postal_code

    @property
    def city(self) -> str:
        return self.postal_code.city

    class Meta:
        verbose_name = _("Real estate")
        verbose_name_plural = _("Real estates")
        ordering = ["id"]

    def __str__(self):
        return str(self.property_identifier)


auditlog.register(RealEstate)
