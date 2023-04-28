import datetime
import uuid
from decimal import Decimal
from itertools import chain
from typing import Any, Dict, Iterable, Optional, Union

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count, Prefetch, Q, QuerySet
from django.db.models.expressions import Case, F, OuterRef, Subquery, Value, When
from django.db.models.functions import Coalesce, Now, NullIf, TruncMonth
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django_filters.rest_framework import BooleanFilter
from enumfields.drf import EnumField, EnumSupportSerializerMixin
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.fields import empty
from rest_framework.request import Request
from rest_framework.response import Response

from hitas.calculations.exceptions import IndexMissingException
from hitas.exceptions import HitasModelNotFound
from hitas.models import (
    Apartment,
    ApartmentConstructionPriceImprovement,
    ApartmentMaximumPriceCalculation,
    Building,
    ConditionOfSale,
    ConstructionPriceIndex,
    ConstructionPriceIndex2005Equal100,
    HousingCompany,
    MarketPriceIndex,
    MarketPriceIndex2005Equal100,
    Ownership,
    SurfaceAreaPriceCeiling,
)
from hitas.models._base import HitasModelDecimalField
from hitas.models.apartment import (
    ApartmentMarketPriceImprovement,
    ApartmentState,
    ApartmentWithAnnotations,
    DepreciationPercentage,
)
from hitas.models.condition_of_sale import GracePeriod
from hitas.models.housing_company import HitasType
from hitas.services.owner import log_access_if_owner_has_non_disclosure
from hitas.services.apartment import (
    get_first_sale_purchase_date,
    get_first_sale_loan_amount,
    get_first_sale_purchase_price,
    get_latest_sale_purchase_date,
    get_latest_sale_purchase_price,
    prefetch_latest_sale,
    check_current_owners_for_non_disclosure,
)

from hitas.services.condition_of_sale import condition_of_sale_queryset
from hitas.utils import RoundWithPrecision, check_for_overlap, this_month, valid_uuid
from hitas.services.validation import lookup_model_id_by_uuid
from hitas.views.codes import ReadOnlyApartmentTypeSerializer
from hitas.views.condition_of_sale import MinimalApartmentSerializer, MinimalOwnerSerializer
from hitas.views.ownership import OwnershipSerializer
from hitas.views.utils import (
    HitasCharFilter,
    HitasDecimalField,
    HitasEnumField,
    HitasFilterSet,
    HitasModelSerializer,
    HitasModelViewSet,
    HitasPostalCodeFilter,
    UUIDRelatedField,
    ValueOrNullField,
)
from hitas.views.utils.merge import merge_model
from hitas.views.utils.pdf import get_pdf_response
from hitas.views.utils.serializers import ApartmentHitasAddressSerializer, ReadOnlySerializer, YearMonthSerializer


class ApartmentFilterSet(HitasFilterSet):
    housing_company_name = HitasCharFilter(
        field_name="building__real_estate__housing_company__display_name",
        lookup_expr="icontains",
    )
    street_address = HitasCharFilter(
        lookup_expr="icontains",
    )
    postal_code = HitasPostalCodeFilter(
        field_name="building__real_estate__housing_company__postal_code__value",
    )
    owner_name = HitasCharFilter(
        field_name="sales__ownerships__owner__name",
        lookup_expr="icontains",
    )
    owner_identifier = HitasCharFilter(
        field_name="sales__ownerships__owner__identifier",
        lookup_expr="icontains",
        max_length=11,
    )
    has_conditions_of_sale = BooleanFilter()

    class Meta:
        model = Apartment
        fields = [
            "housing_company_name",
            "street_address",
            "postal_code",
            "owner_name",
            "owner_identifier",
            "has_conditions_of_sale",
        ]


class MarketPriceImprovementSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    value = HitasDecimalField(required=True, allow_null=False)
    completion_date = YearMonthSerializer(required=True, allow_null=False)
    no_deductions = serializers.BooleanField(default=False)

    class Meta:
        model = ApartmentMarketPriceImprovement
        fields = [
            "name",
            "completion_date",
            "value",
            "no_deductions",
        ]


