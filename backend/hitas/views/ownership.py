from rest_framework import mixins, serializers
from rest_framework.viewsets import GenericViewSet

from hitas.models import NonObfuscatedOwner, Owner, Ownership
from hitas.views.utils import HitasDecimalField, UUIDRelatedField
from hitas.views.utils.serializers import HitasModelSerializer, ReadOnlySerializer
from hitas.views.utils.viewsets import HitasModelMixin


class OwnerSerializer(ReadOnlySerializer):
    id = UUIDRelatedField(queryset=Owner.objects)
    name = serializers.CharField(read_only=True)
    identifier = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    non_disclosure = serializers.BooleanField(read_only=True)

    def get_model_class(self):
        return Owner

    class Meta:
        fields = [
            "id",
            "name",
            "identifier",
            "email",
            "non_disclosure",
        ]


class NonObfuscatedOwnerSerializer(OwnerSerializer):
    def get_model_class(self):
        return NonObfuscatedOwner


class OwnershipSerializer(HitasModelSerializer):
    owner = OwnerSerializer()
    percentage = HitasDecimalField()

    class Meta:
        model = Ownership
        fields = [
            "id",
            "owner",
            "percentage",
        ]
        read_only_fields = ["id", "owner", "percentage"]


class NonObfuscatedOwnerShipSerializer(OwnershipSerializer):
    owner = NonObfuscatedOwnerSerializer()


class OwnershipUpdateSerializer(HitasModelSerializer):
    class Meta:
        model = Ownership
        fields = [
            "id",
            "percentage",
        ]
        read_only_fields = ["id"]


class OwnershipViewSet(HitasModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    serializer_class = OwnershipSerializer
    update_serializer_class = OwnershipUpdateSerializer
    model_class = Ownership
    http_method_names = ["get", "patch"]
