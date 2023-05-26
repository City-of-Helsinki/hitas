import datetime
from decimal import Decimal
from typing import Any, Iterable, Optional, TypeAlias, TypedDict, TypeVar
from uuid import UUID, uuid4

from auditlog.diff import model_instance_diff
from auditlog.models import LogEntry
from auditlog.receivers import log_delete, log_update
from auditlog.registry import auditlog
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Model, QuerySet
from django.db.models.functions import Cast
from django.db.models.manager import BaseManager
from django.utils.functional import classproperty
from post_fetch_hook import mixins
from safedelete.managers import SafeDeleteAllManager, SafeDeleteDeletedManager, SafeDeleteManager
from safedelete.models import SafeDeleteModel
from safedelete.queryset import SafeDeleteQueryset
from safedelete.signals import post_softdelete, post_undelete

from hitas.services.audit_log import bulk_create_log_entries

PK: TypeAlias = int
FieldName: TypeAlias = str
OldValue: TypeAlias = str
NewValue: TypeAlias = str
TModel = TypeVar("TModel", bound=Model)

# Create audit logs when soft-delete models are soft-deleted or undeleted
auditlog._signals[post_softdelete] = log_delete
auditlog._signals[post_undelete] = log_update


class AuditableUpdateMixin:
    def update(self, **kwargs: Any) -> int:  # NOSONAR
        if self.model not in auditlog.get_models():
            return super().update(**kwargs)

        objs: dict[int, Model] = {obj.pk: obj for obj in self.all()}

        # Convert Cast-ed Case-statements from 'bulk_update' to plain values.
        # 'bulk_update' calls this method with 'kwargs' like this:
        #
        # {
        #   "field_1": Cast(
        #     Case(
        #       When(pk=1, then=Value(1)),
        #       When(pk=2, then=Value(2)),
        #       default=None,
        #     ),
        #     output_field=IntegerField(),
        #   ),
        #   "field_2": Cast(
        #     Case(
        #       When(pk=1, then=Value("foo")),
        #       When(pk=2, then=Value("bar")),
        #       default=None,
        #     ),
        #     output_field=CharField(),
        #   ),
        # }
        #
        # This needs to be converted to 'changes' like this:
        #
        # {
        #   1: {"field_1": (objs[1].field_1, 1), "field_2": (objs[1].field_2, "foo")},
        #   2: {"field_1": (objs[2].field_1, 2), "field_2": (objs[2].field_2, "bar")},
        # }
        #
        if any(isinstance(value, Cast) for value in kwargs.values()):
            changes: dict[PK, dict[FieldName, tuple[OldValue, NewValue]]] = {}
            for key, value in kwargs.items():
                for expression in value.source_expressions:
                    for case in expression.cases:
                        next_val = case.result.value
                        for _, pk in case.condition.children:
                            current_val = getattr(objs[pk], key, None)
                            if current_val != next_val:
                                changes.setdefault(pk, {})
                                changes[pk].update({key: (str(current_val), str(next_val))})
        else:
            changes: dict[PK, dict[FieldName, tuple[OldValue, NewValue]]] = {
                pk: {key: (str(getattr(objs[pk], key, None)), str(value)) for key, value in kwargs.items()}
                for pk in objs
            }

        if not changes:
            return 0

        with transaction.atomic():
            ret = super().update(**kwargs)
            bulk_create_log_entries(objs.values(), LogEntry.Action.UPDATE, changes)

        return ret


class AuditableBulkCreateMixin:
    def bulk_create(
        self,
        objs: Iterable[TModel],
        batch_size: Optional[int] = None,
        ignore_conflicts: bool = False,
    ) -> list[TModel]:
        if self.model not in auditlog.get_models():
            return super().bulk_create(objs, batch_size, ignore_conflicts)

        with transaction.atomic():
            # Need to fetch the existing IDs before 'bulk_create',
            # because it does not return the IDs in the created objects
            existing_ids: list[int] = list(self.values_list("pk", flat=True))
            objs = super().bulk_create(objs, batch_size, ignore_conflicts)
            new_objs: list[TModel] = list(self.exclude(id__in=existing_ids))

            changes: dict[PK, dict[FieldName, tuple[OldValue, NewValue]]]
            changes = {obj.pk: model_instance_diff(None, obj) for obj in new_objs}
            bulk_create_log_entries(new_objs, LogEntry.Action.CREATE, changes)

        return objs


