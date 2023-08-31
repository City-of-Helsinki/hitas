import datetime

from django.db import models
from django.db.models import Avg, Count, F, Max, Q, Value
from django.db.models.functions import Coalesce, Concat, ExtractDay, Round

from hitas.models import JobPerformance
from hitas.models.job_performance import JobPerformanceSource
from users.models import User


def find_job_performance(source: JobPerformanceSource, start_date: datetime.date, end_date: datetime.date):
    return (
        JobPerformance.objects.filter(
            source=source,
            delivery_date__gte=start_date,
            delivery_date__lte=end_date,
        )
        .annotate(
            days_between_request_and_delivery=ExtractDay(F("delivery_date") - F("request_date")),
        )
        .aggregate(
            count=Count("id"),
            average_days=Coalesce(Round(Avg("days_between_request_and_delivery")), 0.0),
            maximum_days=Coalesce(Max("days_between_request_and_delivery"), 0),
        )
    )


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
