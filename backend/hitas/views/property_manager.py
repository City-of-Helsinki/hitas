from hitas.models import PropertyManager
from hitas.views.utils import HitasModelSerializer, HitasModelViewSet, UUIDField


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


class ReadOnlyPropertyManagerSerializer(PropertyManagerSerializer):
    id = UUIDField(source="uuid")
    address = PropertyManagerAddressSerializer(source="*", read_only=True)

    class Meta(PropertyManagerSerializer.Meta):
        read_only_fields = ["name", "email", "address"]


class PropertyManagerViewSet(HitasModelViewSet):
    serializer_class = PropertyManagerSerializer
    model_class = PropertyManager

    def get_queryset(self):
        return PropertyManager.objects.all().order_by("id")
