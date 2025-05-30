import datetime
import json
import logging
from typing import TYPE_CHECKING, Iterable, Literal, Optional, TypeAlias, overload

from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.db.models import DateTimeField, OuterRef, Subquery
from django.utils.encoding import smart_str

if TYPE_CHECKING:
    from hitas.models._base import AuditLogAdditionalDataT, HitasModel, HitasSafeDeleteModel


logger = logging.getLogger(__name__)

PK: TypeAlias = int
FieldName: TypeAlias = str
OldValue: TypeAlias = str
NewValue: TypeAlias = str


def bulk_create_log_entries(
    objs: Iterable["HitasSafeDeleteModel"],
    action: Literal[0, 1, 2, 3],
    changes: dict[PK, dict[FieldName, tuple[OldValue, NewValue]]],
) -> list[LogEntry]:
    """Adapted from 'auditlog.models.LogEntryManager.log_create'."""

    log_entries: list[LogEntry] = []
    for obj in objs:
        pk = LogEntry.objects._get_pk_value(obj)

        if pk not in changes:
            continue

        get_additional_data = getattr(obj, "get_additional_data", None)
        additional_data: Optional[AuditLogAdditionalDataT]
        additional_data = get_additional_data() if callable(get_additional_data) else None
        serialized_data = LogEntry.objects._get_serialized_data_or_none(obj)

        log_entries.append(
            LogEntry(
                content_type=ContentType.objects.get_for_model(obj),
                object_pk=pk,
                object_id=pk if isinstance(pk, int) else None,
                object_repr=smart_str(obj),
                action=action,
                changes=json.dumps(changes[obj.pk]),
                serialized_data=serialized_data,
                additional_data=additional_data,
            )
        )

    return LogEntry.objects.bulk_create(log_entries, ignore_conflicts=True)


@overload
def get_last_modified(
    model: type["HitasModel"] | type["HitasSafeDeleteModel"],
    *,
    model_id: str,
    hint: str,
) -> Subquery: ...


@overload
def get_last_modified(
    model: type["HitasModel"] | type["HitasSafeDeleteModel"],
    *,
    model_id: int,
    hint: str,
) -> Optional[datetime.date]: ...


def last_modified(
    model: type["HitasModel"] | type["HitasSafeDeleteModel"],
    *,
    model_id: str | int,
    hint: str = "",
):
    """
    Return the timestamp for the last audit log for the given model object
    (where its changes contain the hinted string).
    """
    subquery = isinstance(model_id, str)
    queryset = (
        LogEntry.objects.filter(
            content_type=ContentType.objects.get_for_model(model),
            object_id=OuterRef(model_id) if subquery else model_id,
            changes__contains=hint,
        )
        .order_by("-timestamp")
        .values_list("timestamp", flat=True)
    )
    if subquery:
        return Subquery(queryset=queryset[:1], output_field=DateTimeField(null=True))
    return queryset.first()


def last_log(
    model: type["HitasModel"] | type["HitasSafeDeleteModel"],
    *,
    model_id: int,
    hint: str = "",
) -> Optional[LogEntry]:
    """Return the last audit log for the given model object (where its changes contain the hinted string)."""
    return (
        LogEntry.objects.select_related("actor")
        .filter(
            content_type=ContentType.objects.get_for_model(model),
            object_id=model_id,
            changes__contains=hint,
        )
        .order_by("-timestamp")
        .first()
    )
