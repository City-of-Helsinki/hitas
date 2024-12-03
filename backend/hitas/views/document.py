from django.shortcuts import redirect
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser

from hitas.models.apartment import Apartment
from hitas.models.document import AparmentDocument, HousingCompanyDocument
from hitas.models.housing_company import HousingCompany
from hitas.services.validation import lookup_model_id_by_uuid
from hitas.views.utils import HitasModelSerializer, HitasModelViewSet


class DocumentSerializerBase(HitasModelSerializer):
    file_content = serializers.FileField(source="file", write_only=True, required=False)
    file_link = serializers.SerializerMethodField()
    file_type_display = serializers.SerializerMethodField()

    class Meta:
        fields = [
            "id",
            "created_at",
            "modified_at",
            "display_name",
            "file_content",
            "file_link",
            "file_type_display",
        ]

    def get_file_link(self, obj):
        return obj.get_file_link()

    def get_file_type_display(self, obj):
        if not obj.original_filename:
            return None
        file_extension = obj.original_filename.split(".")[-1]
        return f"{file_extension.upper()}-tiedosto"

    def create(self, validated_data):
        file = validated_data.get("file")
        if file:
            validated_data["original_filename"] = file.name
        return super().create(validated_data)

    def update(self, instance, validated_data):
        file = validated_data.get("file")
        if file:
            validated_data["original_filename"] = file.name
        return super().update(instance, validated_data)


class HousingCompanyDocumentSerializer(DocumentSerializerBase):
    class Meta(DocumentSerializerBase.Meta):
        model = HousingCompanyDocument


class AparmentDocumentSerializer(DocumentSerializerBase):
    class Meta(DocumentSerializerBase.Meta):
        model = AparmentDocument


class DocumentViewSetBase(HitasModelViewSet):
    parser_classes = [JSONParser, MultiPartParser]

    def get_queryset(self):
        return super().get_queryset()

    def perform_update(self, serializer):
        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        return super().perform_destroy(instance)

    @action(detail=True, methods=["GET"])
    def redirect(self, request, **kwargs):
        obj = self.get_object()
        return redirect(obj.file.url)


class HousingCompanyDocumentViewSet(DocumentViewSetBase):
    serializer_class = HousingCompanyDocumentSerializer
    model_class = HousingCompanyDocument

    def get_queryset(self):
        housingcompany_id = lookup_model_id_by_uuid(self.kwargs["housing_company_uuid"], HousingCompany)
        return super().get_queryset().filter(housing_company_id=housingcompany_id).order_by("pk")

    def perform_create(self, serializer):
        housingcompany_id = lookup_model_id_by_uuid(self.kwargs["housing_company_uuid"], HousingCompany)
        serializer.save(housing_company_id=housingcompany_id)


class ApartmentDocumentViewSet(DocumentViewSetBase):
    serializer_class = AparmentDocumentSerializer
    model_class = AparmentDocument

    def get_queryset(self):
        apartment_id = lookup_model_id_by_uuid(self.kwargs["apartment_uuid"], Apartment)
        return super().get_queryset().filter(apartment_id=apartment_id).order_by("pk")

    def perform_create(self, serializer):
        apartment_id = lookup_model_id_by_uuid(self.kwargs["apartment_uuid"], Apartment)
        serializer.save(apartment_id=apartment_id)
