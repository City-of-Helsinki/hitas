import datetime
import uuid
from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db.models import Prefetch
from enumfields.drf import EnumField, EnumSupportSerializerMixin
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from safedelete import HARD_DELETE

from hitas.exceptions import ModelConflict
from hitas.models.apartment import Apartment
from hitas.models.condition_of_sale import ConditionOfSale, GracePeriod
from hitas.models.housing_company import HitasType
from hitas.models.owner import Owner
from hitas.models.ownership import Ownership
from hitas.services.apartment import prefetch_first_sale
from hitas.services.condition_of_sale import condition_of_sale_queryset, create_conditions_of_sale
from hitas.views.utils import ApartmentHitasAddressSerializer, HitasModelSerializer, HitasModelViewSet, UUIDField


class MinimalApartmentSerializer(HitasModelSerializer):
    housing_company = serializers.SerializerMethodField()
    address = ApartmentHitasAddressSerializer(source="*")

    @staticmethod
    def get_housing_company(instance: Apartment):
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
            "non_disclosure",
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

    @staticmethod
    def get_household(owner_uuids: list[uuid.UUID]) -> list[Owner]:
        # Check that owners exists and prefetch required fields for creating
        # conditions of sale between their ownerships
        owners = list(
            Owner.objects.prefetch_related(
                Prefetch(
                    "ownerships",
                    Ownership.objects.select_related("sale__apartment__building__real_estate__housing_company").exclude(
                        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.HALF_HITAS,
                    ),
                ),
                prefetch_first_sale(lookup_prefix="ownerships__sale__apartment__"),
                "ownerships__sale__apartment__sales__ownerships",
                "ownerships__sale__apartment__sales__ownerships__conditions_of_sale_new",
            ).filter(uuid__in=owner_uuids)
        )

        if len(owners) != len(owner_uuids):
            found_uuids: set[str] = {owner.uuid.hex for owner in owners}
            missing_owners = ", ".join(
                repr(owner_uuid.hex) for owner_uuid in owner_uuids if owner_uuid not in found_uuids
            )
            raise ValidationError(f"Owners not found: {missing_owners}.")

        return owners

    def create(self, validated_data: dict[str, Any]) -> list[ConditionOfSale]:
        owners: list[Owner] = validated_data.pop("household", [])
        return create_conditions_of_sale(owners)

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

    def perform_destroy(self, instance: ConditionOfSale) -> None:
        if instance.new_ownership.owner == instance.old_ownership.owner:
            raise ModelConflict("Cannot delete condition of sale between the same owner.", error_code="invalid")

        instance.delete(force_policy=HARD_DELETE)

    def get_queryset(self):
        return condition_of_sale_queryset()
