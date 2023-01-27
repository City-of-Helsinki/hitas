import datetime
import operator
import uuid
from typing import Any, Optional, TypeVar

from django.db import models
from django.db.models import Value
from django.db.models.functions import Round
from django.utils import timezone

from hitas.exceptions import HitasModelNotFound


class RoundWithPrecision(Round):
    """Implement round from Django 4.0
    https://github.com/django/django/blob/main/django/db/models/functions/math.py#L176
    """

    arity = None  # Override Transform's arity=1 to enable passing precision.

    def __init__(self, expression, precision=0, **extra):
        super().__init__(expression, precision, **extra)

    def as_sqlite(self, compiler, connection, **extra_context):
        precision = self.get_source_expressions()[1]
        if isinstance(precision, Value) and precision.value < 0:
            raise ValueError("SQLite does not support negative precision.")
        return super().as_sqlite(compiler, connection, **extra_context)

    def _resolve_output_field(self):
        source = self.get_source_expressions()[0]
        return source.output_field


def safe_attrgetter(obj: Any, dotted_path: str, default: Optional[Any]) -> Any:
    """
    Examples:
        >>> safe_attrgetter(object, "__class__.__name__.__class__.__name__")
        'str'
        >>> safe_attrgetter(object, "foo.bar.baz") is None
        True
        >>> safe_attrgetter(object, "foo.bar.baz", default="")
        ''
    """
    try:
        return operator.attrgetter(dotted_path)(obj)
    except AttributeError:
        return default


def this_month() -> datetime.date:
    return monthify(timezone.now().today().date())


def monthify(date: datetime.date) -> datetime.date:
    return date.replace(day=1)


def valid_uuid(value: str, version: int = 4) -> bool:
    try:
        uuid.UUID(value, version=version)
        return True
    except ValueError:
        return False


def lookup_id_to_uuid(lookup_id: str, model_class: type[models.Model]) -> uuid.UUID:
    try:
        return uuid.UUID(hex=lookup_id)
    except ValueError as error:
        raise HitasModelNotFound(model=model_class) from error


def lookup_model_id_by_uuid(lookup_id: str, model_class: type[models.Model], **kwargs) -> int:
    uuid = lookup_id_to_uuid(lookup_id, model_class)

    try:
        return model_class.objects.only("id").get(uuid=uuid, **kwargs).id
    except model_class.DoesNotExist as error:
        raise HitasModelNotFound(model=model_class) from error


TModel = TypeVar("TModel", bound=models.Model)
