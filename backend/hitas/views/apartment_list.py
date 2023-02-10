from datetime import datetime
from typing import Optional

from django.db import models
from django.db.models import Case, Count, Prefetch, Q, When
from django_filters.rest_framework import BooleanFilter
from enumfields.drf import EnumSupportSerializerMixin
from rest_framework import mixins, serializers, viewsets

from hitas.models import Apartment, ConditionOfSale, Ownership
from hitas.models.apartment import ApartmentState
from hitas.views.apartment import create_links
from hitas.views.ownership import OwnershipSerializer
from hitas.views.utils import (
    ApartmentHitasAddressSerializer,
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
    sell_by_date = serializers.SerializerMethodField()
    has_grace_period = serializers.SerializerMethodField()

    @staticmethod
    def get_type(instance: Apartment) -> Optional[str]:
        return getattr(getattr(instance, "apartment_type", None), "value", None)

    @staticmethod
    def get_links(instance: Apartment):
        return create_links(instance)

    @staticmethod
    def get_sell_by_date(instance: Apartment) -> Optional[datetime.date]:
        return instance.sell_by_date

    @staticmethod
    def get_has_grace_period(instance: Apartment) -> Optional[datetime.date]:
        return instance.has_grace_period

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
            "sell_by_date",
            "has_grace_period",
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
                    ConditionOfSale.objects.select_related(
                        "new_ownership__apartment",
                        "old_ownership__apartment",
                    ).all(),
                ),
                Prefetch(
                    "ownerships__conditions_of_sale_old",
                    ConditionOfSale.objects.select_related(
                        "new_ownership__apartment",
                        "old_ownership__apartment",
                    ).all(),
                ),
            )
            .select_related(
                "apartment_type",
                "building",
                "building__real_estate",
                "building__real_estate__housing_company",
                "building__real_estate__housing_company__postal_code",
            )
            .alias(
                number_of_conditions_of_sale=(
                    Count(
                        "ownerships__conditions_of_sale_new",
                        filter=Q(ownerships__conditions_of_sale_new__deleted__isnull=True),
                    )
                    + Count(
                        "ownerships__conditions_of_sale_old",
                        filter=Q(ownerships__conditions_of_sale_old__deleted__isnull=True),
                    )
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