class DepreciationPercentageField(serializers.ChoiceField):
    def __init__(self, **kwargs):
        super().__init__(choices=DepreciationPercentage.choices(), **kwargs)

    def to_representation(self, percentage: DepreciationPercentage):
        match percentage:  # noqa: E999
            case DepreciationPercentage.TEN:
                return 10.0
            case DepreciationPercentage.TWO_AND_HALF:
                return 2.5
            case DepreciationPercentage.ZERO:
                return 0.0
            case _:
                raise NotImplementedError(f"Value '{percentage}' not implemented.")

    def to_internal_value(self, data: float):
        if data is None:
            raise serializers.ValidationError(code="blank")

        match data:
            case 10:
                return DepreciationPercentage.TEN
            case 2.5:
                return DepreciationPercentage.TWO_AND_HALF
            case 0:
                return DepreciationPercentage.ZERO
            case _:
                supported_values = ["0.0", "2.5", "10.0"]

                raise serializers.ValidationError(
                    f"Unsupported value '{data}'. Supported values are: [{', '.join(supported_values)}]."
                )


class ConstructionPriceImprovementSerializer(MarketPriceImprovementSerializer):
    name = serializers.CharField(required=True)
    completion_date = YearMonthSerializer(required=True)
    depreciation_percentage = DepreciationPercentageField(required=True)

    class Meta:
        model = ApartmentConstructionPriceImprovement
        fields = [
            "name",
            "completion_date",
            "value",
            "depreciation_percentage",
        ]


class SharesSerializer(serializers.Serializer):
    start = serializers.IntegerField(source="share_number_start", min_value=1, allow_null=True)
    end = serializers.IntegerField(source="share_number_end", min_value=1, allow_null=True)
    total = serializers.SerializerMethodField()

    def get_total(self, instance: Apartment) -> int:
        return instance.shares_count

    def validate(self, data):
        start, end = data["share_number_start"], data["share_number_end"]

        if start is None and end is None:
            return data
        if start is None or end is None:
            err_msg = "Both 'shares.start' and 'shares.end' must be given or be 'null'."
            raise ValidationError({"start": err_msg, "end": err_msg})
        if start > end:
            raise ValidationError({"start": "'shares.start' must not be greater than 'shares.end'."})

        share_range_filter = (
            Q(share_number_start__lte=start, share_number_end__gte=start)  # Overlapping start
            | Q(share_number_start__lte=end, share_number_end__gte=end)  # Overlapping end
            | Q(share_number_start__gte=start, share_number_end__lte=end)  # Fully inside range
            | Q(share_number_start__lte=start, share_number_end__gte=end)  # Fully overlapping range
        )

        apartment_filter = Q(building__real_estate__housing_company__uuid=F("_housing_company"))
        if self.parent.instance is not None:
            apartment_filter &= ~Q(uuid=self.parent.instance.uuid)

        building_id: Optional[str] = None
        building_input = self.parent.initial_data["building"]
        if isinstance(building_input, dict):
            building_id = building_input.get("id")

        # If invalid building ID is given, break early as there is already
        # an error on the way from the building_id validator.
        if not isinstance(building_id, str) or not valid_uuid(building_id):
            return data

        overlapping_apartments: Iterable[Apartment] = (
            Apartment.objects.annotate(
                _housing_company=Subquery(
                    HousingCompany.objects.filter(real_estates__buildings__uuid=building_id).values("uuid"),
                ),
            )
            .filter(apartment_filter & share_range_filter)
            .only("street_address", "stair", "apartment_number", "share_number_start", "share_number_end")
        )

        if overlapping_apartments:
            self.check_share_ranges(start, end, overlapping_apartments)

        return data

    @staticmethod
    def check_share_ranges(start: int, end: int, apartments: Iterable[Apartment]) -> None:
        new_share_range = set(range(start, end + 1))
        share_ranges: dict[range, str] = {
            range(apartment.share_number_start, apartment.share_number_end + 1): apartment.address
            for apartment in apartments
            if apartment.share_number_start is not None and apartment.share_number_end is not None
        }

        errors: dict[str, list[str]] = {}
        for share_range, address in share_ranges.items():
            start, end = check_for_overlap(new_share_range, share_range)

            if start is not None and end is not None:
                msg = f"Shares {start}-{end} have already been taken by {address}."
                errors.setdefault("start", [])
                errors.setdefault("end", [])
                errors["start"].append(msg)
                errors["end"].append(msg)

            elif start is not None:
                msg = f"Share {start} has already been taken by {address}."
                errors.setdefault("start", [])
                errors["start"].append(msg)

            elif end is not None:
                msg = f"Share {end} has already been taken by {address}."
                errors.setdefault("end", [])
                errors["end"].append(msg)

        if errors:
            raise ValidationError(errors)

    def run_validation(self, data=empty):
        value = super().run_validation(data)

        if value is None:
            value = {
                "share_number_start": None,
                "share_number_end": None,
            }

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


