import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
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


class HitasModelDecimalField(models.DecimalField):
    def __init__(self, max_digits=15, decimal_places=2, validators=None, **kwargs):
        if validators is None:
            validators = [MinValueValidator(Decimal("0"))]
        super().__init__(max_digits=max_digits, decimal_places=decimal_places, validators=validators, **kwargs)
