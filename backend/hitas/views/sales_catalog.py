from decimal import Decimal
from itertools import combinations
from typing import TypedDict, Union

from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from hitas.models import ApartmentType
from hitas.utils import check_for_overlap
from hitas.views.utils.excel import ErrorData, NewExcelParser, OldExcelParser, RowFormat, error_key, parse_sheet
from hitas.views.utils.fields import NumberOrRangeField


class MinimalApartmentType(TypedDict):
    id: str
    value: str


class SalesCatalogApartment(TypedDict):
    row: int
    stair: str
    floor: str
    apartment_number: int
    rooms: Union[int, str]
    apartment_type: Union[str, MinimalApartmentType]
    surface_area: Decimal
    share_number_start: int
    share_number_end: int
    debt_free_purchase_price: Decimal
    primary_loan_amount: Decimal
    acquisition_price: Decimal


class SalesCatalogApartmentSerializer(serializers.Serializer):
    row = serializers.IntegerField(min_value=1)
    stair = serializers.CharField(max_length=16)
    floor = serializers.CharField(max_length=50)
    apartment_number = serializers.IntegerField(min_value=0)
    rooms = NumberOrRangeField(min_value=1)
    apartment_type = serializers.CharField(max_length=1024)
    surface_area = serializers.DecimalField(max_digits=15, decimal_places=2)
    share_number_start = serializers.IntegerField(min_value=1)
    share_number_end = serializers.IntegerField(min_value=1)
    debt_free_purchase_price = serializers.DecimalField(max_digits=15, decimal_places=2)
    primary_loan_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    acquisition_price = serializers.DecimalField(max_digits=15, decimal_places=2)


class SalesCatalogDataSerializer(serializers.Serializer):
    confirmation_date = serializers.DateTimeField()
    total_surface_area = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_acquisition_price = serializers.DecimalField(max_digits=15, decimal_places=2)
    acquisition_price_limit = serializers.DecimalField(max_digits=15, decimal_places=2)

    def validate(self, data):
        if data["total_acquisition_price"] > data["acquisition_price_limit"]:
            raise ValidationError(
                detail={
                    "total_acquisition_price": "'total_acquisition_price' is higher than 'acquisition_price_limit'.",
                },
            )
        return data


class SalesCatalogView(ViewSet):
    parser_classes = [NewExcelParser, OldExcelParser]

    def create(self, request, *args, **kwargs) -> Response:
        workbook: Workbook = request.data
        worksheet: Worksheet = workbook.worksheets[0]
        data = parse_sheet(
            worksheet,
            row_data_key="apartments",
            row_format={
                "stair": "A",
                "floor": "B",
                "apartment_number": "C",
                "rooms": "D",
                "apartment_type": "E",
                "surface_area": "F",
                "share_number_start": "G",
                "share_number_end": "H",
                "debt_free_purchase_price": "I",
                "primary_loan_amount": "J",
                "acquisition_price": "K",
            },
            extra_format={
                "1": {},
                "2": {"confirmation_date": "F"},
                "3": {"acquisition_price_limit": "E"},
                "4": {},
                "final": {"total_surface_area": "F", "total_acquisition_price": "K"},
            },
            row_serializer=SalesCatalogApartmentSerializer,
            extra_serializer=SalesCatalogDataSerializer,
            row_post_validators=[
                check_share_ranges,
                check_apartment_types,
            ],
        )
        return Response(data=data, status=status.HTTP_200_OK)


def check_share_ranges(apartments: list[SalesCatalogApartment], row_format: RowFormat, errors: ErrorData) -> None:
    share_ranges_by_row: dict[int, set[int]] = {
        apartment["row"]: set(range(apartment["share_number_start"], apartment["share_number_end"] + 1))
        for apartment in apartments
        if apartment["share_number_start"] is not None and apartment["share_number_end"] is not None
    }

    for (row_1, range_1), (row_2, range_2) in combinations(share_ranges_by_row.items(), r=2):
        start, end = check_for_overlap(range_1, range_2)
        msg = "Overlapping shares with apartment on row {row}: {values}"

        if start is not None and end is not None:
            values = f"{start}-{end}"
            errors[error_key("share_number_start", row_1, row_format)] = [msg.format(row=row_2, values=values)]
            errors[error_key("share_number_start", row_2, row_format)] = [msg.format(row=row_1, values=values)]
            errors[error_key("share_number_end", row_1, row_format)] = [msg.format(row=row_2, values=values)]
            errors[error_key("share_number_end", row_2, row_format)] = [msg.format(row=row_1, values=values)]
        elif start is not None:
            errors[error_key("share_number_start", row_1, row_format)] = [msg.format(row=row_2, values=str(start))]
            errors[error_key("share_number_end", row_2, row_format)] = [msg.format(row=row_1, values=str(start))]
        elif end is not None:
            errors[error_key("share_number_end", row_1, row_format)] = [msg.format(row=row_2, values=str(end))]
            errors[error_key("share_number_start", row_2, row_format)] = [msg.format(row=row_1, values=str(end))]


def check_apartment_types(apartments: list[SalesCatalogApartment], row_format: RowFormat, errors: ErrorData) -> None:
    apartment_types: set[str] = {apartment["apartment_type"] for apartment in apartments}
    apartment_types_by_values: dict[str, MinimalApartmentType] = {
        apartment_type.value: MinimalApartmentType(id=apartment_type.uuid.hex, value=apartment_type.value)
        for apartment_type in ApartmentType.objects.filter(value__in=apartment_types).all()
    }

    for apartment in apartments:
        try:
            apartment["apartment_type"] = apartment_types_by_values[apartment["apartment_type"]]
        except KeyError:
            key = error_key("apartment_type", apartment["row"], row_format)
            if key in errors:  # field already null or empty
                continue
            msg = f"Apartment type {apartment['apartment_type']} not found"
            errors[key] = [msg]
