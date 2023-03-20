from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from hitas.services.thirty_year_regulation import perform_thirty_year_regulation
from hitas.utils import from_iso_format_or_today_if_none


class ThirtyYearRegulationView(ViewSet):
    def list(self, request: Request, *args, **kwargs) -> Response:
        try:
            calculation_date = from_iso_format_or_today_if_none(request.query_params.get("calculation_date"))
        except ValueError as error:
            raise ValidationError({"calculation_date": str(error)}) from error

        results = perform_thirty_year_regulation(calculation_date)
        return Response(data=results, status=status.HTTP_200_OK)
