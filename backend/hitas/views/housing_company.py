import datetime
from typing import Any, Dict, Optional

from django.db.models import F, OuterRef, Prefetch, Subquery, Sum
from django_filters.rest_framework import BooleanFilter
from enumfields.drf.serializers import EnumSupportSerializerMixin
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from hitas.exceptions import ModelConflict
from hitas.models import (
    Apartment,
    ApartmentSale,
    Building,
    HousingCompany,
    HousingCompanyConstructionPriceImprovement,
    HousingCompanyMarketPriceImprovement,
    HousingCompanyState,
    RealEstate,
)
from hitas.models.utils import validate_business_id
from hitas.utils import RoundWithPrecision, max_if_all_not_null, safe_attrgetter
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
    new_hitas = BooleanFilter(method="new_hitas_filter")

    def new_hitas_filter(self, queryset, name, value):
        if value is None:
            return queryset

        cutoff_date = datetime.date(2011, 1, 1)
        if value:
            return queryset.filter(date__gte=cutoff_date)
        else:
            return queryset.filter(date__lt=cutoff_date)

    class Meta:
        model = HousingCompany
        fields = [
            "display_name",
            "street_address",
            "postal_code",
            "property_manager",
            "developer",
            "archive_id",
            "new_hitas",
        ]


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


class MarketPriceImprovementSerializer(serializers.ModelSerializer):
    completion_date = YearMonthSerializer()
    no_deductions = serializers.BooleanField(default=False)

    class Meta:
        model = HousingCompanyMarketPriceImprovement
        fields = [
            "name",
            "completion_date",
            "value",
            "no_deductions",
        ]


class ConstructionPriceImprovementSerializer(serializers.ModelSerializer):
    completion_date = YearMonthSerializer()

    class Meta:
        model = HousingCompanyConstructionPriceImprovement
        fields = [
            "name",
            "completion_date",
            "value",
        ]


class HousingCompanyImprovementSerializer(serializers.Serializer):
    market_price_index = MarketPriceImprovementSerializer(many=True, source="market_price_improvements")
    construction_price_index = ConstructionPriceImprovementSerializer(
        many=True, source="construction_price_improvements"
    )


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
            equal_fields=["value", "completion_date", "name", "no_deductions"],
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

    class Meta:
        model = HousingCompany
        fields = ["id", "name", "state", "address", "area", "date"]


class HousingCompanyViewSet(HitasModelViewSet):
    serializer_class = HousingCompanyDetailSerializer
    list_serializer_class = HousingCompanyListSerializer
    model_class = HousingCompany

    def perform_destroy(self, instance: HousingCompany) -> None:
        if instance.real_estates.exists():
            raise ModelConflict(
                "Cannot delete a housing company with real estates.",
                error_code="real_estates_on_housing_company",
            )

        super().perform_destroy(instance)

    def get_list_queryset(self):
        return (
            HousingCompany.objects.select_related("postal_code")
            .annotate(
                date=max_if_all_not_null(
                    ref="real_estates__buildings__apartments__completion_date",
                    inf=datetime.date.max,
                )
            )
            .order_by("-date")
        )

    def get_detail_queryset(self):
        return (
            HousingCompany.objects.prefetch_related(
                Prefetch(
                    "real_estates",
                    queryset=RealEstate.objects.order_by("id"),
                ),
                Prefetch(
                    "real_estates__buildings",
                    queryset=Building.objects.order_by("id"),
                ),
                Prefetch(
                    "real_estates__buildings__apartments",
                    queryset=Apartment.objects.order_by("id"),
                ),
                Prefetch(
                    "market_price_improvements",
                    queryset=HousingCompanyMarketPriceImprovement.objects.order_by("completion_date", "id"),
                ),
                Prefetch(
                    "construction_price_improvements",
                    queryset=HousingCompanyConstructionPriceImprovement.objects.order_by("completion_date", "id"),
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
            .alias(
                _acquisition_price=Subquery(
                    queryset=(
                        ApartmentSale.objects.filter(apartment_id=OuterRef("real_estates__buildings__apartments__id"))
                        .order_by("purchase_date")
                        .annotate(
                            _acquisition_price=Sum(F("purchase_price") + F("apartment_share_of_housing_company_loans"))
                        )
                        .values_list("_acquisition_price", flat=True)[:1]
                    ),
                ),
            )
            .annotate(
                date=max_if_all_not_null(
                    ref="real_estates__buildings__apartments__completion_date",
                    inf=datetime.date.max,
                ),
                sum_surface_area=Sum("real_estates__buildings__apartments__surface_area"),
                sum_acquisition_price=Sum("_acquisition_price"),
                avg_price_per_square_meter=RoundWithPrecision(
                    F("sum_acquisition_price") / F("sum_surface_area"),
                    precision=2,
                ),
                sum_total_shares=Sum(
                    F("real_estates__buildings__apartments__share_number_end")
                    - F("real_estates__buildings__apartments__share_number_start")
                    + 1
                ),
            )
        )

    @staticmethod
    def get_filterset_class():
        return HousingCompanyFilterSet