class HitasQuerySet(
    AuditableUpdateMixin,
    AuditableBulkCreateMixin,
    # Model send signals to auditlog, so queryset "fast deletes" are not possible.
    # See `django.db.models.deletion.Collector.can_fast_delete`.
    # Therefore, log entries are created with the model's delete,
    # and we don't need to override queryset's delete() method.
    mixins.PostFetchQuerySetMixin,
    QuerySet,
):
    pass


class HitasManager(BaseManager.from_queryset(HitasQuerySet)):
    pass


class PostFetchModelMixin(mixins.PostFetchModelMixin):
    @classproperty
    def obfuscation_rules(cls) -> dict[str, Any]:
        """Which fields to obfuscate and with what values."""
        return NotImplemented

    @property
    def should_obfuscate(self) -> bool:
        """Whether the model should be obfuscated or not."""
        return NotImplemented


class AuditLogAdditionalDataT(TypedDict):
    is_sent: bool


class AuditLogAdditionalDataMixin:
    @staticmethod
    def get_additional_data() -> AuditLogAdditionalDataT:
        """Get additional data to be saved with the log entry."""
        return AuditLogAdditionalDataT(
            is_sent=False,
        )


class HitasModel(PostFetchModelMixin, AuditLogAdditionalDataMixin, Model):
    """
    Model with bulk auditing capabilities.
    """

    objects = HitasManager()

    class Meta:
        abstract = True
        # Django knows to use our custom QuerySet
        # for related managers based on this setting.
        base_manager_name = "objects"

    def __repr__(self) -> str:
        return f"<{type(self).__name__}:{self.pk}>"


class HitasSafeDeleteQuerySet(
    AuditableUpdateMixin,
    AuditableBulkCreateMixin,
    mixins.PostFetchQuerySetMixin,
    # SafeDelete models override queryset's delete() method
    # so that the model's delete() is called for each object.
    # Therefore, log entries are created with the model's delete,
    # and we don't need to override queryset's delete() method.
    SafeDeleteQueryset,
):
    pass


class HitasSafeDeleteManager(SafeDeleteManager):
    _queryset_class = HitasSafeDeleteQuerySet


class HitasSafeDeleteAllManager(SafeDeleteAllManager):
    _queryset_class = HitasSafeDeleteQuerySet


class HitasSafeDeleteDeletedManager(SafeDeleteDeletedManager):
    _queryset_class = HitasSafeDeleteQuerySet


class HitasSafeDeleteModel(PostFetchModelMixin, AuditLogAdditionalDataMixin, SafeDeleteModel):
    """
    Abstract model for Hitas entities without an externally visible ID
    """

    objects = HitasSafeDeleteManager()
    all_objects = HitasSafeDeleteAllManager()
    deleted_objects = HitasSafeDeleteDeletedManager()

    class Meta:
        abstract = True
        # Django knows to use our custom QuerySet
        # for related managers based on this setting.
        # Base manager needs to be the all_object manager
        # so that safe-delete is able to do its magic.
        base_manager_name = "all_objects"

    def __repr__(self) -> str:
        return f"<{type(self).__name__}:{self.pk}>"


class ExternalSafeDeleteHitasModel(HitasSafeDeleteModel):
    """
    Abstract model for Hitas entities with an externally visible ID in UUID format
    """

    uuid: UUID = models.UUIDField(default=uuid4, editable=False, unique=True)

    class Meta:
        abstract = True


class HitasModelDecimalField(models.DecimalField):
    def __init__(self, max_digits=15, decimal_places=2, validators=None, **kwargs):
        if validators is None:
            validators = [MinValueValidator(Decimal("0"))]
        super().__init__(max_digits=max_digits, decimal_places=decimal_places, validators=validators, **kwargs)


class HitasImprovement(HitasSafeDeleteModel):
    name: str = models.CharField(max_length=128)
    completion_date: datetime.date = models.DateField()
    value: Decimal = HitasModelDecimalField(validators=[MinValueValidator(0)])

    class Meta:
        abstract = True
        ordering = ["completion_date", "id"]

    def __str__(self):
        return f"{self.name} ({self.value} €)"


class HitasMarketPriceImprovement(HitasImprovement):
    # No deductions = Excess is not removed from this apartment, and the improvement does not deprecate
    # This means that the full value of the improvement is always added to the price of the apartment
    # This is used e.g. for an attic room, elevators or repair costs of construction defects
    # These improvements values are also index adjusted.
    no_deductions: bool = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = HitasImprovement.Meta.ordering
