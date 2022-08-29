from collections import OrderedDict
from typing import Any, Union

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import filters
from enumfields.drf import EnumSupportSerializerMixin
from rest_framework import serializers
from rest_framework.fields import SkipField, empty

from hitas.models import Apartment, Building, HousingCompany, Ownership
from hitas.models.apartment import ApartmentState
from hitas.models.utils import validate_share_numbers
from hitas.views.codes import ApartmentTypeSerializer
from hitas.views.ownership import OwnershipSerializer
from hitas.views.utils import (
    HitasDecimalField,
    HitasEnumField,
    HitasFilterSet,
    HitasModelSerializer,
    HitasModelViewSet,
    HitasUUIDFilter,
    UUIDRelatedField,
)


class ApartmentFilterSet(HitasFilterSet):
    housing_company = HitasUUIDFilter(field_name="building__real_estate__housing_company__uuid")
    housing_company_name = filters.CharFilter(
        field_name="building__real_estate__housing_company__display_name", lookup_expr="icontains"
    )
    street_address = filters.CharFilter(lookup_expr="icontains")
    postal_code = filters.CharFilter(field_name="building__real_estate__housing_company__postal_code__value")
    owner_name = filters.CharFilter(method="owner_name_filter")
    owner_social_security_number = filters.CharFilter(
        field_name="ownerships__owner__social_security_number", lookup_expr="icontains"
    )

    def owner_name_filter(self, queryset, name, value):
        return queryset.filter(
            Q(ownerships__owner__first_name__icontains=value) | Q(ownerships__owner__last_name__icontains=value)
        )

    class Meta:
        model = Apartment
        fields = ["housing_company_name", "street_address", "postal_code", "owner_name", "owner_social_security_number"]


class HousingCompanySerializer(HitasModelSerializer):
    name = serializers.CharField(source="display_name")

    class Meta:
        model = HousingCompany
        fields = ["id", "name"]


class ApartmentHitasAddressSerializer(serializers.Serializer):
    street_address = serializers.CharField()
    postal_code = serializers.CharField(source="building.real_estate.housing_company.postal_code.value", read_only=True)
    city = serializers.CharField(source="building.real_estate.housing_company.city", read_only=True)


class SharesSerializer(serializers.Serializer):
    start = serializers.IntegerField(source="share_number_start", min_value=1)
    end = serializers.IntegerField(source="share_number_end", min_value=1)
    total = serializers.SerializerMethodField()

    def get_total(self, instance: Apartment) -> int:
        return instance.shares_count

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


class ApartmentDetailSerializer(EnumSupportSerializerMixin, HitasModelSerializer):
    state = HitasEnumField(enum=ApartmentState)
    apartment_type = ApartmentTypeSerializer()
    address = ApartmentHitasAddressSerializer(source="*")
    completion_date = serializers.DateField(required=False, allow_null=True)
    surface_area = HitasDecimalField()
    shares = SharesSerializer(source="*", required=False, allow_null=True)

    debt_free_purchase_price = HitasDecimalField(required=False, allow_null=True)
    purchase_price = HitasDecimalField(required=False, allow_null=True)
    acquisition_price = HitasDecimalField(required=False, allow_null=True)
    primary_loan_amount = HitasDecimalField(required=False, allow_null=True)
    loans_during_construction = HitasDecimalField(required=False, allow_null=True)
    interest_during_construction = HitasDecimalField(required=False, allow_null=True)

    building = UUIDRelatedField(queryset=Building.objects.all())
    real_estate = serializers.SerializerMethodField()
    housing_company = HousingCompanySerializer(source="building.real_estate.housing_company", read_only=True)
    ownerships = OwnershipSerializer(many=True, read_only=False)

    def get_real_estate(self, instance: Apartment) -> str:
        return instance.building.real_estate.uuid.hex

    def validate_ownerships(self, ownerships: OrderedDict):
        if not ownerships:
            return ownerships

        for owner in ownerships:
            op = owner["percentage"]
            if not 0 < op <= 100:
                raise ValidationError(
                    {
                        "percentage": _(
                            "Ownership percentage greater than 0 and less than or equal to 100. (Given value was {})"
                        ).format(op)
                    },
                )

        if (sum_op := sum(o["percentage"] for o in ownerships)) != 100:
            raise ValidationError(
                {
                    "percentage": _(
                        "Ownership percentage of all ownerships combined must be equal to 100. (Given sum was {})"
                    ).format(sum_op)
                }
            )

        return ownerships

    def validate(self, data: Union[OrderedDict, Apartment]):
        if type(data) == OrderedDict:
            validate_share_numbers(start=data.get("share_number_start"), end=data.get("share_number_end"))
        else:
            validate_share_numbers(start=data.share_number_start, end=data.share_number_end)
        return data

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
            "apartment_type",
            "surface_area",
            "shares",
            "address",
            "apartment_number",
            "floor",
            "stair",
            "debt_free_purchase_price",
            "purchase_price",
            "acquisition_price",
            "primary_loan_amount",
            "loans_during_construction",
            "interest_during_construction",
            "completion_date",
            "building",
            "real_estate",
            "housing_company",
            "ownerships",
            "notes",
        ]


class ApartmentListSerializer(ApartmentDetailSerializer):
    apartment_type = serializers.CharField(source="apartment_type.value")
    housing_company = HousingCompanySerializer(source="building.real_estate.housing_company", read_only=True)

    class Meta:
        model = Apartment
        fields = [
            "id",
            "state",
            "apartment_type",
            "surface_area",
            "address",
            "apartment_number",
            "stair",
            "completion_date",
            "housing_company",
            "ownerships",
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
            "purchase_price",
            "acquisition_price",
            "primary_loan_amount",
            "loans_during_construction",
            "interest_during_construction",
            "notes",
            "completion_date",
            "building__uuid",
            "building__real_estate__housing_company__uuid",
            "building__real_estate__housing_company__display_name",
            "building__real_estate__uuid",
            "apartment_type__uuid",
            "apartment_type__value",
            "apartment_type__legacy_code_number",
            "apartment_type__description",
            "building__real_estate__housing_company__postal_code__value",
            "building__real_estate__housing_company__postal_code__city",
        )

    def get_list_queryset(self):
        return (
            Apartment.objects.prefetch_related("ownerships", "ownerships__owner")
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
                "building__real_estate__housing_company__uuid",
                "building__real_estate__housing_company__display_name",
                "apartment_type__value",
                "building__real_estate__housing_company__postal_code__value",
                "building__real_estate__housing_company__postal_code__city",
            )
            .order_by("id")
        )

    def get_filterset_class(self):
        return ApartmentFilterSet
