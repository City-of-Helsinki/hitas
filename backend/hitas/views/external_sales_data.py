from typing import Optional, TypedDict

from dateutil.relativedelta import relativedelta
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from hitas.exceptions import HitasModelNotFound
from hitas.models import ExternalSalesData
from hitas.services.external_sales_data import create_external_sales_data, remove_unused_areas
from hitas.services.validation import validate_postal_code, validate_quarter
from hitas.utils import business_quarter, from_iso_format_or_today_if_none, to_quarter
from hitas.views.utils.excel import NewExcelParser, OldExcelParser, parse_sheet
from hitas.views.utils.fields import IntegerOrEmpty


class CostAreaSalesCatalogRow(TypedDict):
    postal_code: str
    quarter_1_price: Optional[int]
    quarter_1_sale_count: Optional[int]
    quarter_2_price: Optional[int]
    quarter_2_sale_count: Optional[int]
    quarter_3_price: Optional[int]
    quarter_3_sale_count: Optional[int]
    quarter_4_price: Optional[int]
    quarter_4_sale_count: Optional[int]


class CostAreaSalesCatalogData(TypedDict):
    areas: list[CostAreaSalesCatalogRow]
    quarter_1: str
    quarter_2: str
    quarter_3: str
    quarter_4: str


class CostAreaSalesCatalogRowSerializer(serializers.Serializer):
    postal_code = serializers.CharField(min_length=5)
    quarter_1_price = IntegerOrEmpty(allow_null=True, min_value=0)
    quarter_1_sale_count = IntegerOrEmpty(allow_null=True, min_value=0)
    quarter_2_price = IntegerOrEmpty(allow_null=True, min_value=0)
    quarter_2_sale_count = IntegerOrEmpty(allow_null=True, min_value=0)
    quarter_3_price = IntegerOrEmpty(allow_null=True, min_value=0)
    quarter_3_sale_count = IntegerOrEmpty(allow_null=True, min_value=0)
    quarter_4_price = IntegerOrEmpty(allow_null=True, min_value=0)
    quarter_4_sale_count = IntegerOrEmpty(allow_null=True, min_value=0)

    @staticmethod
    def validate_postal_code(value: str) -> str:
        postal_code = value.strip()[:5].strip()  # remove area name and leave just the postal code
        return validate_postal_code(postal_code)


class CostAreaSalesCatalogExtraSerializer(serializers.Serializer):
    quarter_1 = serializers.CharField(min_length=6)
    quarter_2 = serializers.CharField(min_length=6)
    quarter_3 = serializers.CharField(min_length=6)
    quarter_4 = serializers.CharField(min_length=6)

    @staticmethod
    def validate_quarter(value: str) -> str:
        value = value.strip()[:6].strip().upper()
        return validate_quarter(value)

    validate_quarter_1 = validate_quarter
    validate_quarter_2 = validate_quarter
    validate_quarter_3 = validate_quarter
    validate_quarter_4 = validate_quarter


class ExternalSalesDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalSalesData
        fields = [
            "calculation_quarter",
            "quarter_1",
            "quarter_2",
            "quarter_3",
            "quarter_4",
        ]


class ExternalSalesDataView(ViewSet):
    parser_classes = [NewExcelParser, OldExcelParser]

    def create(self, request, *args, **kwargs) -> Response:
        workbook: Workbook = request.data
        worksheet: Worksheet = workbook.worksheets[0]
        sheet_data: CostAreaSalesCatalogData = parse_sheet(
            worksheet,
            row_data_key="areas",
            row_format={
                "postal_code": "A",
                "quarter_1_price": "H",
                "quarter_1_sale_count": "I",
                "quarter_2_price": "J",
                "quarter_2_sale_count": "K",
                "quarter_3_price": "L",
                "quarter_3_sale_count": "M",
                "quarter_4_price": "N",
                "quarter_4_sale_count": "O",
            },
            extra_format={
                "1": {},
                "2": {},
                "3": {
                    "quarter_1": "H",
                    "quarter_2": "J",
                    "quarter_3": "L",
                    "quarter_4": "N",
                },
                "4": {},
            },
            row_serializer=CostAreaSalesCatalogRowSerializer,
            extra_serializer=CostAreaSalesCatalogExtraSerializer,
            row_post_validators=[],
        )

        remove_unused_areas(sheet_data)
        sales_data = create_external_sales_data(sheet_data)
        data = ExternalSalesDataSerializer(sales_data).data
        return Response(data=data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs) -> Response:
        try:
            calculation_date = from_iso_format_or_today_if_none(request.query_params.get("calculation_date"))
        except ValueError as error:
            raise ValidationError({"calculation_date": str(error)}) from error

        calculation_quarter = business_quarter(calculation_date)
        quarter = to_quarter(calculation_quarter - relativedelta(months=3))

        try:
            sales_data = ExternalSalesData.objects.get(calculation_quarter=quarter)
        except ExternalSalesData.DoesNotExist as error:
            raise HitasModelNotFound(ExternalSalesData) from error

        data = ExternalSalesDataSerializer(sales_data).data
        return Response(data=data, status=status.HTTP_200_OK)
