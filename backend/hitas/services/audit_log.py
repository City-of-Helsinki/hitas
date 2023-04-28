from typing import TYPE_CHECKING, Iterable, Literal, TypeAlias

from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.encoding import smart_str

if TYPE_CHECKING:
    from hitas.models._base import HitasSafeDeleteModel


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
        serialized_data = LogEntry.objects._get_serialized_data_or_none(obj)
        log_entries.append(
            LogEntry(
                content_type=ContentType.objects.get_for_model(obj),
                object_pk=pk,
                object_id=pk if isinstance(pk, int) else None,
                object_repr=smart_str(obj),
                action=action,
                changes=changes[obj.pk],
                serialized_data=serialized_data,
            )
        )

    # Delete log entries with the same pk as a newly created model.
    if action is LogEntry.Action.CREATE:
        condition = Q()
        for log_entry in log_entries:
            condition |= Q(content_type=log_entry.content_type) & (
                Q(object_pk=log_entry.object_pk) | Q(object_id=log_entry.object_id)
            )

        LogEntry.objects.filter(condition).delete()

    return LogEntry.objects.bulk_create(log_entries, ignore_conflicts=True)