class ConstructionPricesInterest(serializers.Serializer):
    rate_6 = HitasDecimalField(
        source="interest_during_construction_6",
        required=False,
        allow_null=True,
    )
    rate_14 = HitasDecimalField(
        source="interest_during_construction_14",
        required=False,
        allow_null=True,
    )

    def validate(self, data):
        rate_6, rate_14 = data["interest_during_construction_6"], data["interest_during_construction_14"]

        if rate_6 is None and rate_14 is None:
            return data
        if rate_6 is None or rate_14 is None:
            err_msg = "Both 'rate_6' and 'rate_14' must be given or be 'null'."
            raise ValidationError({"rate_6": err_msg, "rate_14": err_msg})
        if rate_6 > rate_14:
            raise ValidationError({"rate_6": "'rate_6' must not be greater than 'rate_14'."})

        return data

    def run_validation(self, data=empty):
        value = super().run_validation(data)

        if value is None:
            value = {
                "interest_during_construction_6": None,
                "interest_during_construction_14": None,
            }

        return value

    def to_representation(self, instance):
        if instance.interest_during_construction_6 is None:
            return None

        return super().to_representation(instance)

    def validate_empty_values(self, data):
        if data is None:
            return True, None
        else:
            return super().validate_empty_values(data)


class ConstructionPrices(serializers.Serializer):
    loans = HitasDecimalField(source="loans_during_construction", required=False, allow_null=True)
    additional_work = HitasDecimalField(
        source="additional_work_during_construction",
        required=False,
        allow_null=True,
    )
    interest = ConstructionPricesInterest(source="*", required=False, allow_null=True)
    debt_free_purchase_price = HitasDecimalField(
        source="debt_free_purchase_price_during_construction",
        required=False,
        allow_null=True,
    )


