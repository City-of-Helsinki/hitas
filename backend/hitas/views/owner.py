from typing import Any, Optional

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from hitas.models import Owner, Ownership
from hitas.models.utils import (
    check_business_id,
    check_social_security_number,
    deobfuscate,
)
from hitas.services.owner import exclude_obfuscated_owners
from hitas.views.utils import HitasCharFilter, HitasFilterSet, HitasModelMixin, HitasModelSerializer, HitasModelViewSet


class OwnerSerializer(HitasModelSerializer):
    def validate_identifier(self, value: Optional[str]) -> str:
        self.instance: Optional[Owner]
        valid_identifier = check_social_security_number(value) or check_business_id(value)
        if self.instance is not None:  # update
            if value != self.instance.identifier:
                if self.instance.valid_identifier and not valid_identifier:
                    raise ValidationError("Previous identifier was valid. Cannot update to an invalid one.")

                if valid_identifier and Owner.objects.filter(identifier=value).exists():
                    raise ValidationError("An owner with this identifier already exists.")

        elif valid_identifier and Owner.objects.filter(identifier=value).exists():  # create
            raise ValidationError("An owner with this identifier already exists.")

        return value

    class Meta:
        model = Owner
        fields = [
            "id",
            "name",
            "identifier",
            "email",
            "non_disclosure",
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

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
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
        qs = Owner.objects.all().order_by("id")
        return exclude_obfuscated_owners(qs)

    @staticmethod
    def get_filterset_class():
        return OwnerFilterSet


class DeObfuscatedOwnerView(HitasModelMixin, GenericViewSet):
    serializer_class = OwnerSerializer
    model_class = Owner

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        instance: Owner = self.get_object()
        deobfuscate(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
