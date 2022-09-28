from django.db.models import Q
from enumfields.drf import EnumSupportSerializerMixin
from rest_framework import mixins, serializers, viewsets

from hitas.models import Apartment
from hitas.models.apartment import ApartmentState
from hitas.views.apartment import ApartmentHitasAddressSerializer, create_links
from hitas.views.ownership import OwnershipSerializer
from hitas.views.utils import (
    HitasCharFilter,
    HitasDecimalField,
    HitasEnumField,
    HitasFilterSet,
    HitasModelMixin,
    HitasModelSerializer,
    HitasPostalCodeFilter,
    HitasSSNFilter,
)


class ApartmentFilterSet(HitasFilterSet):
    housing_company_name = HitasCharFilter(
        field_name="building__real_estate__housing_company__display_name", lookup_expr="icontains"
    )
    street_address = HitasCharFilter(lookup_expr="icontains")
    postal_code = HitasPostalCodeFilter(field_name="building__real_estate__housing_company__postal_code__value")
    owner_name = HitasCharFilter(method="owner_name_filter")
    owner_social_security_number = HitasSSNFilter(
        field_name="ownerships__owner__social_security_number", lookup_expr="icontains"
    )

    def owner_name_filter(self, queryset, name, value):
        return queryset.filter(
            Q(ownerships__owner__first_name__icontains=value) | Q(ownerships__owner__last_name__icontains=value)
        )

    class Meta:
        model = Apartment
        fields = ["housing_company_name", "street_address", "postal_code", "owner_name", "owner_social_security_number"]


class ApartmentListSerializer(EnumSupportSerializerMixin, HitasModelSerializer):
    state = HitasEnumField(enum=ApartmentState)
    type = serializers.CharField(source="apartment_type.value")
    address = ApartmentHitasAddressSerializer(source="*")
    surface_area = HitasDecimalField()
    completion_date = serializers.DateField(required=False, allow_null=True)
    ownerships = OwnershipSerializer(many=True, read_only=False)
    links = serializers.SerializerMethodField()

    def get_links(self, instance: Apartment):
        return create_links(instance)

    class Meta:
        model = Apartment
        fields = [
            "id",
            "links",
            "state",
            "type",
            "surface_area",
            "address",
            "completion_date",
            "ownerships",
        ]


class ApartmentListViewSet(HitasModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    list_serializer_class = ApartmentListSerializer
    model_class = Apartment

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
                "building__uuid",
                "building__real_estate__uuid",
                "building__real_estate__housing_company__uuid",
                "apartment_type__value",
                "building__real_estate__housing_company__display_name",
                "building__real_estate__housing_company__postal_code__value",
                "building__real_estate__housing_company__postal_code__city",
            )
            .order_by("id")
        )

    def get_filterset_class(self):
        return ApartmentFilterSet
