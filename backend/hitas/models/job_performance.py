from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from enumfields import Enum, EnumField

from hitas.models._base import HitasModel


class JobPerformanceSource(Enum):
    CONFIRMED_MAX_PRICE = "confirmed_max_price"
    UNCONFIRMED_MAX_PRICE = "unconfirmed_max_price"


# 'Suorite'
class JobPerformance(HitasModel):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_performances",
        editable=False,
    )
    source = EnumField(JobPerformanceSource, max_length=21)
    request_date = models.DateField(editable=False)
    delivery_date = models.DateField(editable=False)

    class Meta:
        verbose_name = _("Job performance")
        verbose_name_plural = _("Job performances")

    def __str__(self) -> str:
        return f"Job performance of {self.user} ({self.request_date.isoformat()} -> {self.delivery_date.isoformat()})"
