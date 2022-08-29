from django_filters.rest_framework import filters
from rest_framework import serializers

from hitas.models.codes import AbstractCode, ApartmentType, BuildingType, Developer, FinancingMethod
from hitas.views.utils import HitasFilterSet, HitasModelSerializer, HitasModelViewSet, UUIDField


class AbstractCodeSerializer(HitasModelSerializer):
    value = serializers.CharField()
    description = serializers.CharField()
    code = serializers.CharField(source="legacy_code_number")

    class Meta:
        model = AbstractCode
        fields = ["id", "value", "description", "code"]
        read_only_fields = ["value"]
        abstract = True


class AbstractReadOnlyCodeSerializer(HitasModelSerializer):
    id = UUIDField(source="uuid")
    value = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    code = serializers.CharField(source="legacy_code_number", read_only=True)

    class Meta:
        model = AbstractCode
        fields = ["id", "value", "description", "code"]
        abstract = True


class BuildingTypeSerializer(AbstractCodeSerializer):
    class Meta(AbstractCodeSerializer.Meta):
        model = BuildingType


class ReadOnlyBuildingTypeSerializer(AbstractReadOnlyCodeSerializer):
    class Meta(AbstractReadOnlyCodeSerializer.Meta):
        model = BuildingType


class FinancingMethodSerializer(AbstractCodeSerializer):
    class Meta(AbstractCodeSerializer.Meta):
        model = FinancingMethod


class ReadOnlyFinancingMethodSerializer(AbstractReadOnlyCodeSerializer):
    class Meta(AbstractReadOnlyCodeSerializer.Meta):
        model = FinancingMethod


class DeveloperSerializer(AbstractCodeSerializer):
    class Meta(AbstractCodeSerializer.Meta):
        model = Developer


class ReadOnlyDeveloperSerializer(AbstractReadOnlyCodeSerializer):
    class Meta(AbstractReadOnlyCodeSerializer.Meta):
        model = Developer


class ApartmentTypeSerializer(AbstractCodeSerializer):
    class Meta(AbstractCodeSerializer.Meta):
        model = ApartmentType


class AbstractCodeViewSet(HitasModelViewSet):
    def get_queryset(self):
        return self.model_class.objects.all().order_by("id")

    def get_filterset_class(self):
        class CodeFilterSet(HitasFilterSet):
            code = filters.CharFilter(field_name="legacy_code_number", lookup_expr="exact")

            class Meta:
                model = self.model_class
                fields = ["value", "description", "code"]

        CodeFilterSet.__name__ = f"{self.model_class}FilterSet"

        return CodeFilterSet


class BuildingTypeViewSet(AbstractCodeViewSet):
    serializer_class = BuildingTypeSerializer
    model_class = BuildingType


class FinancingMethodViewSet(AbstractCodeViewSet):
    serializer_class = FinancingMethodSerializer
    model_class = FinancingMethod


class DeveloperViewSet(AbstractCodeViewSet):
    serializer_class = DeveloperSerializer
    model_class = Developer


class ApartmentTypeViewSet(AbstractCodeViewSet):
    serializer_class = ApartmentTypeSerializer
    model_class = ApartmentType
