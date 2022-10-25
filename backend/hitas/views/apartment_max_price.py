import datetime
from http import HTTPStatus

from rest_framework import serializers
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from hitas.calculations import calculate_max_price
from hitas.calculations.max_price import IndexMissingException


class ApartmentMaxPriceViewSet(ListModelMixin, ViewSet):
    def list(self, request, *args, **kwargs):
        # Validate calculation date
        calculation_date = request.query_params.get("calculation_date")
        if calculation_date is not None:
            try:
                # Parse calculation date
                calculation_date = datetime.date.fromisoformat(calculation_date)

                # Calculation date cannot be in the future
                if calculation_date > datetime.date.today():
                    self._validation_error("calculation_date", "Field has to be less than or equal to current date.")
            except ValueError:
                self._validation_error("calculation_date", "Field has to be a valid date in format 'yyyy-mm-dd'.")

        # Validate apartment share of housing company loans
        apartment_share_of_housing_company_loans = request.query_params.get(
            "apartment_share_housing_company_loans", "0"
        )
        try:
            # Parse apartment share of housing company loans
            apartment_share_of_housing_company_loans = int(apartment_share_of_housing_company_loans)

            # apartment share of housing company loans cannot be a negative number
            if apartment_share_of_housing_company_loans < 0:
                self._validation_error(
                    "apartment_share_housing_company_loans", "Ensure this value is greater than or equal to 0."
                )
        except ValueError:
            self._validation_error("apartment_share_housing_company_loans", "A valid number is required.")

        # Calculate max price
        try:
            max_prices = calculate_max_price(
                housing_company_uuid=kwargs["housing_company_uuid"],
                apartment_uuid=kwargs["apartment_uuid"],
                calculation_date=calculation_date,
                apartment_share_of_housing_company_loans=apartment_share_of_housing_company_loans,
            )
            return Response(max_prices)
        except IndexMissingException:
            return Response(
                {
                    "error": "index_missing",
                    "message": "One or more indices required for max price calculation is missing.",
                    "reason": "Conflict",
                    "status": 409,
                },
                status=HTTPStatus.CONFLICT,
            )

    @staticmethod
    def _validation_error(field, details):
        raise serializers.ValidationError({field: details})
