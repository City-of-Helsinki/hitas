from rest_framework import status
from rest_framework.response import Response

from hitas.models import Owner, Ownership
from hitas.views.utils import HitasCharFilter, HitasFilterSet, HitasModelSerializer, HitasModelViewSet


class OwnerSerializer(HitasModelSerializer):
    class Meta:
        model = Owner
        fields = [
            "id",
            "name",
            "identifier",
            "email",
        ]


class OwnerFilterSet(HitasFilterSet):
    name = HitasCharFilter(lookup_expr="icontains")
    identifier = HitasCharFilter(lookup_expr="icontains")
    email = HitasCharFilter(lookup_expr="iexact")

    class Meta:
        model = Owner
        fields = ["name", "identifier", "email"]


class OwnerViewSet(HitasModelViewSet):
    serializer_class = OwnerSerializer
    model_class = Owner

    def destroy(self, request, *args, **kwargs):
        instance: Owner = self.get_object()

        number_of_ownerships = Ownership.objects.filter(owner__id=instance.id).count()
        if number_of_ownerships > 0:
            return Response(
                {
                    "error": "owner_in_use",
                    "message": "Owner has active ownerships and cannot be removed.",
                    "reason": "Conflict",
                    "status": 409,
                },
                status=status.HTTP_409_CONFLICT,
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        return Owner.objects.all().order_by("id")

    @staticmethod
    def get_filterset_class():
        return OwnerFilterSet
