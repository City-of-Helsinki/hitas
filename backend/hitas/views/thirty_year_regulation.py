from uuid import UUID

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from hitas.exceptions import ModelConflict
from hitas.models.thirty_year_regulation import RegulationResult
from hitas.services.thirty_year_regulation import (
    build_thirty_year_regulation_report_excel,
    get_thirty_year_regulation_results,
    get_thirty_year_regulation_results_for_housing_company,
    perform_thirty_year_regulation,
)
from hitas.utils import from_iso_format_or_today_if_none
from hitas.views.utils.excel import get_excel_response
from hitas.views.utils.pdf import get_pdf_response


class ThirtyYearRegulationView(ViewSet):
    def list(self, request: Request, *args, **kwargs) -> Response:
        try:
            calculation_date = from_iso_format_or_today_if_none(request.query_params.get("calculation_date"))
        except ValueError as error:
            raise ValidationError({"calculation_date": str(error)}) from error

        results = perform_thirty_year_regulation(calculation_date)
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

        if results.regulation_result == RegulationResult.SKIPPED:
            raise ModelConflict(
                "Cannot download PDF since regulation for this housing company was skipped.",
                error_code="invalid",
            )

        context = {"results": results}
        choice = "jatkumisesta" if results.regulation_result == RegulationResult.STAYS_REGULATED else "pättymisestä"
        filename = f"Tiedote sääntelyn {choice} - {results.housing_company.display_name}.pdf"
        return get_pdf_response(filename=filename, template="regulation_letter.jinja", context=context)

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
