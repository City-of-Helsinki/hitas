import datetime
from typing import Any, Dict, Optional

from django.db.models import F, Min, Prefetch, Sum
from django.db.models.functions import Round
from enumfields.drf.serializers import EnumSupportSerializerMixin
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from hitas.models import (
    HousingCompany,
    HousingCompanyConstructionPriceImprovement,
    HousingCompanyMarketPriceImprovement,
    HousingCompanyState,
    RealEstate,
)
from hitas.models.utils import validate_business_id
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
    HitasCharFilter,
    HitasDecimalField,
    HitasEnumField,
    HitasFilterSet,
    HitasModelSerializer,
    HitasModelViewSet,
    HitasNumberFilter,
    HitasPostalCodeFilter,
    ValueOrNullField,
)
from hitas.views.utils.merge import merge_model
from hitas.views.utils.serializers import YearMonthSerializer


class HousingCompanyFilterSet(HitasFilterSet):
    display_name = HitasCharFilter(lookup_expr="icontains")
    street_address = HitasCharFilter(lookup_expr="icontains")
    postal_code = HitasPostalCodeFilter(field_name="postal_code__value")
    property_manager = HitasCharFilter(field_name="property_manager__name", lookup_expr="icontains")
    developer = HitasCharFilter(field_name="developer__value", lookup_expr="icontains")
    archive_id = HitasNumberFilter(field_name="id", min_value=1)

    class Meta:
        model = HousingCompany
        fields = ["display_name", "street_address", "postal_code", "property_manager", "developer", "archive_id"]


class HousingCompanyNameSerializer(serializers.Serializer):
    display = serializers.CharField(source="display_name")
    official = serializers.CharField(source="official_name")

    def _validate_qs(self):
        qs = HousingCompany.objects
        if self.parent.instance:
            qs = qs.exclude(id=self.parent.instance.id)
        return qs

    def validate_display(self, value):
        if self._validate_qs().filter(display_name=value).exists():
            raise ValidationError(
                f"Display name provided is already in use. Conflicting display name: '{value}'.", code="unique"
            )

        return value

    def validate_official(self, value):
        if self._validate_qs().filter(official_name=value).exists():
            raise ValidationError(
                f"Official name provided is already in use. Conflicting official name: '{value}'.", code="unique"
            )

        return value


class ImprovementSerializer(serializers.ModelSerializer):
    completion_date = YearMonthSerializer()

    class Meta:
        model = HousingCompanyMarketPriceImprovement
        fields = [
            "name",
            "completion_date",
            "value",
        ]


class HousingCompanyImprovementSerializer(serializers.Serializer):
    market_price_index = ImprovementSerializer(many=True, source="market_price_improvements")
    construction_price_index = ImprovementSerializer(many=True, source="construction_price_improvements")


