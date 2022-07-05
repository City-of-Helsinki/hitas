from typing import Optional

from rest_framework import serializers

from hitas.models.codes import AbstractCode, BuildingType, Developer, FinancingMethod
from hitas.views.helpers import value_or_none


class AbstractCodeSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    code = serializers.CharField(source="legacy_code_number")

    def get_description(self, obj: AbstractCode) -> Optional[str]:
        return value_or_none(obj.description)

    def get_code(self, obj: AbstractCode) -> Optional[str]:
        return obj.legacy_code_number

    class Meta:
        model = AbstractCode
        fields = ["value", "description", "code"]
        read_only_fields = ["value"]
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
