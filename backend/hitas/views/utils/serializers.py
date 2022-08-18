from uuid import UUID

from rest_framework import serializers

from hitas.exceptions import HitasModelNotFound
from hitas.models._base import ExternalHitasModel
from hitas.views.utils import PostalCodeField


class HitasModelSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    def get_id(self, instance: ExternalHitasModel) -> str:
        return instance.uuid.hex

    def to_internal_value(self, data):
        """If referenced in another serializer by id, return an object"""
        if not self.instance and data.get("id", None) is not None:
            try:
                return self.Meta.model.objects.get(uuid=UUID(hex=str(data.get("id", None))))
            except (self.Meta.model.DoesNotExist, ValueError):
                raise HitasModelNotFound(model=self.Meta.model)
        return super().to_internal_value(data)

    class Meta:
        model = None


class AddressSerializer(serializers.Serializer):
    street_address = serializers.CharField()
    postal_code = PostalCodeField()
    city = serializers.CharField(read_only=True)
