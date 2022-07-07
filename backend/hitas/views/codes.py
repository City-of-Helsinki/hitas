from uuid import UUID

from rest_framework import serializers

from hitas.exceptions import HitasModelNotFound
from hitas.models.codes import AbstractCode, BuildingType, Developer, FinancingMethod


class AbstractCodeSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    code = serializers.CharField(source="legacy_code_number")

    def get_id(self, obj: AbstractCode) -> str:
        return obj.uuid.hex

    def to_internal_value(self, data):
        try:
            return self.Meta.model.objects.get(uuid=UUID(hex=str(data)))
        except (self.Meta.model.DoesNotExist, ValueError):
            raise HitasModelNotFound(model=self.Meta.model)

    class Meta:
        model = AbstractCode
        fields = ["id", "value", "description", "code"]
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
