import datetime

from django.db import models

from hitas.models._base import HitasModel


class MigrationDone(HitasModel):
    when: datetime.datetime = models.DateTimeField(auto_now=True)
