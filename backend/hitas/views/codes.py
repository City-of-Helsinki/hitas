from rest_framework import serializers

from hitas.models.codes import AbstractCode, BuildingType, Developer, FinancingMethod
from hitas.views.helpers import ValueOrNullField


class AbstractCodeSerializer(serializers.ModelSerializer):
    description = ValueOrNullField()
    code = serializers.CharField(source="legacy_code_number")

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
