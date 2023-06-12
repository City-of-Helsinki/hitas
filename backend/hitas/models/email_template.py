from django.db import models
from enumfields import Enum, EnumField

from hitas.models._base import HitasModel


class EmailTemplateName(Enum):
    CONFIRMED_MAX_PRICE_CALCULATION = "confirmed_max_price_calculation"
    UNCONFIRMED_MAX_PRICE_CALCULATION = "unconfirmed_max_price_calculation"

    class Labels:
        CONFIRMED_MAX_PRICE_CALCULATION = "Enimmäishintalaskelma"
        UNCONFIRMED_MAX_PRICE_CALCULATION = "Hinta-arvio"


class EmailTemplate(HitasModel):
    name: EmailTemplateName = EnumField(EmailTemplateName, max_length=33, unique=True)
    text: str = models.TextField(max_length=10_000)

    class Meta:
        verbose_name = "Email template"
        verbose_name_plural = "Email templates"

    def __str__(self) -> str:
        return str(self.name)
