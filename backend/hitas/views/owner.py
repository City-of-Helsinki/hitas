from hitas.models import Owner
from hitas.views.utils import HitasModelSerializer, HitasModelViewSet


class OwnerSerializer(HitasModelSerializer):
    class Meta:
        model = Owner
        fields = [
            "apartment",
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
