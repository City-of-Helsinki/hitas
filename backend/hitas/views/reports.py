import datetime
from typing import Any

from django.http import HttpResponse
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from hitas.models import HousingCompany, Owner
from hitas.services.apartment_sale import find_sales_on_interval_for_reporting
from hitas.services.housing_company import (
    find_housing_companies_for_state_reporting,
    find_regulated_housing_companies_for_reporting,
    find_unregulated_housing_companies_for_reporting,
)
from hitas.services.owner import find_apartments_by_housing_company, find_owners_with_multiple_ownerships
from hitas.services.reports import (
    build_housing_company_state_report_excel,
    build_multiple_ownerships_report_excel,
    build_owners_by_housing_companies_report_excel,
    build_regulated_housing_companies_report_excel,
    build_sales_by_postal_code_and_area_report_excel,
    build_sales_report_excel,
    build_unregulated_housing_companies_report_excel,
    sort_housing_companies_by_state,
)
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


class RegulateHousingCompaniesReportView(ViewSet):
    renderer_classes = [HitasJSONRenderer, ExcelRenderer]

    def list(self, request: Request, *args, **kwargs) -> HttpResponse:
        housing_companies = find_regulated_housing_companies_for_reporting()
        workbook = build_regulated_housing_companies_report_excel(housing_companies)
        filename = "Valvonnan piirissä olevat yhtiöt.xlsx"
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

        sales = find_sales_on_interval_for_reporting(start, end)
        workbook = build_sales_by_postal_code_and_area_report_excel(sales)
        filename = f"Yhtiöt postinumero ja kalleusalueittain aikavälillä {start.isoformat()} - {end.isoformat()}.xlsx"
        return get_excel_response(filename=filename, excel=workbook)


class MultipleOwnershipsReportView(ViewSet):
    renderer_classes = [HitasJSONRenderer, ExcelRenderer]

    def list(self, request: Request, *args, **kwargs) -> HttpResponse:
        ownerships = find_owners_with_multiple_ownerships()
        workbook = build_multiple_ownerships_report_excel(ownerships)
        filename = "Useamman sääntelyn piirissä olevan asunnon omistavat omistajat.xlsx"
        return get_excel_response(filename=filename, excel=workbook)


class OwnershipsByCompanyJSONReportView(ViewSet):
    NON_DISCLOSURE_NAME = "xxx"

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        data = [
            {
                "number": d.apartment_number,
                "surface_area": d.apartment_surface_area,
                "share_numbers": f"{d.apartment_share_number_start}-{d.apartment_share_number_end}",
                "purchase_date": d.sale_purchase_date,
                "owner_name": self._get_owner_name(d.owner),
                "owner_ssn": self._get_ssn(d.owner),
            }
            for d in find_apartments_by_housing_company(kwargs.get("pk"))
        ]

        return Response(data=data, status=status.HTTP_200_OK)

    def _get_owner_name(self, owner: Owner) -> str:
        return self.NON_DISCLOSURE_NAME if owner.non_disclosure else owner.name

    def _get_ssn(self, owner: Owner) -> str:
        return "" if owner.non_disclosure else owner.identifier


class OwnershipsByHousingCompanyReport(ViewSet):
    renderer_classes = [HitasJSONRenderer, ExcelRenderer]

    def retrieve(self, request: Request, *args, **kwargs) -> HttpResponse:
        housing_company_id = kwargs.get("pk")
        owners_by_companies = find_apartments_by_housing_company(housing_company_id)
        workbook = build_owners_by_housing_companies_report_excel(owners_by_companies)
        housing_company_name = HousingCompany.objects.get(id=housing_company_id).display_name
        filename = f"Omistajat yhtiölle {housing_company_name}.xlsx"
        return get_excel_response(filename=filename, excel=workbook)
