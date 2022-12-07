import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from dateutil import relativedelta


def roundup(v: Decimal) -> Optional[Decimal]:
    if v is None:
        return None

    return v.quantize(Decimal(".00"), ROUND_HALF_UP)


class NoneSum:
    def __init__(self, default_fn=int):
        self.value = None
        self.default_fn = default_fn

    def __iadd__(self, other):
        if other is None:
            return self

        if self.value is None:
            self.value = self.default_fn()

        self.value += other
        return self


def months_between_dates(first: datetime.date, second: datetime.date) -> int:
    second_day_is_last_day_of_month = (second + relativedelta.relativedelta(days=1)).month != second.month

    return (
        (second.year - first.year) * 12
        + (second.month - first.month)
        - (1 if second.day < first.day and not second_day_is_last_day_of_month else 0)
    )
