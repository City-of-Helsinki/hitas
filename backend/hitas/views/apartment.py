from collections import OrderedDict
from typing import Any, Dict

from django.core.exceptions import ValidationError
from django.urls import reverse
from enumfields.drf import EnumSupportSerializerMixin
from rest_framework import serializers
from rest_framework.fields import SkipField, empty

from hitas.models import Apartment, Building, HousingCompany, Ownership
from hitas.models.apartment import ApartmentState
from hitas.views.codes import ReadOnlyApartmentTypeSerializer
from hitas.views.ownership import OwnershipSerializer
from hitas.views.utils import (
    HitasDecimalField,
    HitasEnumField,
    HitasModelSerializer,
    HitasModelViewSet,
    UUIDRelatedField,
)


class ApartmentHitasAddressSerializer(serializers.Serializer):
    street_address = serializers.CharField()
    postal_code = serializers.CharField(source="building.real_estate.housing_company.postal_code.value", read_only=True)
    city = serializers.CharField(source="building.real_estate.housing_company.city", read_only=True)
    apartment_number = serializers.IntegerField(min_value=0)
    floor = serializers.CharField(max_length=50, required=False, allow_null=True)
    stair = serializers.CharField(max_length=16)


class SharesSerializer(serializers.Serializer):
    start = serializers.IntegerField(source="share_number_start", min_value=1)
    end = serializers.IntegerField(source="share_number_end", min_value=1)
    total = serializers.SerializerMethodField()

    def get_total(self, instance: Apartment) -> int:
        return instance.shares_count

    def validate(self, data):
        if data["share_number_start"] > data["share_number_end"]:
            raise ValidationError("'shares.start' must not be greater than 'shares.end'.")

        return data

    def run_validation(self, data=empty):
        value = super().run_validation(data)

        if value is None:
            raise SkipField

        return value

    def to_representation(self, instance):
        if instance.share_number_start is None:
            return None

        return super().to_representation(instance)

    def validate_empty_values(self, data):
        if data is None:
            return True, None
        else:
            return super().validate_empty_values(data)


class ConstructionPrices(serializers.Serializer):
    loans = serializers.IntegerField(source="loans_during_construction", required=False, allow_null=True, min_value=0)
    additional_work = serializers.IntegerField(
        source="additional_work_during_construction",
        required=False,
        allow_null=True,
        min_value=0,
    )
    interest = serializers.IntegerField(
        source="interest_during_construction", required=False, allow_null=True, min_value=0
    )
    debt_free_purchase_price = serializers.IntegerField(
        source="debt_free_purchase_price_during_construction", required=False, allow_null=True, min_value=0
    )


class PricesSerializer(serializers.Serializer):
    debt_free_purchase_price = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    primary_loan_amount = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    acquisition_price = serializers.IntegerField(read_only=True)
    purchase_price = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    first_purchase_date = serializers.DateField(required=False, allow_null=True)
    second_purchase_date = serializers.DateField(required=False, allow_null=True)

    construction = ConstructionPrices(source="*", required=False, allow_null=True)


def create_links(instance: Apartment) -> Dict[str, Any]:
    return {
        "housing_company": {
            "id": instance.building.real_estate.housing_company.uuid.hex,
            "display_name": instance.building.real_estate.housing_company.display_name,
            "link": reverse(
                "hitas:housing-company-detail",
                kwargs={
                    "uuid": instance.building.real_estate.housing_company.uuid.hex,
                },
            ),
        },
        "real_estate": {
            "id": instance.building.real_estate.uuid.hex,
            "link": reverse(
                "hitas:real-estate-detail",
                kwargs={
                    "housing_company_uuid": instance.building.real_estate.housing_company.uuid.hex,
                    "uuid": instance.building.real_estate.uuid.hex,
                },
            ),
        },
        "building": {
            "id": instance.building.uuid.hex,
            "link": reverse(
                "hitas:building-detail",
                kwargs={
                    "housing_company_uuid": instance.building.real_estate.housing_company.uuid.hex,
                    "real_estate_uuid": instance.building.real_estate.uuid.hex,
                    "uuid": instance.building.uuid.hex,
                },
            ),
        },
        "apartment": {
            "id": instance.uuid.hex,
            "link": reverse(
                "hitas:apartment-detail",
                kwargs={
                    "housing_company_uuid": instance.building.real_estate.housing_company.uuid.hex,
                    "uuid": instance.uuid.hex,
                },
            ),
        },
    }


