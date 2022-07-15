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


class PropertyManagerViewSet(HitasModelViewSet):
    serializer_class = PropertyManagerSerializer
    model_class = PropertyManager

    def get_queryset(self):
        return PropertyManager.objects.select_related("postal_code")
