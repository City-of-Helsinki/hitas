import uuid
from typing import Any

from rest_framework import serializers

from hitas.models import PropertyManager
from hitas.views.utils import HitasCharFilter, HitasFilterSet, HitasModelSerializer, HitasModelViewSet, UUIDRelatedField


class PropertyManagerFilterSet(HitasFilterSet):
    name = HitasCharFilter(lookup_expr="icontains")

    class Meta:
        model = PropertyManager
        fields = [
            "name",
        ]


class PropertyManagerSerializer(HitasModelSerializer):
    class Meta:
        model = PropertyManager
        fields = [
            "id",
            "name",
            "email",
        ]


class ReadOnlyPropertyManagerSerializer(serializers.Serializer):
    id = UUIDRelatedField(queryset=PropertyManager.objects)
    name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True, allow_blank=True)

    def to_internal_value(self, data: dict[str, Any]) -> dict[str, Any]:
        super().to_internal_value(data)

        try:
            return PropertyManager.objects.only("id").get(uuid=uuid.UUID(hex=data["id"]))
        except (PropertyManager.DoesNotExist, ValueError, TypeError):
            return {}


class PropertyManagerViewSet(HitasModelViewSet):
    serializer_class = PropertyManagerSerializer
    model_class = PropertyManager

    def get_queryset(self):
        return PropertyManager.objects.all().order_by("id")

    def get_filterset_class(self):
        return PropertyManagerFilterSet
