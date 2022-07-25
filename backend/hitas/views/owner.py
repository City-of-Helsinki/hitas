from rest_framework import serializers

from hitas.models import Owner
from hitas.views.person import PersonSerializer
from hitas.views.utils import HitasModelSerializer, HitasModelViewSet


class OwnerSerializer(HitasModelSerializer):
    apartment_id = serializers.SerializerMethodField()
    person = PersonSerializer()

    def get_apartment_id(self, instance: Owner) -> str:
        return instance.apartment.uuid.hex

    class Meta:
        model = Owner
        fields = [
            "apartment_id",
            "person",
            "ownership_percentage",
            "ownership_start_date",
            "ownership_end_date",
        ]


class OwnerViewSet(HitasModelViewSet):
    serializer_class = OwnerSerializer
    model_class = Owner

    def get_queryset(self):
        return Owner.objects.select_related("apartment", "person")
