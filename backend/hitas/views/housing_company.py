from collections import defaultdict
from typing import Any, Dict, List, Optional

from django.db.models import Min
from enumfields.drf.serializers import EnumSupportSerializerMixin
from rest_framework import serializers

from hitas.models import Building, HousingCompany
from hitas.models.housing_company import HousingCompanyState
from hitas.utils import safe_attrgetter
from hitas.views.codes import BuildingTypeSerializer, DeveloperSerializer, FinancingMethodSerializer
from hitas.views.helpers import AddressSerializer, HitasDecimalField, HitasModelViewSet, ValueOrNullField
from hitas.views.property_manager import PropertyManagerSerializer
from hitas.views.real_estate import RealEstateSerializer


class HousingCompanyNameSerializer(serializers.Serializer):
    display = serializers.CharField(source="display_name")
    official = serializers.CharField(source="official_name")


class HousingCompanyAcquisitionPriceSerializer(serializers.Serializer):
    initial = HitasDecimalField(source="acquisition_price")
    realized = HitasDecimalField(source="realized_acquisition_price", required=False, allow_null=True)


class HousingCompanyStateField(serializers.Field):
    def to_representation(self, value):
        return value.name.lower()

    def to_internal_value(self, data):
        try:
            return HousingCompanyState[data.upper()]
        except KeyError:
            raise serializers.ValidationError(f"Unsupported state '{data}'.")


class HousingCompanyDetailSerializer(EnumSupportSerializerMixin, serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = HousingCompanyNameSerializer(source="*")
    state = HousingCompanyStateField()
    address = AddressSerializer(source="*")
    area = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    real_estates = serializers.SerializerMethodField()
    financing_method = FinancingMethodSerializer()
    building_type = BuildingTypeSerializer()
    developer = DeveloperSerializer()
    property_manager = PropertyManagerSerializer()
    acquisition_price = HousingCompanyAcquisitionPriceSerializer(source="*")
    notes = ValueOrNullField(required=False)
    legacy_id = ValueOrNullField(read_only=True)
    last_modified = serializers.SerializerMethodField(read_only=True)

    def get_id(self, obj: HousingCompany) -> str:
        return obj.uuid.hex

    def get_area(self, obj: HousingCompany) -> Dict[str, any]:
        return {"name": obj.postal_code.description, "cost_area": obj.area}

    def get_date(self, obj: HousingCompany) -> Optional[str]:
        """
        SerializerMethodField is used instead of DateField due to
        date being an annotated value because of that it's left out in e.g. create action responses
        """
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

    def get_real_estates(self, obj: HousingCompany) -> List[Dict[str, Any]]:
        """Select all buildings for this housing company with one query instead of having one query per property"""
        buildings_by_real_estate = defaultdict(list)
        for b in (
            Building.objects.select_related("postal_code")
            .only(
                "street_address",
                "postal_code__value",
                "building_identifier",
                "real_estate__id",
                "completion_date",
            )
            .filter(real_estate__housing_company_id=obj.id)
        ):
            buildings_by_real_estate[b.real_estate_id].append(b)

        # Fetch real estates
        query = obj.real_estates.select_related("postal_code").only(
            "street_address",
            "postal_code__value",
            "property_identifier",
            "housing_company__id",
        )

        return RealEstateSerializer(query.all(), context={"buildings": buildings_by_real_estate}, many=True).data

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

    class Meta:
        model = HousingCompany
        fields = ["id", "name", "state", "address", "area", "date"]


class HousingCompanyViewSet(HitasModelViewSet):
    serializer_class = HousingCompanyDetailSerializer
    list_serializer_class = HousingCompanyListSerializer

    def get_list_queryset(self):
        return (
            HousingCompany.objects.select_related(
                "postal_code",
            )
            .annotate(date=Min("real_estates__buildings__completion_date"))
            .only("uuid", "state", "postal_code__value", "postal_code__description", "display_name", "street_address")
            .order_by("id")
        )

    def get_detail_queryset(self):
        return (
            HousingCompany.objects.select_related(
                "postal_code",
                "financing_method",
                "developer",
                "building_type",
                "property_manager",
                "property_manager__postal_code",
                "last_modified_by",
            )
            .annotate(date=Min("real_estates__buildings__completion_date"))
            .only(
                "uuid",
                "state",
                "postal_code__value",
                "postal_code__description",
                "financing_method__value",
                "financing_method__description",
                "financing_method__legacy_code_number",
                "developer__value",
                "developer__description",
                "developer__legacy_code_number",
                "building_type__value",
                "building_type__description",
                "building_type__legacy_code_number",
                "property_manager__name",
                "property_manager__email",
                "property_manager__street_address",
                "property_manager__postal_code__value",
                "property_manager__postal_code__description",
                "display_name",
                "street_address",
                "business_id",
                "official_name",
                "acquisition_price",
                "realized_acquisition_price",
                "primary_loan",
                "sales_price_catalogue_confirmation_date",
                "notification_date",
                "legacy_id",
                "notes",
                "last_modified_by__username",
                "last_modified_by__first_name",
                "last_modified_by__last_name",
                "last_modified_datetime",
            )
        )
