import uuid

from django.db import models


class HitasModel(models.Model):
    """
    Abstract model for Hitas entities without an externally visible ID
    """

    class Meta:
        abstract = True

    def __repr__(self) -> str:
        return f"<{type(self).__name__}:{self.pk}>"


class ExternalHitasModel(models.Model):
    """
    Abstract model for Hitas entities with an externally visible ID in UUID format
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True

    def __repr__(self) -> str:
        return f"<{type(self).__name__}:{self.pk}:{self.uuid}>"
