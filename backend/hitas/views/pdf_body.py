from typing import Any

from enumfields.drf import EnumSupportSerializerMixin
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from hitas.models import PDFBody
from hitas.models.pdf_body import PDFBodyName
from hitas.views.utils import HitasModelViewSet


class PDFBodySerializer(EnumSupportSerializerMixin, ModelSerializer):
    def create(self, validated_data: dict[str, Any]) -> PDFBody:
        self.validate_text_lengths(validated_data)
        return super().create(validated_data)

    def update(self, instance: PDFBody, validated_data: dict[str, Any]) -> PDFBody:
        self.validate_text_lengths(validated_data)
        return super().update(instance, validated_data)

    @staticmethod
    def validate_text_lengths(validated_data: dict[str, Any]) -> None:
        if (
            validated_data["name"] == PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION
            and len(validated_data["texts"]) != 3
        ):
            raise ValidationError({"texts": "Unconfirmed max price calculation must have exactly 3 body texts."})
        elif (
            validated_data["name"] == PDFBodyName.CONFIRMED_MAX_PRICE_CALCULATION and len(validated_data["texts"]) != 1
        ):
            raise ValidationError({"texts": "Confirmed max price calculation must have exactly 1 body text."})
        elif validated_data["name"] == PDFBodyName.STAYS_REGULATED and len(validated_data["texts"]) != 3:
            raise ValidationError({"texts": "Regulation continuation letter must have exactly 3 body texts."})
        elif validated_data["name"] == PDFBodyName.RELEASED_FROM_REGULATION and len(validated_data["texts"]) != 1:
            raise ValidationError({"texts": "Regulation release letter must have exactly 1 body text."})

    class Meta:
        model = PDFBody
        fields = [
            "name",
            "texts",
        ]


class PDFBodyViewSet(HitasModelViewSet):
    model_class = PDFBody
    serializer_class = PDFBodySerializer
    lookup_field = "name"

    def get_queryset(self):
        return super().get_queryset().order_by("pk")
