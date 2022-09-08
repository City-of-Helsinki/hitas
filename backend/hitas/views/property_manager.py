import uuid

from rest_framework import serializers

from hitas.models import PropertyManager
from hitas.views.utils import HitasModelSerializer, HitasModelViewSet, UUIDRelatedField


class PropertyManagerAddressSerializer(HitasModelSerializer):
    class Meta:
        model = PropertyManager
        fields = ["street_address", "postal_code", "city"]


class PropertyManagerSerializer(HitasModelSerializer):
    address = PropertyManagerAddressSerializer(source="*")

    class Meta:
        model = PropertyManager
        fields = [
            "id",
            "name",
            "email",
            "address",
        ]


class ReadOnlyPropertyManagerSerializer(serializers.Serializer):
    id = UUIDRelatedField(queryset=PropertyManager.objects, source="uuid")
    name = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    address = PropertyManagerAddressSerializer(source="*", read_only=True)

    def to_internal_value(self, data):
        super().to_internal_value(data)

        try:
            return PropertyManager.objects.only("id").get(uuid=uuid.UUID(hex=data["id"]))
        except (PropertyManager.DoesNotExist, ValueError, TypeError):
            return {}

    class Meta:
        fields = ["id", "name", "email", "address"]


class PropertyManagerViewSet(HitasModelViewSet):
    serializer_class = PropertyManagerSerializer
    model_class = PropertyManager

    def get_queryset(self):
        return PropertyManager.objects.all().order_by("id")
