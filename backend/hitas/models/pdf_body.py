from django.contrib.postgres.fields import ArrayField
from django.db import models
from enumfields import Enum, EnumField

from hitas.models._base import HitasModel


class PDFBodyName(Enum):
    CONFIRMED_MAX_PRICE_CALCULATION = "confirmed_max_price_calculation"
    UNCONFIRMED_MAX_PRICE_CALCULATION = "unconfirmed_max_price_calculation"

    class Labels:
        CONFIRMED_MAX_PRICE_CALCULATION = "Enimmäishintalaskelma"
        UNCONFIRMED_MAX_PRICE_CALCULATION = "Hinta-arvio"


class PDFBody(HitasModel):
    name: PDFBodyName = EnumField(PDFBodyName, max_length=33, unique=True)
    texts: list[str] = ArrayField(base_field=models.TextField(max_length=10_000))

    class Meta:
        verbose_name = "PDF body"
        verbose_name_plural = "PDF bodies"

    def __str__(self) -> str:
        return str(self.name)
