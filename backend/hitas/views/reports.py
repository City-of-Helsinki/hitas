import datetime
from typing import Any

from django.http import HttpResponse
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet

from hitas.services.apartment_sale import find_sales_on_interval_for_reporting
from hitas.services.reports import build_sales_report_excel
from hitas.types import HitasJSONRenderer
from hitas.views.utils.excel import ExcelRenderer, get_excel_response


class SalesReportSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs["start_date"] > attrs["end_date"]:
            raise serializers.ValidationError("Start date must be before end date")
        return attrs


class SalesReportView(ViewSet):
    renderer_classes = [HitasJSONRenderer, ExcelRenderer]

    def list(self, request: Request, *args, **kwargs) -> HttpResponse:
        serializer = SalesReportSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        start: datetime.date = serializer.validated_data["start_date"]
        end: datetime.date = serializer.validated_data["end_date"]

        sales = find_sales_on_interval_for_reporting(start_date=start, end_date=end)
        workbook = build_sales_report_excel(sales)
        filename = f"Hitas kaupat aikavälillä {start.isoformat()} - {end.isoformat()}.xlsx"
        return get_excel_response(filename=filename, excel=workbook)
