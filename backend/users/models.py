import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from helusers.models import AbstractUser


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=50, null=True, blank=True, default=None)
    title = models.CharField(max_length=50, null=True, blank=True, default=None)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}" or self.email

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} ({self.pk}): {self.get_username()}>"

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