class HousingCompanyDetailSerializer(EnumSupportSerializerMixin, HitasModelSerializer):
    name = HousingCompanyNameSerializer(source="*")
    state = HitasEnumField(enum=HousingCompanyState)
    business_id = ValueOrNullField(allow_null=True, required=False)
    address = HitasAddressSerializer(source="*")
    area = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    real_estates = RealEstateSerializer(many=True, read_only=True)
    financing_method = ReadOnlyFinancingMethodSerializer()
    building_type = ReadOnlyBuildingTypeSerializer()
    developer = ReadOnlyDeveloperSerializer()
    property_manager = ReadOnlyPropertyManagerSerializer(allow_null=True, required=False)
    acquisition_price = HitasDecimalField()
    notes = serializers.CharField(required=False, allow_blank=True)
    archive_id = serializers.IntegerField(source="id", read_only=True)
    last_modified = serializers.SerializerMethodField(read_only=True)
    summary = serializers.SerializerMethodField()
    improvements = HousingCompanyImprovementSerializer(source="*")

    def create(self, validated_data):
        mpi = validated_data.pop("market_price_improvements")
        cpi = validated_data.pop("construction_price_improvements")

        instance: HousingCompany = super().create(validated_data)

        for improvement in mpi:
            HousingCompanyMarketPriceImprovement.objects.create(housing_company=instance, **improvement)
        for improvement in cpi:
            HousingCompanyConstructionPriceImprovement.objects.create(housing_company=instance, **improvement)

        return instance

    def update(self, instance: HousingCompany, validated_data: dict[str, Any]):
        mpi = validated_data.pop("market_price_improvements")
        cpi = validated_data.pop("construction_price_improvements")

        instance: HousingCompany = super().update(instance, validated_data)

        merge_model(
            model_class=HousingCompanyMarketPriceImprovement,
            existing_qs=instance.market_price_improvements.all(),
            wanted=mpi,
            create_defaults={"housing_company": instance},
            equal_fields=["value", "completion_date", "name"],
        )

        merge_model(
            model_class=HousingCompanyConstructionPriceImprovement,
            existing_qs=instance.construction_price_improvements.all(),
            wanted=cpi,
            create_defaults={"housing_company": instance},
            equal_fields=["value", "completion_date", "name"],
        )

        return instance

    def validate_business_id(self, value):
        if value == "":
            value = None
        validate_business_id(value)
        return value

    @staticmethod
    def get_area(obj: HousingCompany) -> Dict[str, any]:
        return {"name": obj.postal_code.city, "cost_area": obj.postal_code.cost_area}

    @staticmethod
    def get_date(obj: HousingCompany) -> Optional[datetime.date]:
        """SerializerMethodField is used instead of DateField due to date being an annotated value"""
        return getattr(obj, "date", None)

    @staticmethod
    def get_summary(obj: HousingCompany) -> Dict[str, int]:
        return {
            "realized_acquisition_price": getattr(obj, "sum_acquisition_price", 0.0) or 0.0,
            "average_price_per_square_meter": getattr(obj, "avg_price_per_square_meter", 0.0) or 0.0,
            "total_surface_area": getattr(obj, "sum_surface_area", 0.0) or 0.0,
            "total_shares": getattr(obj, "sum_total_shares", 0.0) or 0.0,
        }

    @staticmethod
    def get_last_modified(obj: HousingCompany) -> Dict[str, Any]:
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
            "archive_id",
            "notification_date",
            "last_modified",
            "summary",
            "improvements",
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
                    queryset=RealEstate.objects.prefetch_related("buildings").order_by("id"),
                ),
                Prefetch(
                    "market_price_improvements",
                    queryset=HousingCompanyMarketPriceImprovement.objects.only(
                        "name", "value", "completion_date", "housing_company_id"
                    ).order_by("completion_date", "id"),
                ),
                Prefetch(
                    "construction_price_improvements",
                    queryset=HousingCompanyConstructionPriceImprovement.objects.only(
                        "name",
                        "value",
                        "completion_date",
                        "housing_company_id",
                    ).order_by("completion_date", "id"),
                ),
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
                "id",
                "uuid",
                "business_id",
                "display_name",
                "official_name",
                "state",
                "street_address",
                "acquisition_price",
                "primary_loan",
                "sales_price_catalogue_confirmation_date",
                "notes",
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
            .annotate(
                sum_acquisition_price=Sum(
                    F("real_estates__buildings__apartments__debt_free_purchase_price")
                    + F("real_estates__buildings__apartments__primary_loan_amount")
                )
            )
            .annotate(sum_surface_area=Sum("real_estates__buildings__apartments__surface_area"))
            .annotate(avg_price_per_square_meter=Round(F("sum_acquisition_price") / F("sum_surface_area"), precision=2))
            .annotate(
                sum_total_shares=Sum(
                    F("real_estates__buildings__apartments__share_number_end")
                    - F("real_estates__buildings__apartments__share_number_start")
                    + 1
                )
            )
        )

    @staticmethod
    def get_filterset_class():
        return HousingCompanyFilterSet
