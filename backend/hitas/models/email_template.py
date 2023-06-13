from django.db import models
from enumfields import Enum, EnumField

from hitas.models._base import HitasModel


class EmailTemplateType(Enum):
    CONFIRMED_MAX_PRICE_CALCULATION = "confirmed_max_price_calculation"
    UNCONFIRMED_MAX_PRICE_CALCULATION = "unconfirmed_max_price_calculation"

    class Labels:
        CONFIRMED_MAX_PRICE_CALCULATION = "Enimmäishintalaskelma"
        UNCONFIRMED_MAX_PRICE_CALCULATION = "Hinta-arvio"


class EmailTemplate(HitasModel):
    name: str = models.CharField(max_length=256)
    type: EmailTemplateType = EnumField(EmailTemplateType, max_length=33)
    text: str = models.TextField(max_length=10_000)

    class Meta:
        verbose_name = "Email template"
        verbose_name_plural = "Email templates"
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_unique_name_type",
                fields=("name", "type"),
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.type})"
