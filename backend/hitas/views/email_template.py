from typing import Any

from enumfields.drf import EnumSupportSerializerMixin
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from rest_framework.settings import api_settings

from hitas.models import EmailTemplate
from hitas.models.email_template import EmailTemplateType
from hitas.views.utils import HitasModelViewSet


class EmailTemplateSerializer(EnumSupportSerializerMixin, ModelSerializer):
    type = serializers.SerializerMethodField()

    def get_type(self, *args, **kwargs) -> str:
        return self.context["view"].get_template_type()

    class Meta:
        model = EmailTemplate
        fields = [
            "name",
            "type",
            "text",
        ]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        attrs["type"] = self.get_type()
        return attrs

    def create(self, validated_data: dict[str, Any]) -> None:
        if EmailTemplate.objects.filter(name=validated_data["name"], type=validated_data["type"]).exists():
            raise ValidationError(
                {api_settings.NON_FIELD_ERRORS_KEY: "Email template with this type and name already exists."},
            )
        return super().create(validated_data)


class EmailTemplateViewSet(HitasModelViewSet):
    model_class = EmailTemplate
    serializer_class = EmailTemplateSerializer
    lookup_field = "name"

    def get_default_queryset(self):
        template_type = self.get_template_type()
        return EmailTemplate.objects.filter(type=template_type).all().order_by("pk")

    def get_template_type(self) -> str:
        try:
            return EmailTemplateType(self.kwargs["type"]).value
        except ValueError:
            raise ValidationError({"type": "Invalid template type."})
