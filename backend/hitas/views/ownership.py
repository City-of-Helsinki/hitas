from rest_framework import serializers

from hitas.models import Ownership, Person
from hitas.views.utils import HitasDecimalField, UUIDRelatedField
from hitas.views.utils.serializers import ReadOnlySerializer


class PersonSerializer(ReadOnlySerializer):
    id = UUIDRelatedField(queryset=Person.objects, source="uuid")

    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    social_security_number = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)

    def get_model_class(self):
        return Person

    class Meta:
        fields = [
            "id",
            "first_name",
            "last_name",
            "social_security_number",
            "email",
        ]


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
