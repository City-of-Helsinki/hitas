import datetime
from typing import Any, Dict, Optional

from django.db.models import Min, Prefetch
from django_filters.rest_framework import filters
from enumfields.drf.serializers import EnumSupportSerializerMixin
from rest_framework import serializers

from hitas.models import Building, HousingCompany, HousingCompanyState, RealEstate
from hitas.utils import safe_attrgetter
from hitas.views.codes import (
    ReadOnlyBuildingTypeSerializer,
    ReadOnlyDeveloperSerializer,
    ReadOnlyFinancingMethodSerializer,
)
from hitas.views.property_manager import ReadOnlyPropertyManagerSerializer
from hitas.views.real_estate import RealEstateSerializer
from hitas.views.utils import (
    HitasAddressSerializer,
    HitasDecimalField,
    HitasEnumField,
    HitasFilterSet,
    HitasModelSerializer,
    HitasModelViewSet,
    ValueOrNullField,
)


class HousingCompanyFilterSet(HitasFilterSet):
    display_name = filters.CharFilter(lookup_expr="icontains")
    street_address = filters.CharFilter(lookup_expr="icontains")
    postal_code = filters.CharFilter(field_name="postal_code__value")
    property_manager = filters.CharFilter(field_name="property_manager__name", lookup_expr="icontains")
    developer = filters.CharFilter(field_name="developer__value", lookup_expr="icontains")

    class Meta:
        model = HousingCompany
        fields = ["display_name", "street_address", "postal_code", "property_manager", "developer"]


class HousingCompanyNameSerializer(serializers.Serializer):
    display = serializers.CharField(source="display_name")
    official = serializers.CharField(source="official_name")


class HousingCompanyAcquisitionPriceSerializer(serializers.Serializer):
    initial = HitasDecimalField(source="acquisition_price")
    realized = HitasDecimalField(source="realized_acquisition_price", required=False, allow_null=True)


class HousingCompanyDetailSerializer(EnumSupportSerializerMixin, HitasModelSerializer):
    name = HousingCompanyNameSerializer(source="*")
    state = HitasEnumField(enum=HousingCompanyState)
    address = HitasAddressSerializer(source="*")
    area = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    real_estates = RealEstateSerializer(many=True, read_only=True)
    financing_method = ReadOnlyFinancingMethodSerializer()
    building_type = ReadOnlyBuildingTypeSerializer()
    developer = ReadOnlyDeveloperSerializer()
    property_manager = ReadOnlyPropertyManagerSerializer()
    acquisition_price = HousingCompanyAcquisitionPriceSerializer(source="*")
    notes = ValueOrNullField(required=False)
    legacy_id = ValueOrNullField(read_only=True)
    last_modified = serializers.SerializerMethodField(read_only=True)

    def get_area(self, obj: HousingCompany) -> Dict[str, any]:
        return {"name": obj.postal_code.city, "cost_area": obj.postal_code.cost_area}

    def get_date(self, obj: HousingCompany) -> Optional[datetime.date]:
        """SerializerMethodField is used instead of DateField due to date being an annotated value"""
        return getattr(obj, "date", None)

    def get_last_modified(self, obj: HousingCompany) -> Dict[str, Any]:
        return {
            "user": {
                "username": safe_attrgetter(obj, "last_modified_by.username", default=None),
                "first_name": safe_attrgetter(obj, "last_modified_by.first_name", default=None),
                "last_name": safe_attrgetter(obj, "last_modified_by.last_name", default=None),
            },
            "datetime": obj.last_modified_datetime,
        }

    class Meta:
        model = HousingCompany
        fields = [
            "id",
            "business_id",
            "name",
            "state",
            "address",
            "area",
            "date",
            "real_estates",
            "financing_method",
            "building_type",
            "developer",
            "property_manager",
            "acquisition_price",
            "primary_loan",
            "sales_price_catalogue_confirmation_date",
            "notes",
            "legacy_id",
            "notification_date",
            "last_modified",
        ]


class HousingCompanyListSerializer(HousingCompanyDetailSerializer):
    name = serializers.CharField(source="display_name", max_length=1024)
    date = serializers.DateField()

    class Meta:
        model = HousingCompany
        fields = ["id", "name", "state", "address", "area", "date"]


class HousingCompanyViewSet(HitasModelViewSet):
    serializer_class = HousingCompanyDetailSerializer
    list_serializer_class = HousingCompanyListSerializer
    model_class = HousingCompany

    def get_list_queryset(self):
        return (
            HousingCompany.objects.select_related("postal_code")
            .only(
                "uuid",
                "display_name",
                "state",
                "street_address",
                "postal_code__value",
                "postal_code__city",
                "postal_code__cost_area",
            )
            .annotate(date=Min("real_estates__buildings__apartments__completion_date"))
            .order_by("id")
        )

    def get_detail_queryset(self):
        return (
            HousingCompany.objects.prefetch_related(
                Prefetch(
                    "real_estates",
                    queryset=RealEstate.objects.prefetch_related(
                        Prefetch("buildings", queryset=Building.objects.select_related("postal_code"))
                    ).select_related("postal_code"),
                )
            )
            .select_related(
                "postal_code",
                "financing_method",
                "developer",
                "building_type",
                "property_manager",
                "last_modified_by",
            )
            .only(
                "uuid",
                "business_id",
                "display_name",
                "official_name",
                "state",
                "street_address",
                "acquisition_price",
                "realized_acquisition_price",
                "primary_loan",
                "sales_price_catalogue_confirmation_date",
                "notes",
                "legacy_id",
                "notification_date",
                "last_modified_datetime",
                "financing_method__uuid",
                "financing_method__value",
                "financing_method__description",
                "financing_method__legacy_code_number",
                "developer__uuid",
                "developer__value",
                "developer__description",
                "developer__legacy_code_number",
                "building_type__uuid",
                "building_type__value",
                "building_type__description",
                "building_type__legacy_code_number",
                "property_manager__uuid",
                "property_manager__name",
                "property_manager__email",
                "property_manager__street_address",
                "property_manager__postal_code",
                "property_manager__city",
                "last_modified_by__id",
                "last_modified_by__username",
                "last_modified_by__first_name",
                "last_modified_by__last_name",
                "postal_code__uuid",
                "postal_code__value",
                "postal_code__city",
                "postal_code__cost_area",
            )
            .annotate(date=Min("real_estates__buildings__apartments__completion_date"))
        )

    def get_filterset_class(self):
        return HousingCompanyFilterSet
