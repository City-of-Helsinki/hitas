from rest_framework import serializers

from hitas.models._base import ExternalHitasModel
from hitas.views.utils import PostalCodeField


class HitasModelSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    def get_id(self, instance: ExternalHitasModel) -> str:
        return instance.uuid.hex


class AddressSerializer(serializers.Serializer):
    street = serializers.CharField(source="street_address")
    postal_code = PostalCodeField()
    city = serializers.CharField(read_only=True)