class PricesSerializer(serializers.Serializer):
    first_sale_purchase_price = serializers.SerializerMethodField()
    first_sale_share_of_housing_company_loans = serializers.SerializerMethodField()
    first_sale_acquisition_price = serializers.SerializerMethodField()
    catalog_purchase_price = serializers.SerializerMethodField()
    catalog_share_of_housing_company_loans = serializers.SerializerMethodField()
    catalog_acquisition_price = serializers.SerializerMethodField()
    first_purchase_date = serializers.SerializerMethodField()
    latest_sale_purchase_price = serializers.SerializerMethodField()
    latest_purchase_date = serializers.SerializerMethodField()
    construction = ConstructionPrices(source="*", required=False, allow_null=True)
    maximum_prices = serializers.SerializerMethodField()

    @staticmethod
    def get_first_sale_purchase_price(instance: ApartmentWithAnnotations) -> Optional[Decimal]:
        return instance.first_sale_purchase_price

    @staticmethod
    def get_first_sale_share_of_housing_company_loans(instance: ApartmentWithAnnotations) -> Optional[Decimal]:
        return instance.first_sale_share_of_housing_company_loans

    @staticmethod
    def get_first_sale_acquisition_price(instance: ApartmentWithAnnotations) -> Optional[Decimal]:
        return instance.first_sale_acquisition_price

    @staticmethod
    def get_catalog_purchase_price(instance: ApartmentWithAnnotations) -> Optional[Decimal]:
        return instance.catalog_purchase_price

    @staticmethod
    def get_catalog_share_of_housing_company_loans(instance: ApartmentWithAnnotations) -> Optional[Decimal]:
        return instance.catalog_primary_loan_amount

    @staticmethod
    def get_catalog_acquisition_price(instance: ApartmentWithAnnotations) -> Optional[Decimal]:
        return instance.catalog_acquisition_price

    @staticmethod
    def get_first_purchase_date(instance: ApartmentWithAnnotations) -> Optional[datetime.date]:
        return instance.first_purchase_date

    @staticmethod
    def get_latest_sale_purchase_price(instance: ApartmentWithAnnotations) -> Optional[Decimal]:
        return instance.latest_sale_purchase_price

    @staticmethod
    def get_latest_purchase_date(instance: ApartmentWithAnnotations) -> Optional[datetime.date]:
        return instance.latest_purchase_date

    def get_maximum_prices(self, instance: Apartment) -> Dict[str, Any]:
        return {
            "unconfirmed": self.get_unconfirmed_max_prices(instance),
            "confirmed": self.get_confirmed_max_prices(instance),
        }

    @staticmethod
    def get_confirmed_max_prices(instance: Apartment) -> Optional[Dict[str, Any]]:
        latest_confirmed_max_price_calculation = (
            instance.max_price_calculations.only(
                "uuid",
                "created_at",
                "confirmed_at",
                "calculation_date",
                "maximum_price",
                "valid_until",
                "apartment_id",
                "json_version",
            )
            .filter(confirmed_at__isnull=False)
            .order_by("-confirmed_at", "-maximum_price")  # migrated calculations have the same datestamp
            .first()
        )

        return (
            {
                "id": (
                    latest_confirmed_max_price_calculation.uuid.hex
                    if latest_confirmed_max_price_calculation.json_version
                    == ApartmentMaximumPriceCalculation.CURRENT_JSON_VERSION
                    else None
                ),
                "maximum_price": latest_confirmed_max_price_calculation.maximum_price,
                "created_at": latest_confirmed_max_price_calculation.created_at,
                "confirmed_at": latest_confirmed_max_price_calculation.confirmed_at,
                "calculation_date": latest_confirmed_max_price_calculation.calculation_date,
                "valid": {
                    "is_valid": latest_confirmed_max_price_calculation.valid_until >= timezone.now().date(),
                    "valid_until": latest_confirmed_max_price_calculation.valid_until,
                },
            }
            if latest_confirmed_max_price_calculation
            else None
        )

    @staticmethod
    def get_unconfirmed_max_prices(instance: Apartment) -> Dict[str, Any]:
        pre2011 = None
        onwards2011 = None

        def instance_values(keys: list[str]):
            retval = []

            for key in keys:
                value = getattr(instance, key, None)

                retval.append(value)

            return retval

        def max_with_nones(*values):
            """
            Differs from normal max() by allowing None values. Returns None if no max value is found.
            """

            values = list(filter(None, values))
            return max(values) if values else None

        def value_obj(v: float, max_value: float):
            return {"value": v, "maximum": v is not None and v == max_value}

        if instance.completion_date and instance.completion_date < datetime.date(2011, 1, 1):
            # Handle apartments completed before year 2011
            cpi, mpi, sapc = instance_values(["cpi", "mpi", "sapc"])
            maximum = max_with_nones(cpi, mpi, sapc)

            pre2011 = {
                "construction_price_index": value_obj(cpi, maximum),
                "market_price_index": value_obj(mpi, maximum),
                "surface_area_price_ceiling": value_obj(sapc, maximum),
            }
        else:
            # Handle apartments not yet completed or completed 2011 onwards
            cpi, mpi, sapc = instance_values(["cpi_2005_100", "mpi_2005_100", "sapc"])
            maximum = max_with_nones(cpi, mpi, sapc)

            onwards2011 = {
                "construction_price_index": value_obj(cpi, maximum),
                "market_price_index": value_obj(mpi, maximum),
                "surface_area_price_ceiling": value_obj(sapc, maximum),
            }

        return {
            "pre_2011": pre2011,
            "onwards_2011": onwards2011,
        }


