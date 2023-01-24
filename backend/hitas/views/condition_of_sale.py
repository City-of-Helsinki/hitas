import datetime
import uuid
from itertools import chain
from typing import Any, Optional

from django.db.models import OuterRef, Prefetch, Q, QuerySet, Subquery
from enumfields.drf import EnumField, EnumSupportSerializerMixin
from rest_framework import serializers

from hitas.exceptions import HitasModelNotFound
from hitas.models import Apartment, ApartmentSale, ConditionOfSale, Owner, Ownership
from hitas.models.condition_of_sale import GracePeriod, condition_of_sale_queryset
from hitas.utils import lookup_id_to_uuid
from hitas.views.utils import HitasModelSerializer, HitasModelViewSet, UUIDField


class MinimalApartmentSerializer(HitasModelSerializer):
    class Meta:
        model = Apartment
        fields = [
            "id",
            "street_address",
            "apartment_number",
            "floor",
            "stair",
        ]


class MinimalOwnerSerializer(HitasModelSerializer):
    class Meta:
        model = Owner
        fields = [
            "id",
            "name",
            "identifier",
            "email",
        ]


class ConditionOfSaleOwnershipSerializer(HitasModelSerializer):

    apartment = MinimalApartmentSerializer()
    owner = MinimalOwnerSerializer()

    class Meta:
        model = Ownership
        fields = [
            "id",
            "percentage",
            "apartment",
            "owner",
        ]


class ConditionOfSaleSerializer(EnumSupportSerializerMixin, HitasModelSerializer):

    new_ownership = ConditionOfSaleOwnershipSerializer(read_only=True)
    old_ownership = ConditionOfSaleOwnershipSerializer(read_only=True)
    grace_period = EnumField(GracePeriod)
    fulfilled = serializers.SerializerMethodField()

    @staticmethod
    def get_fulfilled(instance: ConditionOfSale) -> Optional[datetime.datetime]:
        return instance.fulfilled

    class Meta:
        model = ConditionOfSale
        fields = [
            "id",
            "new_ownership",
            "old_ownership",
            "grace_period",
            "fulfilled",
        ]


class ConditionOfSaleCreateSerializer(serializers.Serializer):

    additional_ownerships = serializers.ListField(child=UUIDField(), required=False, allow_empty=True)

    def validate_additional_ownerships(self, value: list[str]) -> list[Ownership]:
        if value:
            value = self.get_additional_ownerships(value)
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        owner_uuid = lookup_id_to_uuid(self.context["view"].kwargs.get("owner_uuid"), Owner)
        attrs["owner"] = self.get_owner_with_ownerships(owner_uuid)
        return attrs

    def create(self, validated_data: dict[str, Any]) -> list[ConditionOfSale]:
        owner: Owner = validated_data.pop("owner")
        additional_ownerships: list[Ownership] = validated_data.pop("additional_ownerships", [])
        ownerships = list(chain(owner.ownerships.all(), additional_ownerships))

        to_save: list[ConditionOfSale] = []

        # Create conditions of sale for all ownerships to new apartments this owner has,
        # and all the additional ownerships given (if they are for new apartments)
        for ownership in ownerships:
            apartment = ownership.apartment
            is_additional = ownership in additional_ownerships

            if apartment.is_new:
                for other_ownership in ownerships:
                    # Don't create circular conditions of sale
                    if ownership.id == other_ownership.id:
                        continue

                    # Don't create conditions of sale between two additional ownerships
                    if is_additional and other_ownership in additional_ownerships:
                        continue

                    to_save.append(ConditionOfSale(new_ownership=ownership, old_ownership=other_ownership))

        if not to_save:
            return []

        # 'ignore_conflicts' so that we can create all missing conditions of sale if some already exist
        ConditionOfSale.objects.bulk_create(to_save, ignore_conflicts=True)

        # We have to fetch ownerships separately, since if only some conditions of sale in 'to_save' were created,
        # the ids or conditions of sale in the returned list from 'bulk_create' are not correct.
        return list(
            condition_of_sale_queryset().filter(Q(new_ownership__owner=owner) | Q(old_ownership__owner=owner)).all()
        )

    def get_additional_ownerships(self, value: list[str]) -> list[Ownership]:
        return list(
            self.ownerships_with_apartment()
            .filter(uuid__in=value)
            .prefetch_related(
                Prefetch(
                    "apartment__sales",
                    self.first_sale(),
                )
            )
            .all()
        )

    def get_owner_with_ownerships(self, owner_uuid: uuid.UUID) -> Owner:
        # Check that owner exists and prefetch required fields for creating
        # conditions of sale between their ownerships
        try:
            return (
                Owner.objects.prefetch_related(
                    Prefetch(
                        "ownerships",
                        self.ownerships_with_apartment(),
                    ),
                    Prefetch(
                        "ownerships__apartment__sales",
                        self.first_sale(),
                    ),
                )
                .only("id")
                .get(uuid=owner_uuid)
            )
        except Owner.DoesNotExist as error:
            raise HitasModelNotFound(model=Owner) from error

    @staticmethod
    def ownerships_with_apartment() -> QuerySet[Ownership]:
        return Ownership.objects.select_related("apartment").only(
            "id",
            "uuid",
            "percentage",
            "apartment__id",
            "apartment__first_purchase_date",
            "apartment__completion_date",
        )

    @staticmethod
    def first_sale() -> QuerySet[ApartmentSale]:
        # Limit the fetched sales to only the first sale,
        # as we only need that to figure out if the apartment is new
        return ApartmentSale.objects.filter(
            id__in=Subquery(
                ApartmentSale.objects.filter(apartment_id=OuterRef("apartment_id"))
                .order_by("purchase_date")
                .values_list("id", flat=True)[:1]
            )
        ).only("id", "purchase_date")

    def to_representation(self, validated_data: list[ConditionOfSale]) -> dict[str, Any]:
        return {
            "conditions_of_sale": [
                ConditionOfSaleSerializer(condition_of_sale).data for condition_of_sale in validated_data
            ]
        }


class ConditionOfSaleViewSet(HitasModelViewSet):
    serializer_class = ConditionOfSaleSerializer
    create_serializer_class = ConditionOfSaleCreateSerializer
    model_class = ConditionOfSale

    def get_queryset(self):
        return condition_of_sale_queryset()
