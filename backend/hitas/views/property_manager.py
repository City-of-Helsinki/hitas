from uuid import UUID

from rest_framework import serializers

from hitas.exceptions import HitasModelNotFound
from hitas.models import PropertyManager
from hitas.views.helpers import AddressSerializer


class PropertyManagerSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    address = AddressSerializer(source="*")

    def get_id(self, obj: PropertyManager) -> str:
        return obj.uuid.hex

    class Meta:
        model = PropertyManager
        fields = [
            "id",
            "address",
            "name",
            "email",
        ]

    def to_internal_value(self, data):
        try:
            return self.Meta.model.objects.get(uuid=UUID(hex=str(data)))
        except (self.Meta.model.DoesNotExist, ValueError):
            raise HitasModelNotFound(model=self.Meta.model)
