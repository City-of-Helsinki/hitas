from rest_framework import serializers

from hitas.models import Ownership
from hitas.views.person import PersonSerializer
from hitas.views.utils import HitasDecimalField


class OwnershipSerializer(serializers.ModelSerializer):
    owner = PersonSerializer()
    percentage = HitasDecimalField(required=True)

    class Meta:
        model = Ownership
        fields = [
            "owner",
            "percentage",
            "start_date",
            "end_date",
        ]
