from rest_framework import serializers

from hitas.models import Owner
from hitas.views.person import PersonSerializer
from hitas.views.utils import HitasDecimalField


class OwnerSerializer(serializers.ModelSerializer):
    person = PersonSerializer()
    ownership_percentage = HitasDecimalField(required=True)

    class Meta:
        model = Owner
        fields = [
            "person",
            "ownership_percentage",
            "ownership_start_date",
            "ownership_end_date",
        ]
