from rest_framework import serializers

from hitas.models.codes import AbstractCode, BuildingType, Developer, FinancingMethod
from hitas.views.helpers import value_or_none


class AbstractCodeSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()

    def get_description(self, obj: AbstractCode) -> str:
        return value_or_none(obj.description)

    def get_code(self, obj: AbstractCode) -> str:
        return obj.legacy_code_number

    class Meta:
        model = AbstractCode
        fields = ["value", "description", "code"]
        abstract = True


class BuildingTypeSerializer(AbstractCodeSerializer):
    class Meta(AbstractCodeSerializer.Meta):
        model = BuildingType


class FinancingMethodSerializer(AbstractCodeSerializer):
    class Meta(AbstractCodeSerializer.Meta):
        model = FinancingMethod


class DeveloperSerializer(AbstractCodeSerializer):
    class Meta(AbstractCodeSerializer.Meta):
        model = Developer
