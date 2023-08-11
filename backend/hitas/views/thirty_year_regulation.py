from typing import Optional
from uuid import UUID

from dateutil.relativedelta import relativedelta
from django.http import HttpResponse
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from hitas.exceptions import ModelConflict
from hitas.models import PDFBody
from hitas.models.pdf_body import PDFBodyName
from hitas.models.thirty_year_regulation import RegulationResult, ReplacementPostalCodes
from hitas.services.thirty_year_regulation import (
    PostalCodeT,
    build_thirty_year_regulation_report_excel,
    combine_sales_data,
    compile_postal_codes_with_cost_areas,
    convert_thirty_year_regulation_results_to_comparison_data,
    get_external_sales_data,
    get_sales_data,
    get_thirty_year_regulation_results,
    get_thirty_year_regulation_results_for_housing_company,
    perform_thirty_year_regulation,
)
from hitas.services.validation import validate_postal_code
from hitas.utils import business_quarter, from_iso_format_or_today_if_none, hitas_calculation_quarter, to_quarter
from hitas.views.utils.excel import get_excel_response
from hitas.views.utils.pdf import get_pdf_response


class ReplacementPostalCodeSerializer(serializers.Serializer):
    postal_code = serializers.CharField(max_length=5, min_length=5)
    replacements = serializers.ListField(
        child=serializers.CharField(max_length=5, min_length=5),
        min_length=2,
        max_length=2,
    )

    @staticmethod
    def validate_postal_code(value: str) -> str:
        return validate_postal_code(value)

    @staticmethod
    def validate_replacement_postal_codes(value: list[str]) -> list[str]:
        errors: list[ValidationError] = []
        for postal_code in value:
            try:
                validate_postal_code(postal_code)
            except ValidationError as error:
                errors += error

        if errors:
            raise ValidationError(errors)

        return value


class ThirtyYearRegulationView(ViewSet):
    def list(self, request: Request, *args, **kwargs) -> Response:
        try:
            calculation_date = from_iso_format_or_today_if_none(request.query_params.get("calculation_date"))
        except ValueError as error:
            raise ValidationError({"calculation_date": str(error)}) from error

        data = get_thirty_year_regulation_results(calculation_date)
        results = convert_thirty_year_regulation_results_to_comparison_data(data)

        return Response(data=results, status=status.HTTP_200_OK)

    def create(self, request: Request, *args, **kwargs) -> Response:
        try:
            calculation_date = from_iso_format_or_today_if_none(request.data.get("calculation_date"))
        except ValueError as error:
            raise ValidationError({"calculation_date": str(error)}) from error

        replacement_postal_codes: list[ReplacementPostalCodes] = request.data.get("replacement_postal_codes", [])
        if replacement_postal_codes:
            ReplacementPostalCodeSerializer(data=replacement_postal_codes, many=True).is_valid(raise_exception=True)

        replacements: dict[PostalCodeT, list[PostalCodeT]] = {
            replacement["postal_code"]: replacement["replacements"] for replacement in replacement_postal_codes
        }

        results = perform_thirty_year_regulation(calculation_date, replacements)
        return Response(data=results, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        url_path=r"reports/download-regulation-letter",
        url_name="letter",
    )
    def regulation_letter(self, request: Request, *args, **kwargs) -> HttpResponse:
        try:
            housing_company_uuid = UUID(hex=request.query_params.get("housing_company_id"))
        except ValueError as error:
            raise ValidationError({"housing_company_id": "Not a valid UUID."}) from error
        except TypeError as error:
            raise ValidationError({"housing_company_id": "This field is mandatory and cannot be null."}) from error

        try:
            calculation_date = from_iso_format_or_today_if_none(request.query_params.get("calculation_date"))
        except ValueError as error:
            raise ValidationError({"calculation_date": str(error)}) from error

        results = get_thirty_year_regulation_results_for_housing_company(housing_company_uuid, calculation_date)

        if results.regulation_result == RegulationResult.STAYS_REGULATED:
            choice = "jatkumisesta"
            body_parts: Optional[list[str]] = (
                PDFBody.objects.filter(name=PDFBodyName.STAYS_REGULATED).values_list("texts", flat=True).first()
            )
            if body_parts is None:
                raise ModelConflict("Missing regulated body template", error_code="missing")
        else:
            choice = "pättymisestä"
            body_parts: Optional[list[str]] = (
                PDFBody.objects.filter(name=PDFBodyName.RELEASED_FROM_REGULATION)
                .values_list("texts", flat=True)
                .first()
            )
            if body_parts is None:
                raise ModelConflict("Missing released body template", error_code="missing")

        context = {
            "results": results,
            "user": request.user,
            "body_parts": body_parts,
        }

        filename = f"Tiedote sääntelyn {choice} - {results.housing_company.display_name}.pdf"
        response = get_pdf_response(filename=filename, template="regulation_letter.jinja", context=context)

        if not results.letter_fetched:
            results.letter_fetched = True
            results.save(update_fields=["letter_fetched"])

        return response

    @action(
        methods=["GET"],
        detail=False,
        url_path=r"reports/download-regulation-results",
        url_name="results",
    )
    def regulation_results(self, request: Request, *args, **kwargs) -> HttpResponse:
        try:
            calculation_date = from_iso_format_or_today_if_none(request.query_params.get("calculation_date"))
        except ValueError as error:
            raise ValidationError({"calculation_date": str(error)}) from error

        results = get_thirty_year_regulation_results(calculation_date)
        workbook = build_thirty_year_regulation_report_excel(results)
        filename = f"30v vertailun tulokset ({results.calculation_month.isoformat()}).xlsx"
        return get_excel_response(filename=filename, excel=workbook)


class ThirtyYearRegulationPostalCodesView(ViewSet):
    def list(self, request: Request, *args, **kwargs) -> Response:
        try:
            calculation_date = from_iso_format_or_today_if_none(request.query_params.get("calculation_date"))
        except ValueError as error:
            raise ValidationError({"calculation_date": str(error)}) from error

        calculation_month = hitas_calculation_quarter(calculation_date)
        this_quarter = business_quarter(calculation_month)
        this_quarter_previous_year = this_quarter - relativedelta(years=1)

        sales_data = get_sales_data(this_quarter_previous_year, this_quarter)
        external_sales_data = get_external_sales_data(to_quarter(this_quarter))
        price_by_area = combine_sales_data(sales_data, external_sales_data)
        results = compile_postal_codes_with_cost_areas(price_by_area)

        return Response(data=results, status=status.HTTP_200_OK)
