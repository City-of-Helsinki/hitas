from rest_framework import serializers

from hitas.models import RealEstate
from hitas.views.building import BuildingSerializer
from hitas.views.helpers import AddressSerializer


class RealEstateSerializer(serializers.ModelSerializer):
    address = AddressSerializer(source="*")
    buildings = BuildingSerializer(many=True)

    class Meta:
        model = RealEstate
        fields = [
            "address",
            "property_identifier",
            "buildings",
        ]