def create_links(instance: Apartment) -> Dict[str, Any]:
    return {
        "housing_company": {
            "id": instance.housing_company.uuid.hex,
            "display_name": instance.housing_company.display_name,
            "link": reverse(
                "hitas:housing-company-detail",
                kwargs={
                    "uuid": instance.housing_company.uuid.hex,
                },
            ),
        },
        "real_estate": {
            "id": instance.building.real_estate.uuid.hex,
            "link": reverse(
                "hitas:real-estate-detail",
                kwargs={
                    "housing_company_uuid": instance.housing_company.uuid.hex,
                    "uuid": instance.building.real_estate.uuid.hex,
                },
            ),
        },
        "building": {
            "id": instance.building.uuid.hex,
            "street_address": instance.building.street_address,
            "link": reverse(
                "hitas:building-detail",
                kwargs={
                    "housing_company_uuid": instance.housing_company.uuid.hex,
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
                    "housing_company_uuid": instance.housing_company.uuid.hex,
                    "uuid": instance.uuid.hex,
                },
            ),
        },
    }


class ApartmentImprovementSerializer(serializers.Serializer):
    market_price_index = MarketPriceImprovementSerializer(many=True, source="market_price_improvements")
    construction_price_index = ConstructionPriceImprovementSerializer(
        many=True, source="construction_price_improvements"
    )


class ReadOnlyBuildingSerializer(ReadOnlySerializer):
    id = UUIDRelatedField(queryset=Building.objects, write_only=True)

    def get_model_class(self):
        return Building

    class Meta:
        fields = ["id"]


class ApartmentConditionsOfSaleSerializer(EnumSupportSerializerMixin, HitasModelSerializer):
    owner = serializers.SerializerMethodField()
    apartment = serializers.SerializerMethodField()
    grace_period = EnumField(GracePeriod)
    fulfilled = serializers.SerializerMethodField()
    sell_by_date = serializers.SerializerMethodField()

    @staticmethod
    def get_fulfilled(instance: ConditionOfSale) -> Optional[datetime.datetime]:
        return instance.fulfilled

    @staticmethod
    def get_sell_by_date(instance: ConditionOfSale) -> Optional[datetime.date]:
        return instance.sell_by_date

    def select_ownership(self, instance: ConditionOfSale) -> Ownership:
        if instance.old_ownership.apartment == self.context["apartment"]:
            return instance.new_ownership
        else:
            return instance.old_ownership

    def get_owner(self, instance: ConditionOfSale):
        return MinimalOwnerSerializer(self.select_ownership(instance).owner).data

    def get_apartment(self, instance: ConditionOfSale):
        return MinimalApartmentSerializer(self.select_ownership(instance).apartment).data

    class Meta:
        model = ConditionOfSale
        fields = [
            "id",
            "owner",
            "apartment",
            "grace_period",
            "fulfilled",
            "sell_by_date",
        ]


