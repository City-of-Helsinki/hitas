from hitas.models import Building
from hitas.views.helpers import AddressSerializer, HitasModelSerializer, ValueOrNullField


class BuildingSerializer(HitasModelSerializer):
    address = AddressSerializer(source="*")
    building_identifier = ValueOrNullField(required=False)

    class Meta:
        model = Building
        fields = [
            "id",
            "address",
            "building_identifier",
            "completion_date",
        ]
