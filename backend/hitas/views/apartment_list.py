from typing import Optional

from django.db import models
from django.db.models import Case, Count, Prefetch, Q, When
from django_filters.rest_framework import BooleanFilter
from enumfields.drf import EnumSupportSerializerMixin
from rest_framework import mixins, serializers, viewsets

from hitas.models import Apartment, ConditionOfSale, Ownership
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
)


class ApartmentFilterSet(HitasFilterSet):
    housing_company_name = HitasCharFilter(
        field_name="building__real_estate__housing_company__display_name", lookup_expr="icontains"
    )
    street_address = HitasCharFilter(lookup_expr="icontains")
    postal_code = HitasPostalCodeFilter(field_name="building__real_estate__housing_company__postal_code__value")
    owner_name = HitasCharFilter(field_name="ownerships__owner__name", lookup_expr="icontains")
    owner_identifier = HitasCharFilter(
        field_name="ownerships__owner__identifier", lookup_expr="icontains", max_length=11
    )
    sales_condition = BooleanFilter()

    class Meta:
        model = Apartment
        fields = [
            "housing_company_name",
            "street_address",
            "postal_code",
            "owner_name",
            "owner_identifier",
            "sales_condition",
        ]


class ApartmentListSerializer(EnumSupportSerializerMixin, HitasModelSerializer):
    state = HitasEnumField(enum=ApartmentState)
    type = serializers.SerializerMethodField()
    address = ApartmentHitasAddressSerializer(source="*")
    surface_area = HitasDecimalField()
    completion_date = serializers.DateField(required=False, allow_null=True)
    ownerships = OwnershipSerializer(many=True, read_only=False)
    links = serializers.SerializerMethodField()

    @staticmethod
    def get_type(instance: Apartment) -> Optional[str]:
        return getattr(getattr(instance, "apartment_type", None), "value", None)

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
            Apartment.objects.prefetch_related(
                Prefetch(
                    "ownerships",
                    Ownership.objects.select_related("owner").all(),
                ),
                Prefetch(
                    "ownerships__conditions_of_sale_new",
                    ConditionOfSale.objects.all(),
                ),
                Prefetch(
                    "ownerships__conditions_of_sale_old",
                    ConditionOfSale.objects.all(),
                ),
            )
            .select_related(
                "building",
                "building__real_estate",
                "apartment_type",
                "building__real_estate__housing_company",
                "building__real_estate__housing_company__postal_code",
            )
            .alias(
                number_of_conditions_of_sale=(
                    Count("ownerships__conditions_of_sale_new") + Count("ownerships__conditions_of_sale_old")
                ),
            )
            .annotate(
                sales_condition=Case(
                    When(condition=Q(number_of_conditions_of_sale__gt=0), then=True),
                    default=False,
                    output_field=models.BooleanField(),
                ),
            )
            .order_by("apartment_number", "id")
        )

    def get_filterset_class(self):
        return ApartmentFilterSet
