import datetime

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from hitas.models.job_performance import JobPerformanceSource
from hitas.services.job_performance import find_job_performance, find_job_performance_per_user
from hitas.types import HitasJSONRenderer
from hitas.views.reports import SalesReportSerializer


class JobPerformanceView(ViewSet):
    renderer_classes = [HitasJSONRenderer]

    def generic_job_performance_view(self, request: Request, source: JobPerformanceSource) -> HttpResponse:
        serializer = SalesReportSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        start: datetime.date = serializer.validated_data["start_date"]
        end: datetime.date = serializer.validated_data["end_date"]

        job_performance_totals = find_job_performance(
            source=source,
            start_date=start,
            end_date=end,
        )
        job_performance_per_user = find_job_performance_per_user(
            source=source,
            start_date=start,
            end_date=end,
        )

        data = {
            "totals": job_performance_totals,
            "per_user": job_performance_per_user,
        }
        return Response(data=data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        url_path=r"unconfirmed-maximum-price",
        url_name="unconfirmed-maximum-price",
    )
    def unconfirmed_maximum_price(self, request: Request, *args, **kwargs) -> HttpResponse:
        source = JobPerformanceSource.UNCONFIRMED_MAX_PRICE
        return self.generic_job_performance_view(request, source)

    @action(
        methods=["GET"],
        detail=False,
        url_path=r"confirmed-maximum-price",
        url_name="confirmed-maximum-price",
    )
    def confirmed_maximum_price(self, request: Request, *args, **kwargs) -> HttpResponse:
        source = JobPerformanceSource.CONFIRMED_MAX_PRICE
        return self.generic_job_performance_view(request, source)