class ApartmentDetailSerializer(EnumSupportSerializerMixin, HitasModelSerializer):
    state = HitasEnumField(enum=ApartmentState, required=False, allow_null=True)
    type = ReadOnlyApartmentTypeSerializer(source="apartment_type", required=False, allow_null=True)
    address = ApartmentHitasAddressSerializer(source="*")
    completion_date = serializers.DateField(required=False, allow_null=True)
    surface_area = HitasDecimalField(required=False, allow_null=True)
    rooms = ValueOrNullField(required=False, allow_null=True)
    shares = SharesSerializer(source="*", required=False, allow_null=True)
    prices = PricesSerializer(source="*", required=False, allow_null=True)
    ownerships = serializers.SerializerMethodField()
    links = serializers.SerializerMethodField()
    building = ReadOnlyBuildingSerializer(write_only=True)
    improvements = ApartmentImprovementSerializer(source="*")
    conditions_of_sale = serializers.SerializerMethodField()
    sell_by_date = serializers.SerializerMethodField()

    @staticmethod
    def get_ownerships(instance: Apartment) -> list[dict[str, Any]]:
        ownerships: list[dict[str, Any]] = []
        for sale in instance.sales.all():  # only first sale prefetched
            for ownership in sale.ownerships.all():
                ownerships.append(OwnershipSerializer(instance=ownership).data)
        return ownerships

    @staticmethod
    def get_conditions_of_sale(instance: Apartment) -> list[dict[str, Any]]:
        conditions_of_sale: list[ConditionOfSale] = [
            cos
            for sale in instance.sales.all()  # only first sale prefetched
            for ownership in sale.ownerships.all()
            for cos in chain(ownership.conditions_of_sale_new.all(), ownership.conditions_of_sale_old.all())
        ]

        context = {"apartment": instance}
        return [ApartmentConditionsOfSaleSerializer(cos, context=context).data for cos in conditions_of_sale]

    @staticmethod
    def get_sell_by_date(instance: Apartment) -> Optional[datetime.date]:
        return instance.sell_by_date

    @staticmethod
    def get_links(instance: Apartment):
        return create_links(instance)

    def validate_building(self, building: Building) -> Building:
        if building is None:
            raise serializers.ValidationError(code="blank")

        housing_company_uuid = self.context["view"].kwargs["housing_company_uuid"]
        try:
            hc = HousingCompany.objects.only("id").get(uuid=uuid.UUID(hex=housing_company_uuid))
        except (HousingCompany.DoesNotExist, ValueError, TypeError):
            raise

        if building.real_estate.housing_company.id != hc.id:
            raise ValidationError(f"Object does not exist with given id '{building.uuid.hex}'.", code="invalid")

        return building

    def create(self, validated_data: dict[str, Any]) -> Apartment:
        mpi = validated_data.pop("market_price_improvements")
        cpi = validated_data.pop("construction_price_improvements")

        instance: Apartment = super().create(validated_data)

        for improvement in mpi:
            ApartmentMarketPriceImprovement.objects.create(apartment=instance, **improvement)
        for improvement in cpi:
            ApartmentConstructionPriceImprovement.objects.create(apartment=instance, **improvement)

        return instance

    def update(self, instance: Apartment, validated_data: dict[str, Any]) -> Apartment:
        mpi = validated_data.pop("market_price_improvements")
        cpi = validated_data.pop("construction_price_improvements")

        instance: Apartment = super().update(instance, validated_data)

        # Improvements
        merge_model(
            model_class=ApartmentMarketPriceImprovement,
            existing_qs=instance.market_price_improvements.all(),
            wanted=mpi,
            create_defaults={"apartment": instance},
            equal_fields=["value", "completion_date", "name", "no_deductions"],
        )
        merge_model(
            model_class=ApartmentConstructionPriceImprovement,
            existing_qs=instance.construction_price_improvements.all(),
            wanted=cpi,
            create_defaults={"apartment": instance},
            equal_fields=["value", "completion_date", "name", "depreciation_percentage"],
        )

        return instance

    class Meta:
        model = Apartment
        fields = [
            "id",
            "state",
            "type",
            "surface_area",
            "rooms",
            "shares",
            "links",
            "address",
            "prices",
            "completion_date",
            "ownerships",
            "notes",
            "building",
            "improvements",
            "conditions_of_sale",
            "sell_by_date",
        ]


class ApartmentListSerializer(ApartmentDetailSerializer):
    type = serializers.SerializerMethodField()
    has_conditions_of_sale = serializers.SerializerMethodField()
    has_grace_period = serializers.SerializerMethodField()

    @staticmethod
    def get_type(instance: Apartment) -> Optional[str]:
        return getattr(getattr(instance, "apartment_type", None), "value", None)

    @staticmethod
    def get_has_conditions_of_sale(instance: ApartmentWithAnnotations) -> bool:
        return instance.has_conditions_of_sale

    @staticmethod
    def get_has_grace_period(instance: Apartment) -> bool:
        return instance.has_grace_period

    class Meta:
        model = Apartment
        fields = [
            "id",
            "state",
            "type",
            "surface_area",
            "rooms",
            "address",
            "completion_date",
            "ownerships",
            "has_conditions_of_sale",
            "has_grace_period",
            "sell_by_date",
            "links",
        ]