class ApartmentDetailSerializer(EnumSupportSerializerMixin, HitasModelSerializer):
    state = HitasEnumField(enum=ApartmentState)
    type = ReadOnlyApartmentTypeSerializer(source="apartment_type")
    address = ApartmentHitasAddressSerializer(source="*")
    completion_date = serializers.DateField(required=False, allow_null=True)
    surface_area = HitasDecimalField()
    shares = SharesSerializer(source="*", required=False, allow_null=True)
    prices = PricesSerializer(source="*", required=False, allow_null=True)
    ownerships = OwnershipSerializer(many=True, read_only=False)
    links = serializers.SerializerMethodField()
    building = UUIDRelatedField(queryset=Building.objects.all(), write_only=True)

    @staticmethod
    def get_links(instance: Apartment):
        return create_links(instance)

    def validate_building(self, building: Building):
        housing_company_uuid = self.context["view"].kwargs["housing_company_uuid"]
        try:
            import uuid

            hc = HousingCompany.objects.only("id").get(uuid=uuid.UUID(hex=housing_company_uuid))
        except (HousingCompany.DoesNotExist, ValueError, TypeError):
            raise

        if building.real_estate.housing_company.id != hc.id:
            raise ValidationError(f"Object does not exist with given id '{building.uuid.hex}'.", code="invalid")

        return building

    @staticmethod
    def validate_ownerships(ownerships: OrderedDict):
        if not ownerships:
            return ownerships

        for owner in ownerships:
            op = owner["percentage"]
            if not 0 < op <= 100:
                raise ValidationError(
                    {
                        "percentage": (
                            "Ownership percentage greater than 0 and"
                            f" less than or equal to 100. Given value was {op}."
                        )
                    },
                )

        if (sum_op := sum(o["percentage"] for o in ownerships)) != 100:
            raise ValidationError(
                {
                    "percentage": (
                        "Ownership percentage of all ownerships combined"
                        f" must be equal to 100. Given sum was {sum_op}."
                    )
                }
            )

        return ownerships

    def create(self, validated_data: dict[str, Any]):
        ownerships = validated_data.pop("ownerships")
        instance: Apartment = super().create(validated_data)
        for owner_data in ownerships:
            Ownership.objects.create(apartment=instance, **owner_data)
        return instance

    def update(self, instance: Apartment, validated_data: dict[str, Any]):
        ownerships = validated_data.pop("ownerships")
        instance: Apartment = super().update(instance, validated_data)

        if not ownerships:
            instance.ownerships.all().delete()

        ownership_objs = []
        for owner_data in ownerships:
            owner = owner_data.pop("owner")
            owner_obj, _ = Ownership.objects.update_or_create(apartment=instance, owner=owner, defaults={**owner_data})
            ownership_objs.append(owner_obj)

        # Using `instance.ownerships.set(ownership_objs)` does not work here
        # due to the `Ownership.apartment` field isn't nullable, so the set method fails silently
        for ownership in instance.ownerships.all():
            if ownership not in ownership_objs:
                ownership.delete()

        return instance

    class Meta:
        model = Apartment
        fields = [
            "id",
            "state",
            "type",
            "surface_area",
            "shares",
            "links",
            "address",
            "prices",
            "completion_date",
            "ownerships",
            "notes",
            "building",
        ]


class ApartmentListSerializer(ApartmentDetailSerializer):
    type = serializers.CharField(source="apartment_type.value")

    class Meta:
        model = Apartment
        fields = [
            "id",
            "state",
            "type",
            "surface_area",
            "address",
            "completion_date",
            "ownerships",
            "links",
        ]


class ApartmentViewSet(HitasModelViewSet):
    serializer_class = ApartmentDetailSerializer
    list_serializer_class = ApartmentListSerializer
    model_class = Apartment

    def get_detail_queryset(self):
        return self.get_list_queryset().only(
            "uuid",
            "state",
            "surface_area",
            "street_address",
            "apartment_number",
            "floor",
            "stair",
            "share_number_start",
            "share_number_end",
            "debt_free_purchase_price",
            "primary_loan_amount",
            "purchase_price",
            "first_purchase_date",
            "second_purchase_date",
            "additional_work_during_construction",
            "loans_during_construction",
            "interest_during_construction",
            "debt_free_purchase_price_during_construction",
            "notes",
            "completion_date",
            "building__uuid",
            "building__real_estate__uuid",
            "apartment_type__uuid",
            "apartment_type__value",
            "apartment_type__legacy_code_number",
            "apartment_type__description",
            "building__real_estate__housing_company__uuid",
            "building__real_estate__housing_company__display_name",
            "building__real_estate__housing_company__postal_code__value",
            "building__real_estate__housing_company__postal_code__city",
        )

    def get_list_queryset(self):
        hc_id = self._lookup_model_id_by_uuid(HousingCompany, "housing_company_uuid")

        return (
            Apartment.objects.filter(building__real_estate__housing_company__id=hc_id)
            .prefetch_related("ownerships", "ownerships__owner")
            .select_related(
                "building",
                "building__real_estate",
                "apartment_type",
                "building__real_estate__housing_company",
                "building__real_estate__housing_company__postal_code",
            )
            .only(
                "uuid",
                "state",
                "surface_area",
                "street_address",
                "apartment_number",
                "floor",
                "stair",
                "completion_date",
                "apartment_type__value",
                "building__uuid",
                "building__real_estate__uuid",
                "building__real_estate__housing_company__uuid",
                "building__real_estate__housing_company__display_name",
                "building__real_estate__housing_company__postal_code__value",
                "building__real_estate__housing_company__postal_code__city",
            )
            .order_by("id")
        )
