import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional


def roundup(v: Decimal) -> Optional[float]:
    if v is None:
        return None

    return float(v.quantize(Decimal(".00"), ROUND_HALF_UP))


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
    return (second.year - first.year) * 12 + (second.month - first.month)
