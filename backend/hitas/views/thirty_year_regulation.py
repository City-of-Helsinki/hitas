from uuid import UUID

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from hitas.services.thirty_year_regulation import (
    get_thirty_year_regulation_results_for_housing_company,
    perform_thirty_year_regulation,
)
from hitas.utils import from_iso_format_or_today_if_none
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
        url_path=r"reports/regulation-continuation-letter",
        url_name="continuation-letter",
    )
    def regulation_continuation_letter(self, request: Request, *args, **kwargs) -> HttpResponse:
        try:
            housing_company_uuid = UUID(hex=request.query_params.get("housing_company_id"))
        except ValueError as error:
            raise ValidationError({"housing_company_id": "Not a valid UUID."}) from error
        except TypeError as error:
            raise ValidationError({"housing_company_id": "This field is mandatory and cannot be null."}) from error

        results = get_thirty_year_regulation_results_for_housing_company(housing_company_uuid)

        context = {"results": results}
        filename = f"Tiedote sääntelyn jatkumisesta - {results.housing_company.display_name}.pdf"
        return get_pdf_response(filename=filename, template="regulation_continuation_letter.jinja", context=context)
