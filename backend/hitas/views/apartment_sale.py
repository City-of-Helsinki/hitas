from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Prefetch, prefetch_related_objects
from rest_framework import serializers

from hitas.exceptions import HitasModelNotFound, ModelConflict
from hitas.models.apartment import Apartment, ApartmentSale
from hitas.models.housing_company import RegulationStatus
from hitas.models.ownership import Ownership, OwnershipLike, check_ownership_percentages
from hitas.services.apartment import get_latest_sale_purchase_date, prefetch_first_sale
from hitas.services.condition_of_sale import create_conditions_of_sale
from hitas.services.validation import lookup_id_to_uuid, lookup_model_id_by_uuid
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
            "exclude_from_statistics",
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
            apartment: Apartment = (
                Apartment.objects.select_related(
                    "building__real_estate__housing_company",
                )
                .prefetch_related(
                    prefetch_first_sale(),
                    "sales__ownerships",
                    "sales__ownerships__conditions_of_sale_new",
                )
                .annotate(
                    _latest_purchase_date=get_latest_sale_purchase_date("id", include_first_sale=True),
                )
                .get(uuid=apartment_uuid)
            )
        except Apartment.DoesNotExist as error:
            raise HitasModelNotFound(model=Apartment) from error

        if apartment.housing_company.regulation_status != RegulationStatus.REGULATED:
            raise ModelConflict("Cannot sell an unregulated apartment.", error_code="invalid")

        validated_data["apartment"] = apartment

        with transaction.atomic():
            # Ownerships from precious sales are soft-deleted so that their conditions of sale are fulfilled.
            # This requires the previous sale's ownerships to be undeleted if this sale is ever cancelled.
            Ownership.objects.filter(
                sale__apartment=apartment,
                # Do not delete sales that are newer than this sale.
                sale__purchase_date__lte=validated_data["purchase_date"],
            ).delete()

            instance: ApartmentSale = super().create(validated_data)
            ownerships = Ownership.objects.bulk_create(
                objs=[
                    Ownership(
                        owner=data["owner"],
                        sale=instance,
                        percentage=data["percentage"],
                        # If this sale is earlier than the latest sale,
                        # its ownerships should be created as already soft-deleted.
                        deleted=(
                            apartment.latest_purchase_date
                            if apartment.latest_purchase_date is not None
                            and validated_data["purchase_date"] < apartment.latest_purchase_date
                            else None
                        ),
                    )
                    for data in ownership_data
                ],
            )

        self.context["conditions_of_sale_created"] = False

        if apartment.is_new:
            owners = [ownership.owner for ownership in ownerships]
            prefetch_related_objects(
                owners,
                Prefetch("ownerships", Ownership.objects.select_related("sale__apartment")),
                # Ignore the sale we just created so that apartments sold for the first time
                # after they have been completed are treated as new at this moment.
                prefetch_first_sale(lookup_prefix="ownerships__sale__apartment__", ignore=[instance.id]),
                "ownerships__sale__apartment__sales__ownerships",
                "ownerships__sale__apartment__sales__ownerships__conditions_of_sale_new",
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
            "exclude_from_statistics",
            "conditions_of_sale_created",
        ]


class ApartmentSaleViewSet(HitasModelViewSet):
    serializer_class = ApartmentSaleSerializer
    create_serializer_class = ApartmentSaleCreateSerializer
    model_class = ApartmentSale

    def get_default_queryset(self):
        apartment_id = lookup_model_id_by_uuid(self.kwargs["apartment_uuid"], Apartment)
        return ApartmentSale.objects.prefetch_related(
            Prefetch(
                "ownerships",
                Ownership.objects.select_related("owner"),
            ),
        ).filter(apartment_id=apartment_id)
