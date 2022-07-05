from rest_framework import serializers

from hitas.models import PropertyManager
from hitas.views.helpers import AddressSerializer


class PropertyManagerSerializer(serializers.ModelSerializer):
    address = AddressSerializer(source="*")

    class Meta:
        model = PropertyManager
        fields = [
            "address",
            "name",
            "email",
        ]
