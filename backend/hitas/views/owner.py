from typing import Any, Optional

from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from hitas.exceptions import HitasModelNotFound
from hitas.models import Owner, Ownership
from hitas.models.apartment import Apartment
from hitas.models.owner import NonObfuscatedOwner
from hitas.models.utils import (
    check_business_id,
    check_social_security_number,
    deobfuscate,
)
from hitas.services.validation import lookup_id_to_uuid
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


class OwnerMergeSerializer(serializers.Serializer):
    first_owner_id = serializers.CharField()
    second_owner_id = serializers.CharField()
    should_use_second_owner_name = serializers.BooleanField()
    should_use_second_owner_identifier = serializers.BooleanField()
    should_use_second_owner_email = serializers.BooleanField()


class OwnerFilterSet(HitasFilterSet):
    name = HitasCharFilter(lookup_expr="icontains")
    identifier = HitasCharFilter(lookup_expr="icontains")
    email = HitasCharFilter(lookup_expr="iexact")
    search = HitasCharFilter(method="filter_search")

    class Meta:
        model = Owner
        fields = ["name", "identifier", "email"]

    def filter_search(self, queryset, name, value):
        return (
            queryset.filter(name__icontains=value)
            | queryset.filter(identifier__icontains=value)
            | queryset.filter(email__icontains=value)
        )


class OwnerViewSet(HitasModelViewSet):
    serializer_class = OwnerSerializer
    model_class = NonObfuscatedOwner

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

    @action(detail=False, methods=["post"])
    def merge(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = OwnerMergeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        first_owner_uuid = lookup_id_to_uuid(data["first_owner_id"], Owner)
        second_owner_uuid = lookup_id_to_uuid(data["second_owner_id"], Owner)
        try:
            first_owner = NonObfuscatedOwner.objects.get(uuid=first_owner_uuid)
            second_owner = NonObfuscatedOwner.objects.get(uuid=second_owner_uuid)
        except Owner.DoesNotExist as error:
            raise HitasModelNotFound(Owner) from error
        # Merge of two owners of the same apartment not allowed,
        # because there is no use case for it and the transfer is non-trivial
        first_owner_apartment_ids = Apartment.objects.filter(sales__ownerships__owner_id=first_owner.pk).values_list(
            "pk", flat=True
        )
        second_owner_apartment_ids = Apartment.objects.filter(sales__ownerships__owner_id=second_owner.pk).values_list(
            "pk", flat=True
        )
        overlapping_apartment_ids = set(first_owner_apartment_ids).intersection(set(second_owner_apartment_ids))
        if len(overlapping_apartment_ids) > 0:
            return Response(
                {
                    "error": "overlapping_ownerships",
                    "message": "Kahden saman asunnon omistajan yhdistäminen ei ole sallittua.",
                    "reason": "Conflict",
                    "status": 409,
                },
                status=status.HTTP_409_CONFLICT,
            )
        # Transfer ownerships from second owner to first owner
        Ownership.objects.filter(owner=second_owner).update(owner=first_owner)
        # Update first owner with data from second owner if requested
        if data["should_use_second_owner_name"]:
            first_owner.name = second_owner.name
        if data["should_use_second_owner_identifier"]:
            first_owner.identifier = second_owner.identifier
            first_owner.valid_identifier = check_social_security_number(first_owner.identifier) or check_business_id(
                first_owner.identifier
            )
        if data["should_use_second_owner_email"]:
            first_owner.email = second_owner.email
        # If either owner has non-disclosure, set it to True for the merged owner
        if second_owner.non_disclosure:
            first_owner.non_disclosure = True
        first_owner.save()
        second_owner.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