class ApartmentViewSet(HitasModelViewSet):
    model_class = Apartment
    serializer_class = ApartmentDetailSerializer
    list_serializer_class = ApartmentListSerializer

    def get_filterset_class(self):
        return ApartmentFilterSet

    @staticmethod
    def select_index(
        table: Union[
            type[MarketPriceIndex],
            type[MarketPriceIndex2005Equal100],
            type[ConstructionPriceIndex],
            type[ConstructionPriceIndex2005Equal100],
        ],
    ) -> RoundWithPrecision:
        original_value = Subquery(
            table.objects.filter(month=OuterRef("completion_month")).values("value"),
            output_field=HitasModelDecimalField(),
        )

        current_value = Subquery(
            table.objects.filter(month=TruncMonth(Now())).values("value"),
            output_field=HitasModelDecimalField(),
        )

        interest: Union[Case, Value] = Value(0, output_field=HitasModelDecimalField())
        if issubclass(table, MarketPriceIndex):
            interest = Case(
                When(
                    condition=~Q(
                        building__real_estate__housing_company__hitas_type__in=HitasType.with_new_hitas_ruleset(),
                    ),
                    then=Coalesce(F("interest_during_construction_6"), 0, output_field=HitasModelDecimalField()),
                ),
                default=0,
                output_field=HitasModelDecimalField(),
            )
        elif issubclass(table, ConstructionPriceIndex):
            interest = Case(
                # Check for exceptions where old ruleset is not used
                When(
                    condition=Q(
                        building__real_estate__housing_company__hitas_type__in=HitasType.with_new_hitas_ruleset(),
                    ),
                    then=0,
                ),
                When(
                    condition=Q(completion_date__lt=datetime.date(2005, 1, 1)),
                    then=Coalesce(F("interest_during_construction_14"), 0, output_field=HitasModelDecimalField()),
                ),
                default=Coalesce(F("interest_during_construction_6"), 0, output_field=HitasModelDecimalField()),
                output_field=HitasModelDecimalField(),
            )

        return RoundWithPrecision(
            (
                F("_first_sale_purchase_price")
                + F("_first_sale_share_of_housing_company_loans")
                + F("additional_work_during_construction")
                + interest
            )
            * current_value
            / NullIf(original_value, 0, output_field=HitasModelDecimalField()),  # prevent zero division errors
            precision=2,
        )

    @staticmethod
    def select_sapc() -> RoundWithPrecision:
        current_value = Subquery(
            SurfaceAreaPriceCeiling.objects.filter(month=TruncMonth(Now())).values("value"),
            output_field=HitasModelDecimalField(),
        )

        return RoundWithPrecision(
            F("surface_area") * current_value,
            precision=2,
        )

    @staticmethod
    def get_base_queryset():
        return (
            Apartment.objects.prefetch_related(
                prefetch_latest_sale(include_first_sale=True),
                Prefetch(
                    "sales__ownerships",
                    Ownership.objects.select_related("owner"),
                ),
                Prefetch(
                    "sales__ownerships__conditions_of_sale_new",
                    condition_of_sale_queryset(),
                ),
                Prefetch(
                    "sales__ownerships__conditions_of_sale_old",
                    condition_of_sale_queryset(),
                ),
            )
            .select_related(
                "building",
                "apartment_type",
                "building__real_estate",
                "building__real_estate__housing_company",
                "building__real_estate__housing_company__postal_code",
            )
            .alias(
                number_of_conditions_of_sale=(
                    Count(
                        "sales__ownerships__conditions_of_sale_new",
                        filter=Q(sales__ownerships__conditions_of_sale_new__deleted__isnull=True),
                    )
                    + Count(
                        "sales__ownerships__conditions_of_sale_old",
                        filter=Q(sales__ownerships__conditions_of_sale_old__deleted__isnull=True),
                    )
                ),
            )
            .annotate(
                has_conditions_of_sale=Case(
                    When(condition=Q(number_of_conditions_of_sale__gt=0), then=True),
                    default=False,
                    output_field=models.BooleanField(),
                ),
            )
            .order_by("-has_conditions_of_sale", "apartment_number", "id")
        )

    def get_list_queryset(self):
        hc_id = lookup_model_id_by_uuid(self.kwargs["housing_company_uuid"], HousingCompany)
        return self.get_base_queryset().filter(building__real_estate__housing_company__id=hc_id)

    def get_detail_queryset(self):
        return self.get_list_queryset().annotate(
            _first_sale_purchase_price=get_first_sale_purchase_price("id"),
            _first_sale_share_of_housing_company_loans=get_first_sale_loan_amount("id"),
            _first_purchase_date=get_first_sale_purchase_date("id"),
            _latest_sale_purchase_price=get_latest_sale_purchase_price("id"),
            _latest_purchase_date=get_latest_sale_purchase_date("id"),
            completion_month=TruncMonth("completion_date"),  # Used for calculating indexes
            cpi=self.select_index(ConstructionPriceIndex),
            cpi_2005_100=self.select_index(ConstructionPriceIndex2005Equal100),
            mpi=self.select_index(MarketPriceIndex),
            mpi_2005_100=self.select_index(MarketPriceIndex2005Equal100),
            sapc=self.select_sapc(),
        )

    @action(detail=True, methods=["POST"], url_path="reports/download-latest-unconfirmed-prices")
    def download_latest_unconfirmed_prices(self, request, **kwargs) -> Union[HttpResponse, Response]:
        apartment = self.get_object()
        apartment_data = ApartmentDetailSerializer(apartment).data
        ump = apartment_data["prices"]["maximum_prices"]["unconfirmed"]
        is_pre_2011 = ump["pre_2011"] is not None
        ump = ump["pre_2011"] if is_pre_2011 else ump["onwards_2011"]

        if ump["construction_price_index"]["value"] is None:
            raise IndexMissingException(error_code="cpi" if is_pre_2011 else "cpi2005eq100", date=this_month())
        if ump["market_price_index"]["value"] is None:
            raise IndexMissingException(error_code="mpi" if is_pre_2011 else "mpi2005eq100", date=this_month())
        if ump["surface_area_price_ceiling"]["value"] is None:
            raise IndexMissingException(error_code="sapc", date=this_month())

        sapc = SurfaceAreaPriceCeiling.objects.only("value").get(month=this_month())
        context = {
            "apartment": apartment_data,
            "additional_info": request.data.get("additional_info", ""),
            "surface_area_price_ceiling": sapc.value,
            "old_hitas_ruleset": apartment.old_hitas_ruleset,
        }
        filename = f"Hinta-arvio {apartment.address}.pdf"
        return get_pdf_response(filename=filename, template="unconfirmed_maximum_price.jinja", context=context)

    @action(detail=True, methods=["POST"], url_path="reports/download-latest-confirmed-prices")
    def download_latest_confirmed_prices(self, request, **kwargs) -> HttpResponse:
        mpc = (
            ApartmentMaximumPriceCalculation.objects.filter(
                apartment=self.get_object(),
                json_version=ApartmentMaximumPriceCalculation.CURRENT_JSON_VERSION,
            )
            .exclude(confirmed_at=None)
            .order_by("-confirmed_at")
            .first()
        )

        if mpc is None:
            raise HitasModelNotFound(model=ApartmentMaximumPriceCalculation)

        filename = f"Enimmäishintalaskelma {mpc.apartment.address}.pdf"
        context = {"maximum_price_calculation": mpc}
        return get_pdf_response(filename=filename, template="confirmed_maximum_price.jinja", context=context)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        apartment: Apartment = self.get_object()
        check_current_owners_for_non_disclosure(apartment)
        serializer = self.get_serializer(apartment)
        return Response(serializer.data)

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset: QuerySet[Apartment] = self.filter_queryset(self.get_queryset())

        page: Optional[list[Apartment]] = self.paginate_queryset(queryset)
        if page is not None:
            for apartment in page:
                check_current_owners_for_non_disclosure(apartment)

            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        for apartment in queryset:
            check_current_owners_for_non_disclosure(apartment)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
