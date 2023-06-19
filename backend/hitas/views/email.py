from typing import Any

from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ViewSet

from hitas.services.email import (
    send_confirmed_max_price_calculation_email,
    send_regulation_letter_email,
    send_unconfirmed_max_price_calculation_email,
)
from hitas.utils import hitas_calculation_quarter
from hitas.views.utils import UUIDField


class ConfirmedMaxPriceCalculationEmailSerializer(Serializer):
    calculation_id = UUIDField()
    request_date = serializers.DateField()
    template_name = serializers.CharField(max_length=256)
    recipients = serializers.ListField(child=serializers.EmailField(), min_length=1)


class UnconfirmedMaxPriceCalculationEmailSerializer(Serializer):
    apartment_id = UUIDField()
    calculation_date = serializers.DateField(default=lambda: timezone.now().date())
    request_date = serializers.DateField()
    additional_info = serializers.CharField(allow_blank=True)
    template_name = serializers.CharField(max_length=256)
    recipients = serializers.ListField(child=serializers.EmailField(), min_length=1)


class RegulationLetterEmailSerializer(Serializer):
    housing_company_id = UUIDField()
    calculation_date = serializers.DateField(default=lambda: hitas_calculation_quarter(timezone.now().date()))
    template_name = serializers.CharField(max_length=256)
    recipients = serializers.ListField(child=serializers.EmailField(), min_length=1)


class ConfirmedMaxPriceCalculationEmailViewSet(ViewSet):
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = ConfirmedMaxPriceCalculationEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        send_confirmed_max_price_calculation_email(
            calculation_id=data["calculation_id"],
            request_date=data["request_date"],
            template_name=data["template_name"],
            recipients=data["recipients"],
            user=request.user,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class UnconfirmedMaxPriceCalculationEmailViewSet(ViewSet):
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = UnconfirmedMaxPriceCalculationEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        send_unconfirmed_max_price_calculation_email(
            apartment_id=data["apartment_id"],
            calculation_date=data["calculation_date"],
            request_date=data["request_date"],
            additional_info=data["additional_info"],
            template_name=data["template_name"],
            recipients=data["recipients"],
            user=request.user,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegulationLetterEmailViewSet(ViewSet):
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = RegulationLetterEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        send_regulation_letter_email(
            housing_company_id=data["housing_company_id"],
            calculation_date=data["calculation_date"],
            template_name=data["template_name"],
            recipients=data["recipients"],
            user=request.user,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
