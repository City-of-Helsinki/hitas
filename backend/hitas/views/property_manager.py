from hitas.models import PropertyManager
from hitas.views.utils import HitasModelSerializer, HitasModelViewSet


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


class PropertyManagerViewSet(HitasModelViewSet):
    serializer_class = PropertyManagerSerializer
    model_class = PropertyManager

    def get_queryset(self):
        return PropertyManager.objects.all()
