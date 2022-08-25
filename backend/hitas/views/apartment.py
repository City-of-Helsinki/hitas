from collections import OrderedDict
from typing import Any, Union

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import filters
from enumfields.drf import EnumSupportSerializerMixin
from rest_framework import serializers

from hitas.models import Apartment, Building, HousingCompany, Owner
from hitas.models.apartment import ApartmentState
from hitas.models.utils import validate_share_numbers
from hitas.views.codes import ApartmentTypeSerializer
from hitas.views.owner import OwnerSerializer
from hitas.views.utils import (
    HitasAddressSerializer,
    HitasDecimalField,
    HitasEnumField,
    HitasFilterSet,
    HitasModelSerializer,
    HitasModelViewSet,
    UUIDRelatedField,
)


class ApartmentFilterSet(HitasFilterSet):
    housing_company_name = filters.CharFilter(
        field_name="building__real_estate__housing_company__display_name", lookup_expr="icontains"
    )
    street_address = filters.CharFilter(lookup_expr="icontains")
    postal_code = filters.CharFilter(field_name="postal_code__value")
    owner_name = filters.CharFilter(method="owner_name_filter")
    owner_social_security_number = filters.CharFilter(
        field_name="owners__person__social_security_number", lookup_expr="icontains"
    )

    def owner_name_filter(self, queryset, name, value):
        return queryset.filter(
            Q(owners__person__first_name__icontains=value) | Q(owners__person__last_name__icontains=value)
        )

    class Meta:
        model = Apartment
        fields = ["housing_company_name", "street_address", "postal_code", "owner_name", "owner_social_security_number"]


class HousingCompanySerializer(EnumSupportSerializerMixin, HitasModelSerializer):
    name = serializers.CharField(source="display_name")

    class Meta:
        model = HousingCompany
        fields = ["id", "name"]


class ApartmentDetailSerializer(EnumSupportSerializerMixin, HitasModelSerializer):
    state = HitasEnumField(enum=ApartmentState)
    apartment_type = ApartmentTypeSerializer()
    address = HitasAddressSerializer(source="*")
    date = serializers.DateField(source="building.completion_date", read_only=True)
    surface_area = HitasDecimalField()

    debt_free_purchase_price = HitasDecimalField(required=False, allow_null=True)
    purchase_price = HitasDecimalField(required=False, allow_null=True)
    acquisition_price = HitasDecimalField(required=False, allow_null=True)
    primary_loan_amount = HitasDecimalField(required=False, allow_null=True)
    loans_during_construction = HitasDecimalField(required=False, allow_null=True)
    interest_during_construction = HitasDecimalField(required=False, allow_null=True)

    building = UUIDRelatedField(queryset=Building.objects.all())
    real_estate = serializers.SerializerMethodField()
    housing_company = HousingCompanySerializer(source="building.real_estate.housing_company", read_only=True)
    owners = OwnerSerializer(many=True, read_only=False)

    def get_real_estate(self, instance: Apartment) -> str:
        return instance.building.real_estate.uuid.hex

    def validate_owners(self, owners: OrderedDict):
        if owners == []:
            return owners

        for owner in owners:
            op = owner["ownership_percentage"]
            if not 0 < op <= 100:
                raise ValidationError(
                    {
                        "ownership_percentage": _(
                            "Ownership percentage greater than 0 and less than or equal to 100. (Given value was {})"
                        ).format(op)
                    },
                )

        if (sum_op := sum(o["ownership_percentage"] for o in owners)) != 100:
            raise ValidationError(
                {
                    "ownership_percentage": _(
                        "Ownership percentage of all owners combined must be equal to 100. (Given sum was {})"
                    ).format(sum_op)
                }
            )

        return owners

    def validate(self, data: Union[OrderedDict, Apartment]):
        if type(data) == OrderedDict:
            validate_share_numbers(start=data.get("share_number_start"), end=data.get("share_number_end"))
        else:
            validate_share_numbers(start=data.share_number_start, end=data.share_number_end)
        return data

    def create(self, validated_data: dict[str, Any]):
        owners = validated_data.pop("owners")
        instance: Apartment = super().create(validated_data)
        for owner_data in owners:
            Owner.objects.create(apartment=instance, **owner_data)
        return instance

    def update(self, instance: Apartment, validated_data: dict[str, Any]):
        owners = validated_data.pop("owners")
        instance: Apartment = super().update(instance, validated_data)

        if not owners:
            instance.owners.all().delete()

        owner_objs = []
        for owner_data in owners:
            person = owner_data.pop("person")
            owner_obj, _ = Owner.objects.update_or_create(apartment=instance, person=person, defaults={**owner_data})
            owner_objs.append(owner_obj)

        # Using `instance.owners.set(owner_objs)` does not work here
        # due to the `Owner.apartment` field isn't nullable, so the set method fails silently
        for owner in instance.owners.all():
            if owner not in owner_objs:
                owner.delete()

        return instance

    class Meta:
        model = Apartment
        fields = [
            "id",
            "state",
            "apartment_type",
            "surface_area",
            "share_number_start",
            "share_number_end",
            "address",
            "apartment_number",
            "floor",
            "stair",
            "date",
            "debt_free_purchase_price",
            "purchase_price",
            "acquisition_price",
            "primary_loan_amount",
            "loans_during_construction",
            "interest_during_construction",
            "building",
            "real_estate",
            "housing_company",
            "owners",
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
            "date",
            "housing_company",
            "owners",
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
            "building__uuid",
            "building__completion_date",
            "building__real_estate__housing_company__uuid",
            "building__real_estate__housing_company__display_name",
            "building__real_estate__uuid",
            "apartment_type__uuid",
            "apartment_type__value",
            "apartment_type__legacy_code_number",
            "apartment_type__description",
            "postal_code__value",
            "postal_code__city",
        )

    def get_list_queryset(self):
        return (
            Apartment.objects.prefetch_related("owners", "owners__person")
            .select_related(
                "postal_code",
                "building",
                "building__real_estate",
                "apartment_type",
                "building__real_estate__housing_company",
            )
            .only(
                "uuid",
                "state",
                "surface_area",
                "street_address",
                "apartment_number",
                "floor",
                "stair",
                "building__completion_date",
                "building__real_estate__housing_company__uuid",
                "building__real_estate__housing_company__display_name",
                "apartment_type__value",
                "postal_code__value",
                "postal_code__city",
            )
        )

    def get_filterset_class(self):
        return ApartmentFilterSet
