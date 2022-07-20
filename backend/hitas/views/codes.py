from django_filters.rest_framework import filters
from rest_framework import serializers

from hitas.models.codes import AbstractCode, ApartmentType, BuildingType, Developer, FinancingMethod, PostalCode
from hitas.models.utils import validate_code_number
from hitas.views.utils import HitasFilterSet, HitasModelSerializer, HitasModelViewSet


class AbstractCodeSerializer(HitasModelSerializer):
    value = serializers.CharField()
    description = serializers.CharField()
    code = serializers.CharField(source="legacy_code_number")

    def validate_code(self, value):
        validate_code_number(value)
        return value

    class Meta:
        model = AbstractCode
        fields = ["id", "value", "description", "code"]
        read_only_fields = ["value"]
        abstract = True


class PostalCodeSerializer(AbstractCodeSerializer):
    class Meta(AbstractCodeSerializer.Meta):
        model = PostalCode


class BuildingTypeSerializer(AbstractCodeSerializer):
    class Meta(AbstractCodeSerializer.Meta):
        model = BuildingType


class FinancingMethodSerializer(AbstractCodeSerializer):
    class Meta(AbstractCodeSerializer.Meta):
        model = FinancingMethod


class DeveloperSerializer(AbstractCodeSerializer):
    class Meta(AbstractCodeSerializer.Meta):
        model = Developer


class ApartmentTypeSerializer(AbstractCodeSerializer):
    class Meta(AbstractCodeSerializer.Meta):
        model = ApartmentType


class AbstractCodeViewSet(HitasModelViewSet):
    def get_queryset(self):
        return self.model_class.objects.all()

    def get_filterset_class(self):
        class CodeFilterSet(HitasFilterSet):
            code = filters.CharFilter(field_name="legacy_code_number", lookup_expr="exact")

            class Meta:
                model = self.model_class
                fields = ["value", "description", "code"]

        CodeFilterSet.__name__ = f"{self.model_class}FilterSet"

        return CodeFilterSet


class PostalCodeViewSet(AbstractCodeViewSet):
    serializer_class = PostalCodeSerializer
    model_class = PostalCode


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
