import datetime
import uuid
from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db.models import OuterRef, Prefetch, Q, Subquery
from enumfields.drf import EnumField, EnumSupportSerializerMixin
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from hitas.models import Apartment, ApartmentSale, ConditionOfSale, Owner, Ownership
from hitas.models.condition_of_sale import GracePeriod, condition_of_sale_queryset
from hitas.views.utils import ApartmentHitasAddressSerializer, HitasModelSerializer, HitasModelViewSet, UUIDField


class MinimalApartmentSerializer(HitasModelSerializer):
    housing_company = serializers.SerializerMethodField()
    address = ApartmentHitasAddressSerializer(source="*")

    def get_housing_company(self, instance: Apartment):
        return {
            "id": instance.housing_company.uuid.hex,
            "display_name": instance.housing_company.display_name,
        }

    class Meta:
        model = Apartment
        fields = [
            "id",
            "address",
            "housing_company",
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


class ConditionOfSaleOwnershipSerializer(ModelSerializer):

    apartment = MinimalApartmentSerializer()
    owner = MinimalOwnerSerializer()

    class Meta:
        model = Ownership
        fields = [
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

    household = serializers.ListField(child=UUIDField())

    def validate_household(self, value: list[uuid.UUID]) -> list[Owner]:
        if value:
            value = self.get_household(value)
        return value

    def create(self, validated_data: dict[str, Any]) -> list[ConditionOfSale]:
        owners: list[Owner] = validated_data.pop("household", [])

        return self.create_conditions_of_sale(owners)

    @staticmethod
    def create_conditions_of_sale(owners: list[Owner]) -> list[ConditionOfSale]:
        ownerships: list[Ownership] = [
            ownership for owner in owners for ownership in owner.ownerships.all() if not owner.bypass_conditions_of_sale
        ]

        to_save: list[ConditionOfSale] = []

        # Create conditions of sale for all ownerships to new apartments this owner has,
        # and all the additional ownerships given (if they are for new apartments)
        for ownership in ownerships:
            apartment = ownership.apartment

            if apartment.is_new:
                for other_ownership in ownerships:
                    # Don't create circular conditions of sale
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
            condition_of_sale_queryset()
            .filter(Q(new_ownership__owner__in=owners) | Q(old_ownership__owner__in=owners))
            .all()
        )

    @staticmethod
    def get_household(owner_uuids: list[uuid.UUID]) -> list[Owner]:
        # Check that owners exists and prefetch required fields for creating
        # conditions of sale between their ownerships
        owners = list(
            Owner.objects.prefetch_related(
                Prefetch(
                    "ownerships",
                    Ownership.objects.select_related("apartment"),
                ),
                Prefetch(
                    "ownerships__apartment__sales",
                    # Limit the fetched sales to only the first sale,
                    # as we only need that to figure out if the apartment is new
                    ApartmentSale.objects.filter(
                        id__in=Subquery(
                            ApartmentSale.objects.filter(apartment_id=OuterRef("apartment_id"))
                            .order_by("purchase_date")
                            .values_list("id", flat=True)[:1]
                        )
                    ),
                ),
            ).filter(uuid__in=owner_uuids)
        )

        if len(owners) != len(owner_uuids):
            found_uuids: set[str] = {owner.uuid.hex for owner in owners}
            missing_owners = ", ".join(
                repr(owner_uuid.hex) for owner_uuid in owner_uuids if owner_uuid not in found_uuids
            )
            raise ValidationError(f"Owners not found: {missing_owners}.")

        return owners

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
