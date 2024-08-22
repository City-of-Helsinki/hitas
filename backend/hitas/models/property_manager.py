import datetime
from typing import Optional

from auditlog.models import LogEntry
from auditlog.registry import auditlog
from django.db import models
from django.utils.translation import gettext_lazy as _

from hitas.models._base import ExternalSafeDeleteHitasModel


# Isännöitsijä
class PropertyManager(ExternalSafeDeleteHitasModel):
    name: str = models.CharField(max_length=1024)
    email: str = models.EmailField(blank=True)

    class Meta:
        verbose_name = _("Property manager")
        verbose_name_plural = _("Property managers")
        ordering = ["id"]

    @property
    def modified_at(self) -> Optional[datetime.datetime]:
        latest_logentry: LogEntry = (
            LogEntry.objects.get_for_object(self)
            .filter(action__in=[LogEntry.Action.UPDATE, LogEntry.Action.CREATE])
            .order_by("-timestamp", "-id")
            .first()
        )
        if latest_logentry is not None:
            return latest_logentry.timestamp
        return None

    def __str__(self):
        return self.name


auditlog.register(PropertyManager)
