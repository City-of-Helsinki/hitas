from hitas.models import RealEstate
from hitas.views.building import BuildingSerializer
from hitas.views.helpers import AddressSerializer, HitasModelSerializer


class RealEstateSerializer(HitasModelSerializer):
    address = AddressSerializer(source="*")
    buildings = BuildingSerializer(many=True)

    class Meta:
        model = RealEstate
        fields = [
            "id",
            "address",
            "property_identifier",
            "buildings",
        ]
