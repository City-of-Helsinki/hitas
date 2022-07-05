from rest_framework import serializers

from hitas.models import Building
from hitas.views.helpers import AddressSerializer, ValueOrNullField


class BuildingSerializer(serializers.ModelSerializer):
    address = AddressSerializer(source="*")
    building_identifier = ValueOrNullField(required=False)

    class Meta:
        model = Building
        fields = [
            "address",
            "building_identifier",
            "completion_date",
        ]
