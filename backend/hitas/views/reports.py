import datetime
from typing import Any

from django.http import HttpResponse
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from hitas.models import HousingCompany, Owner, Ownership
from hitas.services.apartment_sale import find_sales_on_interval_for_reporting
from hitas.services.housing_company import (
    find_half_hitas_housing_companies_for_reporting,
    find_housing_companies_for_state_reporting,
    find_regulated_housing_companies_for_reporting,
    find_unregulated_housing_companies_for_reporting,
)
from hitas.services.owner import (
    find_apartments_by_housing_company,
    find_owners_with_multiple_ownerships,
    find_regulated_ownerships,
)
from hitas.services.reports import (
    build_housing_company_state_report_excel,
    build_multiple_ownerships_report_excel,
    build_owners_by_housing_companies_report_excel,
    build_regulated_housing_companies_report_excel,
    build_regulated_ownerships_report_excel,
    build_sales_and_maximum_prices_report_excel,
    build_sales_by_postal_code_and_area_report_excel,
    build_sales_report_excel,
    build_unregulated_housing_companies_report_excel,
    sort_housing_companies_by_state,
)
from hitas.services.validation import lookup_model_by_uuid
from hitas.types import HitasJSONRenderer
from hitas.views.utils import HitasDecimalField
from hitas.views.utils.excel import ExcelRenderer, get_excel_response


class SalesReportSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    filter = serializers.ChoiceField(choices=["all", "resale", "firstsale"], default="all")

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


class SalesAndMaximumPricesReportView(ViewSet):
    renderer_classes = [HitasJSONRenderer, ExcelRenderer]

    def list(self, request: Request, *args, **kwargs) -> HttpResponse:
        serializer = SalesReportSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        start: datetime.date = serializer.validated_data["start_date"]
        end: datetime.date = serializer.validated_data["end_date"]

        sales = find_sales_on_interval_for_reporting(start_date=start, end_date=end)
        workbook = build_sales_and_maximum_prices_report_excel(sales)
        filename = f"Hitas kauppa- ja enimmäishinnat aikavälillä {start.isoformat()} - {end.isoformat()}.xlsx"
        return get_excel_response(filename=filename, excel=workbook)


class RegulatedHousingCompaniesReportView(ViewSet):
    renderer_classes = [HitasJSONRenderer, ExcelRenderer]

    def list(self, request: Request, *args, **kwargs) -> HttpResponse:
        housing_companies = find_regulated_housing_companies_for_reporting()
        workbook = build_regulated_housing_companies_report_excel(housing_companies)
        filename = "Valvonnan piirissä olevat yhtiöt.xlsx"
        return get_excel_response(filename=filename, excel=workbook)


class HalfHitasHousingCompaniesReportView(ViewSet):
    renderer_classes = [HitasJSONRenderer, ExcelRenderer]

    def list(self, request: Request, *args, **kwargs) -> HttpResponse:
        housing_companies = find_half_hitas_housing_companies_for_reporting()
        workbook = build_regulated_housing_companies_report_excel(housing_companies)
        filename = "Puolihitas-yhtiöt.xlsx"
        return get_excel_response(filename=filename, excel=workbook)


class UnregulatedHousingCompaniesReportView(ViewSet):
    renderer_classes = [HitasJSONRenderer, ExcelRenderer]

    def list(self, request: Request, *args, **kwargs) -> HttpResponse:
        housing_companies = find_unregulated_housing_companies_for_reporting()
        workbook = build_unregulated_housing_companies_report_excel(housing_companies)
        filename = "Vapautuneet yhtiöt.xlsx"
        return get_excel_response(filename=filename, excel=workbook)


class HousingCompanyStatesReportView(ViewSet):
    renderer_classes = [HitasJSONRenderer, ExcelRenderer]

    def list(self, request: Request, *args, **kwargs) -> HttpResponse:
        housing_companies = find_housing_companies_for_state_reporting()
        workbook = build_housing_company_state_report_excel(housing_companies)
        filename = "Yhtiöiden tilat.xlsx"
        return get_excel_response(filename=filename, excel=workbook)


class HousingCompanyStatesJSONReportView(ViewSet):
    def list(self, request: Request, *args, **kwargs) -> Response:
        housing_companies = find_housing_companies_for_state_reporting()
        by_state = sort_housing_companies_by_state(housing_companies)

        data = [
            {
                "status": name.value,
                "housing_company_count": info["housing_company_count"],
                "apartment_count": info["apartment_count"],
            }
            for name, info in by_state.items()
        ]

        return Response(data=data, status=status.HTTP_200_OK)


