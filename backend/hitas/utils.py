import datetime
import operator
import re
from decimal import ROUND_HALF_UP, Decimal
from functools import partial
from typing import Any, Iterable, Optional, overload
from uuid import UUID

from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import Case, Count, F, Max, Model, OuterRef, Q, Subquery, When
from django.db.models.functions import NullIf
from django.utils import timezone
from openpyxl.cell import Cell
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from hitas.models._base import HitasModelDecimalField


def subquery_count(model: type[Model], *outer_fields: str, **kwargs) -> Subquery:
    """Annotates the number of rows on the model (with references to outer_field) to the queryset."""
    return Subquery(
        queryset=(
            model.objects.filter(**{outer_field: OuterRef(outer_field) for outer_field in outer_fields}, **kwargs)
            .values(*outer_fields)  # fixes grouping
            .annotate(__count=Count("*"))
            .values("__count")
        ),
        output_field=models.IntegerField(),
    )


def subquery_first_id(model: type[Model], outer_field: str, order_by: list[str], **kwargs) -> Subquery:
    """Selects the first row on the model (with references to outer_field) based on the given ordering."""
    return Subquery(
        model.objects.filter(**{outer_field: OuterRef(outer_field)}, **kwargs)
        .order_by(*order_by)
        .values_list("id", flat=True)[:1]
    )


def max_if_all_not_null(ref: str, max: Any, min: Any) -> NullIf:
    """Return the maximum value in the array referenced by 'ref', but only if the array contains no null values.

    Null values will be converted to the supplied 'max' value (which should always be the largest value in the array).
    If the 'max' value exists in the array, the aggregation result will be null instead of the 'max' value.

    If 'ref' has empty relations before the target array, these relations will produce nulls in the resulting array.
    Therefore, replace empty relations with the supplied 'min' value (which should always be the lowest value in
    the array). If the 'min' values would be the largest value (e.g. there are only empty relations), replace
    the 'min' value with nulls instead.

    Also, any soft-deleted relations will be replaced with the supplied 'min' value, resulting in the same effect
    as described above.

    :param ref: Reference to an array of items to aggregate.
    :param max: Highest possible value, which will replace nulls, e.g., 'datetime.max'.
    :param min: Lowest possible value, used when there are empty relations, e.g. 'datetime.min'.
    """
    parent_ref = "__".join(ref.split("__")[:-1])
    return NullIf(
        NullIf(
            Max(
                Case(
                    When(
                        condition=~Q(**{f"{parent_ref}__deleted": None}),
                        then=min,
                    ),
                    When(
                        condition=Q(**{f"{parent_ref}__isnull": True}),
                        then=min,
                    ),
                    When(
                        condition=Q(**{f"{ref}__isnull": True}),
                        then=max,
                    ),
                    default=F(ref),
                ),
            ),
            max,
        ),
        min,
    )


max_date_if_all_not_null = partial(max_if_all_not_null, max=datetime.date.max, min=datetime.date.min)


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
    return monthify(timezone.now().date())


def monthify(date: datetime.date) -> datetime.date:
    return date.replace(day=1)


def business_quarter(date: datetime.date) -> datetime.date:
    """Get business quarter (yyyy-[1,4,7,10]-01) from the given date."""
    if date.month in (1, 2, 3):
        return date.replace(month=1, day=1)
    if date.month in (4, 5, 6):
        return date.replace(month=4, day=1)
    if date.month in (7, 8, 9):
        return date.replace(month=7, day=1)
    return date.replace(month=10, day=1)


def hitas_calculation_quarter(date: datetime.date) -> datetime.date:
    """Get hitas calculation quarter (yyyy-[02,05,08,11]-01) from the given date.

    Hitas calculation quarters are different from business quarters, since hitas calculations
    have to be made at least one month after business quarters start due to delays in receiving index
    information from Tilastokeskus.
    """
    if date.month == 1:
        return date.replace(year=date.year - 1, month=11, day=1)
    if date.month in (2, 3, 4):
        return date.replace(month=2, day=1)
    if date.month in (5, 6, 7):
        return date.replace(month=5, day=1)
    if date.month in (8, 9, 10):
        return date.replace(month=8, day=1)
    return date.replace(month=11, day=1)


def to_quarter(date: datetime.date) -> str:
    """Get business quarter as a string from a date."""
    if date.month in (1, 2, 3):
        return f"{date.year}Q1"
    if date.month in (4, 5, 6):
        return f"{date.year}Q2"
    if date.month in (7, 8, 9):
        return f"{date.year}Q3"
    if date.month in (10, 11, 12):
        return f"{date.year}Q4"
    raise NotImplementedError


def from_quarter(quarter: str) -> datetime.date:
    """Get business quarter as a date from string."""
    result = re.match(r"(?P<year>\d{4})Q(?P<quarter>[1234])", quarter)
    if result is None:
        raise ValueError(f"{quarter!r} is not a valid quarter.")

    year = result.group("year")
    number = result.group("quarter")
    number_to_month = {"1": 1, "2": 4, "3": 7, "4": 10}
    month = number_to_month[number]

    return datetime.date(year=int(year), month=month, day=1)


def from_iso_format_or_today_if_none(date: Optional[str]) -> datetime.date:
    if date is None:
        return timezone.now().date()
    return datetime.date.fromisoformat(date)


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
def roundup(v: Decimal, precision: int = 2) -> Decimal: ...


@overload
def roundup(v: None, precision: int = 2) -> None: ...


def roundup(v, precision: int = 2):
    if v is None:
        return None

    if precision <= 0:
        return v.quantize(Decimal("1"), ROUND_HALF_UP)
    return v.quantize(Decimal("." + "0" * precision), ROUND_HALF_UP)


def humanize_relativedelta(delta: relativedelta) -> str:
    return f"{delta.years} v {delta.months} kk"


def resize_columns(worksheet: Worksheet) -> None:
    column_widths = []
    cells: list[Cell]
    for cells in worksheet.rows:
        for i, cell in enumerate(cells):
            length = len(str(cell.value)) + 5
            if len(column_widths) == i:
                column_widths.append(length)
            elif length > column_widths[i]:
                column_widths[i] = length

    for i, column_width in enumerate(column_widths, 1):
        worksheet.column_dimensions[get_column_letter(i)].width = column_width


def format_sheet(worksheet: Worksheet, formatting_rules: dict[str, dict[str, Any]]) -> None:
    cell: Cell
    for column, changes in formatting_rules.items():
        is_cell = any(num in column for num in "0123456789")
        for key, value in changes.items():
            if is_cell:
                _set_cell_attribute(worksheet[column], key, value)
                continue

            for cell in worksheet[column][1:]:
                _set_cell_attribute(cell, key, value)


def _set_cell_attribute(cell: Cell, key: str, value: Any) -> None:
    if not isinstance(value, dict):
        setattr(cell, key, value)
        return

    val = value.get(cell.value)
    if val is None:
        return

    setattr(cell, key, val)


class SQSum(Subquery):
    """Refs. (https://stackoverflow.com/a/58001368)"""

    template = "(SELECT SUM(%(sum_field)s) FROM (%(subquery)s) _sum)"
    output_field = HitasModelDecimalField()

    def __init__(self, queryset, output_field=None, *, sum_field="", **extra):
        extra["sum_field"] = sum_field
        super().__init__(queryset, output_field, **extra)


def index_of(tup: tuple[Any, ...], value: Any) -> Optional[int]:
    """Get the index of a value in a tuple or None if item is not in the tuple."""
    try:
        return tup.index(value)
    except ValueError:
        return None
