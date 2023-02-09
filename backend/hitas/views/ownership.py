from rest_framework import serializers

from hitas.models import Owner, Ownership
from hitas.views.utils import HitasDecimalField, UUIDRelatedField
from hitas.views.utils.serializers import ReadOnlySerializer


class OwnerSerializer(ReadOnlySerializer):
    id = UUIDRelatedField(queryset=Owner.objects)
    name = serializers.CharField(read_only=True)
    identifier = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)

    def get_model_class(self):
        return Owner

    class Meta:
        fields = [
            "id",
            "name",
            "identifier",
            "email",
        ]


class OwnershipSerializer(serializers.ModelSerializer):

    owner = OwnerSerializer()
    percentage = HitasDecimalField(required=True)

    class Meta:
        model = Ownership
        fields = [
            "owner",
            "percentage",
        ]
