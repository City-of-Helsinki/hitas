import uuid
from decimal import Decimal
from typing import Any, Iterable, Optional, TypeAlias, TypeVar

from auditlog.diff import model_instance_diff
from auditlog.models import LogEntry
from auditlog.registry import auditlog
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Model, QuerySet
from django.db.models.functions import Cast
from django.db.models.manager import BaseManager
from safedelete.managers import SafeDeleteAllManager, SafeDeleteDeletedManager, SafeDeleteManager
from safedelete.models import SafeDeleteModel
from safedelete.queryset import SafeDeleteQueryset

from hitas.services.audit_log import bulk_create_log_entries

PK: TypeAlias = int
FieldName: TypeAlias = str
OldValue: TypeAlias = str
NewValue: TypeAlias = str
TModel = TypeVar("TModel", bound=Model)


class AuditableUpdateMixin:
    def update(self, **kwargs: Any) -> int:
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


class AuditableDeleteMixin:
    def delete(self) -> tuple[int, dict[str, int]]:
        if self.model not in auditlog.get_models():
            return super().delete()

        objs: list[Model] = list(self.all())
        changes: dict[PK, dict[FieldName, tuple[OldValue, NewValue]]]
        changes = {obj.pk: model_instance_diff(obj, None) for obj in objs}

        with transaction.atomic():
            ret = super().delete()
            bulk_create_log_entries(objs, LogEntry.Action.DELETE, changes)

        return ret


class AuditableDeleteForceMixin:
    def delete(self, force_policy: Optional[int] = None) -> tuple[int, dict[str, int]]:
        if self.model not in auditlog.get_models():
            return super().delete(force_policy)

        objs: list[Model] = list(self.all())
        changes: dict[PK, dict[FieldName, tuple[OldValue, NewValue]]]
        changes = {obj.pk: model_instance_diff(obj, None) for obj in objs}

        with transaction.atomic():
            ret = super().delete(force_policy)
            bulk_create_log_entries(objs, LogEntry.Action.DELETE, changes)

        return ret


class PostFetchQuerySetMixin:
    """Patch QuerySet so that results can be modified right after they are fetched."""

    def _fetch_all(self):
        if self._result_cache is None:
            results: list[Model] = list(self._iterable_class(self))
            self._result_cache = self.model.post_fetch_hook(results)
        if self._prefetch_related_lookups and not self._prefetch_done:
            self._prefetch_related_objects()


class HitasQuerySet(
    AuditableUpdateMixin,
    AuditableBulkCreateMixin,
    AuditableDeleteMixin,
    PostFetchQuerySetMixin,
    QuerySet,
):
    pass


class HitasManager(BaseManager.from_queryset(HitasQuerySet)):
    pass


class PostFetchModelMixin:
    @classmethod
    def post_fetch_hook(cls: type[TModel], results: list[TModel]) -> list[TModel]:
        """Implement this method to modify queryset results after they are fetched."""
        return results


class HitasModel(PostFetchModelMixin, Model):
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
    AuditableDeleteForceMixin,
    PostFetchQuerySetMixin,
    SafeDeleteQueryset,
):
    pass


class HitasSafeDeleteManager(SafeDeleteManager):
    _queryset_class = HitasSafeDeleteQuerySet


class HitasSafeDeleteAllManager(SafeDeleteAllManager):
    _queryset_class = HitasSafeDeleteQuerySet


class HitasSafeDeleteDeletedManager(SafeDeleteDeletedManager):
    _queryset_class = HitasSafeDeleteQuerySet


class HitasSafeDeleteModel(PostFetchModelMixin, SafeDeleteModel):
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

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True


class HitasModelDecimalField(models.DecimalField):
    def __init__(self, max_digits=15, decimal_places=2, validators=None, **kwargs):
        if validators is None:
            validators = [MinValueValidator(Decimal("0"))]
        super().__init__(max_digits=max_digits, decimal_places=decimal_places, validators=validators, **kwargs)


class HitasImprovement(HitasSafeDeleteModel):
    name = models.CharField(max_length=128)
    completion_date = models.DateField()
    value = HitasModelDecimalField(validators=[MinValueValidator(0)])

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
    no_deductions = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = HitasImprovement.Meta.ordering
