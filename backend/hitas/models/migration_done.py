from django.db import models


class MigrationDone(models.Model):
    when = models.DateTimeField(auto_now=True)
