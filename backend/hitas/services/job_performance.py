import datetime
from typing import Callable, List, TypeAlias, Union

from auditlog.models import LogEntry
from django.db import models
from django.db.models import Count, F, Q, Value
from django.db.models.functions import Concat
from django.utils import timezone

from hitas.models import ApartmentSale, JobPerformance
from hitas.models.job_performance import JobPerformanceSource
from users.models import User

DEFAULT_DAYS_FOR_SAME_DAY_HANDLING = 0.5
HandleDaysNumber: TypeAlias = Union[int, float]


def find_job_performance(source: JobPerformanceSource, start_date: datetime.date, end_date: datetime.date):
    qs = JobPerformance.objects.filter(source=source, delivery_date__gte=start_date, delivery_date__lte=end_date)
    data = qs.aggregate(count=Count("id"))
    handle_days = []
    for jp in qs.all():
        handle_days.append(_get_week_days_between_request_and_delivery(jp.delivery_date, jp.request_date))

    data.update(
        {
            "average_days": round(_get_average_handle_days(handle_days), 2),
            "maximum_days": _get_maximum_handle_days(handle_days),
        }
    )
    return data


def _get_week_days_between_request_and_delivery(delivery_date, request_date):
    """Default handling time for 0 days needs to be done here
    so there is a difference with no entries ond same day handling times"""
    raw_delta_days = (delivery_date - request_date).days
    dates = (request_date + datetime.timedelta(i + 1) for i in range(raw_delta_days))
    return sum(1 for day in dates if _is_weekday(day)) or DEFAULT_DAYS_FOR_SAME_DAY_HANDLING


def _is_weekday(day: datetime.date):
    """date.weekday return values from 0 to 6 0=monday, 1=tuesday etc.
    saturday=5 and sunday=6
    """
    return day.weekday() < 5


def _get_combined_value(
    handle_days: List[Union[int, float]], calculate: Callable[[List[HandleDaysNumber]], HandleDaysNumber]
) -> HandleDaysNumber:
    if len(handle_days) == 0:
        return 0
    return calculate(handle_days)


def _get_average_handle_days(handle_days: List[HandleDaysNumber]) -> HandleDaysNumber:
    return _get_combined_value(handle_days, lambda x: sum(x) / len(x))


def _get_maximum_handle_days(handle_days: List[HandleDaysNumber]) -> HandleDaysNumber:
    return _get_combined_value(handle_days, max)


def find_job_performance_per_user(source: JobPerformanceSource, start_date: datetime.date, end_date: datetime.date):
    filter = Q(
        job_performances__source=source,
        job_performances__delivery_date__gte=start_date,
        job_performances__delivery_date__lte=end_date,
    )

    return (
        User.objects.annotate(
            full_name=Concat(F("first_name"), Value(" "), F("last_name"), output_field=models.CharField()),
            job_performance_count=Count("job_performances", filter=filter),
        )
        .exclude(job_performance_count=0)
        .values("full_name", "job_performance_count")
        .order_by("-job_performance_count")
    )


def find_apartment_sale_creations(start_date: datetime.date, end_date: datetime.date):
    """Creation times of apartment sales are found from log entries"""
    return LogEntry.objects.get_for_model(ApartmentSale).filter(
        action=LogEntry.Action.CREATE,
        timestamp__range=(
            timezone.make_aware(datetime.datetime.combine(start_date, datetime.time.min)),
            timezone.make_aware(datetime.datetime.combine(end_date, datetime.time.max)),
        ),
    )
