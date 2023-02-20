from typing import Any

from django.core.exceptions import ValidationError
from django.db.models import Prefetch, prefetch_related_objects
from rest_framework import serializers

from hitas.exceptions import HitasModelNotFound
from hitas.models import Apartment, ApartmentSale
from hitas.models.ownership import Ownership, OwnershipLike, check_ownership_percentages
from hitas.services.apartment import prefetch_first_sale
from hitas.services.condition_of_sale import create_conditions_of_sale
from hitas.utils import lookup_id_to_uuid
from hitas.views.ownership import OwnershipSerializer
from hitas.views.utils import HitasModelSerializer, HitasModelViewSet


class ApartmentSaleSerializer(HitasModelSerializer):

    ownerships = OwnershipSerializer(many=True)

    def to_internal_value(self, data: dict[str, Any]) -> dict[str, Any]:
        # Add empty list here for os that ownerships is can be left out when updating.
        data.setdefault("ownerships", [])
        return super().to_internal_value(data)

    @staticmethod
    def validate_ownerships(ownerships: list[OwnershipLike]) -> list[OwnershipLike]:
        if ownerships:
            raise ValidationError("Can't update ownerships.")
        return ownerships

    def update(self, instance: ApartmentSale, validated_data: dict[str, Any]) -> ApartmentSale:
        validated_data.pop("ownerships")
        return super().update(instance, validated_data)

    class Meta:
        model = ApartmentSale
        fields = [
            "id",
            "ownerships",
            "notification_date",
            "purchase_date",
            "purchase_price",
            "apartment_share_of_housing_company_loans",
            "exclude_in_statistics",
        ]


class ApartmentSaleCreateSerializer(HitasModelSerializer):

    ownerships = OwnershipSerializer(many=True)
    conditions_of_sale_created = serializers.ReadOnlyField(default=False)

    @staticmethod
    def validate_ownerships(ownerships: list[OwnershipLike]) -> list[OwnershipLike]:
        if not ownerships:
            raise ValidationError("Sale must have ownerships.")

        if len(ownerships) != len({ownership["owner"] for ownership in ownerships}):
            raise ValidationError("All ownerships must be for different owners.")

        check_ownership_percentages(ownerships)
        return ownerships

    def create(self, validated_data: dict[str, Any]) -> ApartmentSale:
        ownership_data: list[OwnershipLike] = validated_data.pop("ownerships")
        apartment_uuid = lookup_id_to_uuid(self.context["view"].kwargs.get("apartment_uuid"), Apartment)

        try:
            apartment = Apartment.objects.prefetch_related(prefetch_first_sale()).get(uuid=apartment_uuid)
        except Apartment.DoesNotExist as error:
            raise HitasModelNotFound(model=Apartment) from error

        validated_data["apartment"] = apartment

        instance: ApartmentSale = super().create(validated_data)

        ownerships = apartment.change_ownerships(ownership_data, sale=instance)
        self.context["conditions_of_sale_created"] = False

        if apartment.is_new:
            owners = [ownership.owner for ownership in ownerships]
            prefetch_related_objects(
                owners,
                Prefetch(
                    "ownerships",
                    Ownership.objects.select_related("apartment"),
                ),
                # Limit the fetched sales to only the first sale,
                # as we only need that to figure out if the apartment is new.
                # Ignore the sale we just created so that this apartment is treated as new.
                prefetch_first_sale("ownerships__apartment__", ignore=[instance.id]),
            )
            for owner in owners:
                cos = create_conditions_of_sale(owners=[owner])
                if cos:
                    self.context["conditions_of_sale_created"] = True

        return instance

    def to_representation(self, validated_data: ApartmentSale) -> dict[str, Any]:
        ret = super().to_representation(validated_data)
        ret["conditions_of_sale_created"] = self.context.pop("conditions_of_sale_created", False)
        return ret

    class Meta:
        model = ApartmentSale
        fields = [
            "id",
            "ownerships",
            "notification_date",
            "purchase_date",
            "purchase_price",
            "apartment_share_of_housing_company_loans",
            "exclude_in_statistics",
            "conditions_of_sale_created",
        ]


class ApartmentSaleViewSet(HitasModelViewSet):
    serializer_class = ApartmentSaleSerializer
    create_serializer_class = ApartmentSaleCreateSerializer
    model_class = ApartmentSale

    def get_default_queryset(self):
        return ApartmentSale.objects.prefetch_related(
            Prefetch(
                "ownerships",
                Ownership.objects.select_related("owner"),
            ),
        )