class SalesByPostalCodeAndAreaReportView(ViewSet):
    renderer_classes = [HitasJSONRenderer, ExcelRenderer]

    def list(self, request: Request, *args, **kwargs) -> HttpResponse:
        serializer = SalesReportSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        start: datetime.date = serializer.validated_data["start_date"]
        end: datetime.date = serializer.validated_data["end_date"]
        sales_filter = serializer.validated_data["filter"]

        sales = find_sales_on_interval_for_reporting(start, end, sales_filter)
        workbook = build_sales_by_postal_code_and_area_report_excel(sales)
        if sales_filter == "all":
            filename = "Kaikki kaupat postinumeroittain ja alueittain"
        elif sales_filter == "resale":
            filename = "Jälleenmyynnit postinumeroittain ja alueittain"
        elif sales_filter == "firstsale":
            filename = "Uudiskohteet postinumeroittain ja alueittain"
        filename += f" {start.isoformat()} - {end.isoformat()}.xlsx"
        return get_excel_response(filename=filename, excel=workbook)


class RegulatedOwnershipsReportView(ViewSet):
    renderer_classes = [HitasJSONRenderer, ExcelRenderer]

    def list(self, request: Request, *args, **kwargs) -> HttpResponse:
        ownerships = find_regulated_ownerships()
        workbook = build_regulated_ownerships_report_excel(ownerships)
        filename = "Sääntelyn piirissä olevien asuntojen omistajat.xlsx"
        return get_excel_response(filename=filename, excel=workbook)


class MultipleOwnershipsReportView(ViewSet):
    renderer_classes = [HitasJSONRenderer, ExcelRenderer]

    def list(self, request: Request, *args, **kwargs) -> HttpResponse:
        ownerships = find_owners_with_multiple_ownerships()
        workbook = build_multiple_ownerships_report_excel(ownerships)
        filename = "Useamman sääntelyn piirissä olevan asunnon omistavat omistajat.xlsx"
        return get_excel_response(filename=filename, excel=workbook)


class OwnershipsByHousingCompanyReportSerializer(serializers.ModelSerializer):
    owner_id = serializers.SerializerMethodField()
    number = serializers.IntegerField(source="sale.apartment.apartment_number")
    surface_area = HitasDecimalField(source="sale.apartment.surface_area")
    share_numbers = serializers.SerializerMethodField()
    purchase_date = serializers.DateField(source="sale.purchase_date")
    owner_name = serializers.SerializerMethodField()
    owner_ssn = serializers.SerializerMethodField()

    class Meta:
        model = Ownership
        fields = ("owner_id", "number", "surface_area", "share_numbers", "purchase_date", "owner_name", "owner_ssn")

    def get_owner_id(self, obj):
        return obj.owner.uuid.hex

    def get_share_numbers(self, obj):
        return f"{obj.sale.apartment.share_number_start}-{obj.sale.apartment.share_number_end}"

    def get_owner_name(self, obj):
        return Owner.OBFUSCATED_OWNER_NAME if obj.owner.non_disclosure else obj.owner.name

    def get_owner_ssn(self, obj):
        return "" if obj.owner.non_disclosure else obj.owner.identifier


class OwnershipsByCompanyJSONReportView(ViewSet):
    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        housing_company_obj: HousingCompany = lookup_model_by_uuid(kwargs.get("pk"), HousingCompany)

        serializer = OwnershipsByHousingCompanyReportSerializer(
            data=find_apartments_by_housing_company(housing_company_obj.id), many=True
        )
        serializer.is_valid()
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class OwnershipsByHousingCompanyReport(ViewSet):
    renderer_classes = [HitasJSONRenderer, ExcelRenderer]

    def retrieve(self, request: Request, *args, **kwargs) -> HttpResponse:
        housing_company_obj: HousingCompany = lookup_model_by_uuid(kwargs.get("pk"), HousingCompany)
        owners_by_companies = find_apartments_by_housing_company(housing_company_obj.id)
        workbook = build_owners_by_housing_companies_report_excel(owners_by_companies)
        filename = f"Omistajat yhtiölle {housing_company_obj.display_name}.xlsx"
        return get_excel_response(filename=filename, excel=workbook)
