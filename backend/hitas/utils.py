import datetime
import operator
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Iterable, Optional, overload
from uuid import UUID

from django.db import models
from django.db.models import Count, Model, OuterRef, Subquery, Value
from django.db.models.functions import Round
from django.utils import timezone


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


def subquery_count(model: type[Model], outer_field: str, **kwargs) -> Subquery:
    """Annotates the number of rows on the model (with references to outer_field) to the queryset."""
    return Subquery(
        queryset=(
            model.objects.filter(**{outer_field: OuterRef(outer_field)}, **kwargs)
            .values(outer_field)  # fixes grouping
            .annotate(__count=Count("*"))
            .values("__count")
        ),
        output_field=models.IntegerField(),
    )


def subquery_first_id(model: type[Model], outer_field: str, order_by: str, **kwargs) -> Subquery:
    """Selects the first row on the model (with references to outer_field) based on the given ordering."""
    return Subquery(
        model.objects.filter(**{outer_field: OuterRef(outer_field)}, **kwargs)
        .order_by(order_by)
        .values_list("id", flat=True)[:1]
    )


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
        UUID(value, version=version)
        return True
    except ValueError:
        return False


def check_for_overlap(range_1: set[int], range_2: Iterable[int]) -> tuple[Optional[int], Optional[int]]:
    overlapping: set[int] = range_1.intersection(range_2)
    if not overlapping:
        return None, None

    if len(overlapping) == 1:
        share: int = next(iter(overlapping))
        start: int = next(iter(range_1))

        if share == start:
            return share, None

        return None, share

    sorted_shares: list[int] = sorted(overlapping)
    return sorted_shares[0], sorted_shares[-1]


@overload
def roundup(v: Decimal, precision: int = 2) -> Decimal:
    ...


@overload
def roundup(v: None, precision: int = 2) -> None:
    ...


def roundup(v, precision: int = 2):
    if v is None:
        return None

    if precision <= 0:
        return v.quantize(Decimal("1"), ROUND_HALF_UP)
    return v.quantize(Decimal("." + "0" * precision), ROUND_HALF_UP)
