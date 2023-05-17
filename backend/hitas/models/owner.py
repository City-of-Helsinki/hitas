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
    def post_fetch_hook(cls, results, fields):
        for i, owner in enumerate(results):
            # qs.values(...)
            if isinstance(owner, dict):
                # If non_disclosure is not given, we assume the owner needs to be obfuscated
                if "non_disclosure" not in owner or owner["non_disclosure"] is True:
                    for field in cls.obfuscation_rules:
                        if field in owner:
                            owner[field] = None

            # qs.values_list(...)
            elif isinstance(owner, tuple):
                # Fields that were accessed
                index_nd = index_of(fields, "non_disclosure")

                # If non_disclosure is not given, we assume the owner needs to be obfuscated
                if index_nd is None or owner[index_nd] is True:
                    for field in cls.obfuscation_rules:
                        field_index = index_of(fields, field)
                        if field_index is not None:
                            results[i] = (*owner[:field_index], None, *owner[field_index + 1 :])

            # qs.get(...), qs.all(), etc.
            elif isinstance(owner, Owner):
                obfuscate(owner)

            # qs.values_list(..., flat=True)
            else:
                # We cannot know if the owner should be obfuscated or not, so we assume it should be.
                # This should probably not be used, but it's here just in case.
                if fields[0] in cls.obfuscation_rules:
                    results[i] = None

        return results

    class Meta:
        verbose_name = _("Owner")
        verbose_name_plural = _("Owners")
        ordering = ["id"]

    def __str__(self):
        return str(self.name)

    def __repr__(self) -> str:
        return f"<{type(self).__name__}:{self.pk} ({str(self)})>"


auditlog.register(Owner)
