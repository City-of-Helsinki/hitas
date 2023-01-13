from typing import Any
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db.models import Prefetch

from hitas.exceptions import HitasModelNotFound
from hitas.models import Apartment, ApartmentSale
from hitas.models.ownership import Ownership, OwnershipLike, check_ownership_percentages
from hitas.views.ownership import OwnershipSerializer
from hitas.views.utils import HitasModelSerializer, HitasModelViewSet


class ApartmentSaleSerializer(HitasModelSerializer):

    ownerships = OwnershipSerializer(many=True)

    def to_internal_value(self, data: dict[str, Any]) -> dict[str, Any]:
        # Add empty list here for os that ownerships is can be left out when updating.
        data.setdefault("ownerships", [])
        return super().to_internal_value(data)

    def validate_ownerships(self, ownerships: list[OwnershipLike]) -> list[OwnershipLike]:
        if self.context["view"].action != "create":
            if ownerships:
                raise ValidationError("Can't update ownerships.")
            return ownerships

        if not ownerships:
            raise ValidationError("Sale must have ownerships.")

        check_ownership_percentages(ownerships)
        return ownerships

    def get_apartment_id(self) -> int:
        try:
            apartment_uuid = UUID(hex=self.context["view"].kwargs.get("apartment_uuid"))
            apartment_id = Apartment.objects.only("id").get(uuid=apartment_uuid).id
        except (Apartment.DoesNotExist, ValueError) as error:
            raise HitasModelNotFound(model=Apartment) from error
        return apartment_id

    def create(self, validated_data: dict[str, Any]) -> ApartmentSale:
        ownership_data: list[OwnershipLike] = validated_data.pop("ownerships")
        apartment_id = self.get_apartment_id()
        validated_data["apartment_id"] = apartment_id

        instance: ApartmentSale = super().create(validated_data)

        # Mark current ownerships for the apartment as "past"
        Ownership.objects.filter(apartment_id=apartment_id).delete()
        # Replace with the new ownerships
        for entry in ownership_data:
            Ownership.objects.create(apartment_id=apartment_id, sale=instance, **entry)

        return instance

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
            "include_in_statistics",
        ]


class ApartmentSaleViewSet(HitasModelViewSet):
    serializer_class = ApartmentSaleSerializer
    model_class = ApartmentSale

    def get_queryset(self):
        return ApartmentSale.objects.prefetch_related(
            Prefetch(
                "ownerships",
                Ownership.objects.select_related("owner"),
            ),
        ).only(
            "id",
            "uuid",
            "notification_date",
            "purchase_date",
            "purchase_price",
            "apartment_share_of_housing_company_loans",
            "include_in_statistics",
        )
