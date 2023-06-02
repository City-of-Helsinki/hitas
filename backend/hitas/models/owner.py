from typing import Any, Optional, TypedDict

from auditlog.registry import auditlog
from django.db import models
from django.utils.functional import classproperty
from django.utils.translation import gettext_lazy as _

from hitas.models._base import ExternalSafeDeleteHitasModel
from hitas.models.utils import check_business_id, check_social_security_number, lift_obfuscation, obfuscate
from hitas.utils import index_of


class OwnerT(TypedDict):
    name: Optional[str]
    identifier: Optional[str]
    email: Optional[str]


class Owner(ExternalSafeDeleteHitasModel):
    name: str = models.CharField(max_length=256, blank=True)
    identifier: Optional[str] = models.CharField(max_length=11, blank=True, null=True)
    valid_identifier: bool = models.BooleanField(default=False)
    email: Optional[str] = models.EmailField(blank=True, null=True)
    bypass_conditions_of_sale: bool = models.BooleanField(default=False)
    non_disclosure: bool = models.BooleanField(default=False)

    @classproperty
    def obfuscation_rules(cls) -> dict[str, Any]:
        return {"name": "", "identifier": None, "email": None}

    @property
    def should_obfuscate(self) -> bool:
        return self.non_disclosure

    @lift_obfuscation
    def save(self, *args, **kwargs) -> None:
        self.valid_identifier = check_social_security_number(self.identifier) or check_business_id(self.identifier)
        super().save(*args, **kwargs)

    @classmethod
    def post_fetch_hook(cls, model: "Owner") -> "Owner":
        obfuscate(model)
        return model

    @classmethod
    def post_fetch_values_hook(cls, values: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
        if "non_disclosure" not in values:
            raise RuntimeError(
                f"Due to owner obfuscation, 'non_disclosure' field should always be included "
                f"when fetching owners. Field not found in fields: {fields}"
            )
        # If non_disclosure is not given, we assume the owner needs to be obfuscated
        if values["non_disclosure"] is True:
            for field, value in cls.obfuscation_rules.items():
                if field in values:
                    values[field] = value
        return values

    @classmethod
    def post_fetch_values_list_hook(cls, values: tuple[Any, ...], fields: tuple[str, ...]) -> tuple[Any, ...]:
        index_nd = index_of(fields, "non_disclosure")
        if index_nd is None:
            raise RuntimeError(
                f"Due to owner obfuscation, 'non_disclosure' field should always be included "
                f"when fetching owners. Field not found in fields: {fields}"
            )
        if values[index_nd] is True:
            for field, value in cls.obfuscation_rules.items():
                field_index = index_of(fields, field)
                if field_index is not None:
                    values = (*values[:field_index], value, *values[field_index + 1 :])
        return values

    @classmethod
    def post_fetch_values_list_flat_hook(cls, value: Any, field: str) -> None:
        # Primary keys must be allowed so that 'bulk_create' works
        if field == "pk":
            return value

        raise RuntimeError(
            "Due to owner obfuscation, 'non_disclosure' field should always be included "
            "when fetching owners. When using .values_list(..., flat=True), this cannot be done."
            "Please use some other way to fetch this value."
        )

    class Meta:
        verbose_name = _("Owner")
        verbose_name_plural = _("Owners")
        ordering = ["id"]

    def __str__(self):
        return str(self.name)

    def __repr__(self) -> str:
        return f"<{type(self).__name__}:{self.pk} ({str(self)})>"


auditlog.register(Owner)
