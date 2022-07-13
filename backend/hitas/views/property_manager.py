from uuid import UUID

from hitas.exceptions import HitasModelNotFound
from hitas.models import PropertyManager
from hitas.views.utils import AddressSerializer, HitasModelSerializer, HitasModelViewSet


class PropertyManagerSerializer(HitasModelSerializer):
    address = AddressSerializer(source="*")

    class Meta:
        model = PropertyManager
        fields = [
            "id",
            "address",
            "name",
            "email",
        ]

    def to_internal_value(self, data):
        """If referenced in another serializer by id, return an object"""
        if data.get("id", None) is not None:
            try:
                return self.Meta.model.objects.get(uuid=UUID(hex=str(data.get("id", None))))
            except (self.Meta.model.DoesNotExist, ValueError):
                raise HitasModelNotFound(model=self.Meta.model)
        return super().to_internal_value(data)


class PropertyManagerViewSet(HitasModelViewSet):
    serializer_class = PropertyManagerSerializer
    model_class = PropertyManager

    def get_queryset(self):
        return PropertyManager.objects.select_related("postal_code")
