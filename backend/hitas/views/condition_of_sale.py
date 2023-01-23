import datetime
from typing import Any, Optional

from django.db.models import Prefetch, Q
from enumfields.drf import EnumField, EnumSupportSerializerMixin
from rest_framework import serializers

from hitas.exceptions import HitasModelNotFound
from hitas.models import Apartment, ApartmentSale, ConditionOfSale, Owner, Ownership
from hitas.models.condition_of_sale import GracePeriod, condition_of_sale_queryset
from hitas.utils import lookup_id_to_uuid
from hitas.views.utils import HitasModelSerializer, HitasModelViewSet


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
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        owner_uuid = lookup_id_to_uuid(self.context["view"].kwargs.get("owner_uuid"), Owner)

        # Check that owner exists and prefetch required fields for creating
        # conditions of sale between their ownerships
        try:
            attrs["owner"] = Owner.objects.prefetch_related(
                Prefetch(
                    "ownerships",
                    Ownership.objects.select_related("apartment").only(
                        "id",
                        "percentage",
                        "apartment__id",
                        "apartment__first_purchase_date",
                        "apartment__completion_date",
                    ),
                ),
                Prefetch(
                    "ownerships__apartment__sales",
                    ApartmentSale.objects.only(
                        "id",
                        "purchase_date",
                    ),
                ),
            ).get(uuid=owner_uuid)
        except Owner.DoesNotExist as error:
            raise HitasModelNotFound(model=Owner) from error

        return attrs

    def create(self, validated_data: dict[str, Any]) -> list[ConditionOfSale]:
        owner: Owner = validated_data.pop("owner")
        ownerships = owner.ownerships.all()

        to_save: list[ConditionOfSale] = []

        # Create conditions of sale for all ownerships to new apartments this owner has
        for ownership in ownerships:
            apartment = ownership.apartment

            if apartment.is_new:
                for other_ownership in ownerships:
                    if ownership.id == other_ownership.id:
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
