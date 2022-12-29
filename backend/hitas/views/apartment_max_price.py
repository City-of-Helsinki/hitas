import datetime
from http import HTTPStatus
from typing import Any, Optional, Tuple

from django.utils import timezone
from rest_framework import fields
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ViewSet

from hitas.calculations.exceptions import IndexMissingException, InvalidCalculationResultException
from hitas.calculations.max_prices import create_max_price_calculation
from hitas.exceptions import HitasModelNotFound
from hitas.models import Apartment, HousingCompany
from hitas.models.apartment import ApartmentMaximumPriceCalculation


class ApartmentMaximumPriceViewSet(CreateModelMixin, RetrieveModelMixin, ViewSet):
    def create(self, request, *args, **kwargs):
        serializer = CreateCalculationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        calculation_date = serializer.validated_data.get("calculation_date") or timezone.now().date()
        apartment_share_of_housing_company_loans = (
            serializer.validated_data.get("apartment_share_of_housing_company_loans") or 0
        )
        apartment_share_of_housing_company_loans_date = (
            serializer.validated_data.get("apartment_share_of_housing_company_loans_date") or timezone.now().date()
        )

        # Calculate max price
        try:
            max_prices = create_max_price_calculation(
                housing_company_uuid=kwargs["housing_company_uuid"],
                apartment_uuid=kwargs["apartment_uuid"],
                calculation_date=calculation_date,
                apartment_share_of_housing_company_loans=apartment_share_of_housing_company_loans,
                apartment_share_of_housing_company_loans_date=apartment_share_of_housing_company_loans_date,
                additional_info=serializer.validated_data.get("additional_info", ""),
            )
            return Response(max_prices)
        except InvalidCalculationResultException:
            return Response(
                {
                    "error": "invalid_calculation_result",
                    "message": "Maximum price calculation could not be completed.",
                    "reason": "Conflict",
                    "status": 409,
                },
                status=HTTPStatus.CONFLICT,
            )
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

    def retrieve(self, request, *args, **kwargs):
        # Verify housing company and apartment exists (so we can raise an appropriate error)
        hc_id, apartment_id = self.verify_housing_company_and_apartment(kwargs)

        # Try to fetch the maximum price calculation
        with model_or_404(ApartmentMaximumPriceCalculation):
            mpc = ApartmentMaximumPriceCalculation.objects.only(
                "json_version", "json", "confirmed_at", "apartment_id"
            ).get(
                apartment_id=apartment_id,
                uuid=kwargs["pk"],
                json_version=ApartmentMaximumPriceCalculation.CURRENT_JSON_VERSION,
            )
            if mpc.json_version is None:
                raise HitasModelNotFound(model=ApartmentMaximumPriceCalculation)

            return self.response(mpc)

    def update(self, request, *args, **kwargs):
        serializer = ConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        confirm = serializer.data["confirm"]

        # Verify housing company and apartment exists (so we can raise an appropriate error)
        hc_id, apartment_id = self.verify_housing_company_and_apartment(kwargs)

        # Try to fetch the maximum price calculation
        with model_or_404(ApartmentMaximumPriceCalculation):
            ampc = ApartmentMaximumPriceCalculation.objects.only(
                "json_version", "json", "confirmed_at", "apartment_id"
            ).get(
                apartment_id=apartment_id,
                uuid=kwargs["pk"],
                json_version=ApartmentMaximumPriceCalculation.CURRENT_JSON_VERSION,
            )

            if ampc.json_version is None:
                raise HitasModelNotFound(model=ApartmentMaximumPriceCalculation)

        # Check calculation is not yet confirmed
        if ampc.confirmed_at is not None:
            return Response(
                {
                    "error": "already_confirmed",
                    "message": "Maximum price calculation has already been confirmed.",
                    "reason": "Conflict",
                    "status": 409,
                },
                status=HTTPStatus.CONFLICT,
            )

        if confirm:
            # Confirm the calculation by marking the `confirmed_at` to current timestamp and making it the latest
            # confirmed calculation
            ampc.confirmed_at = timezone.now()
            ampc.save()

            # Delete other unconfirmed calculations for this apartment
            ApartmentMaximumPriceCalculation.objects.filter(
                apartment_id=apartment_id, confirmed_at__isnull=True
            ).delete()

            return self.response(ampc)
        else:
            # In case the user wanted not to confirm we will delete the calculation
            ampc.delete()
            return Response(status=HTTPStatus.NO_CONTENT)

    @staticmethod
    def verify_housing_company_and_apartment(kwargs: dict[str, Any]) -> Tuple[int, int]:
        # Verify housing company and apartment exists (so we can raise an appropriate error)
        with model_or_404(HousingCompany):
            hc_id = HousingCompany.objects.only("id").get(uuid=kwargs["housing_company_uuid"])
        with model_or_404(Apartment):
            apartment_id = Apartment.objects.only("pk").get(
                uuid=kwargs["apartment_uuid"], building__real_estate__housing_company_id=hc_id
            )
        return hc_id, apartment_id

    @staticmethod
    def response(ampc):
        retval = ampc.json
        retval["confirmed_at"] = ampc.confirmed_at
        return Response(retval)


class ConfirmSerializer(Serializer):
    confirm = fields.BooleanField(required=True)


class CreateCalculationSerializer(Serializer):
    calculation_date = fields.DateField(required=False, allow_null=True)
    apartment_share_of_housing_company_loans = fields.IntegerField(allow_null=True, required=False, min_value=0)
    apartment_share_of_housing_company_loans_date = fields.DateField(required=False, allow_null=True)
    additional_info = fields.CharField(required=False, allow_null=True, allow_blank=True)

    def validate_calculation_date(self, date):
        return self._validate_not_in_future(date)

    @staticmethod
    def _validate_not_in_future(date: datetime.date) -> Optional[datetime.date]:
        if date is not None and date > timezone.now().date():
            raise ValidationError("Field has to be less than or equal to current date.")
        return date


def model_or_404(model_class):
    return ModelDoesNotExistContextManager(model_class)


class ModelDoesNotExistContextManager:
    def __init__(self, model_class):
        self.model_class = model_class

    def __enter__(self):
        return self.model_class.objects

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(exc_val, self.model_class.DoesNotExist):
            raise HitasModelNotFound(model=self.model_class)
