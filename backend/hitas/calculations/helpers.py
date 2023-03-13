import datetime

from dateutil import relativedelta


def months_between_dates(first: datetime.date, second: datetime.date) -> int:
    second_day_is_last_day_of_month = (second + relativedelta.relativedelta(days=1)).month != second.month

    return (
        (second.year - first.year) * 12
        + (second.month - first.month)
        - (1 if second.day < first.day and not second_day_is_last_day_of_month else 0)
    )
