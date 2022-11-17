import datetime
import uuid
from collections import OrderedDict
from http import HTTPStatus
from typing import Any, Dict, Optional, Union

from django.core.exceptions import ValidationError
from django.db.models import Prefetch
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from enumfields.drf import EnumSupportSerializerMixin
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.fields import empty
from rest_framework.response import Response

from hitas.exceptions import HitasModelNotFound
from hitas.models import (
    Apartment,
    ApartmentConstructionPriceImprovement,
    ApartmentMaximumPriceCalculation,
    Building,
    HousingCompany,
    Owner,
    Ownership,
)
from hitas.models.apartment import ApartmentMarketPriceImprovement, ApartmentState, DepreciationPercentage
from hitas.views.codes import ReadOnlyApartmentTypeSerializer
from hitas.views.ownership import OwnershipSerializer
from hitas.views.utils import (
    HitasDecimalField,
    HitasEnumField,
    HitasModelSerializer,
    HitasModelViewSet,
    UUIDRelatedField,
    ValueOrNullField,
)
from hitas.views.utils.merge import merge_model
from hitas.views.utils.pdf import get_pdf_response
from hitas.views.utils.serializers import YearMonthSerializer


class MarketPriceImprovementSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    value = HitasDecimalField(required=True, allow_null=False)
    completion_date = YearMonthSerializer(required=True, allow_null=False)

    class Meta:
        model = ApartmentMarketPriceImprovement
        fields = [
            "name",
            "completion_date",
            "value",
        ]


class DepreciationPercentageField(serializers.ChoiceField):
    def __init__(self, **kwargs):
        super().__init__(choices=DepreciationPercentage.choices(), **kwargs)

    def to_representation(self, percentage: DepreciationPercentage):
        match percentage:
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


class ApartmentHitasAddressSerializer(serializers.Serializer):
    street_address = serializers.CharField()
    postal_code = serializers.CharField(source="building.real_estate.housing_company.postal_code.value", read_only=True)
    city = serializers.CharField(source="building.real_estate.housing_company.city", read_only=True)
    apartment_number = serializers.IntegerField(min_value=0)
    floor = serializers.CharField(max_length=50, required=False, allow_null=True, allow_blank=True)
    stair = serializers.CharField(max_length=16)


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

        return data

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


class ConstructionPrices(serializers.Serializer):
    loans = HitasDecimalField(source="loans_during_construction", required=False, allow_null=True)
    additional_work = HitasDecimalField(
        source="additional_work_during_construction",
        required=False,
        allow_null=True,
    )
    interest = HitasDecimalField(
        source="interest_during_construction",
        required=False,
        allow_null=True,
    )
    debt_free_purchase_price = HitasDecimalField(
        source="debt_free_purchase_price_during_construction",
        required=False,
        allow_null=True,
    )


class PricesSerializer(serializers.Serializer):
    debt_free_purchase_price = HitasDecimalField(required=False, allow_null=True)
    primary_loan_amount = HitasDecimalField(required=False, allow_null=True)
    acquisition_price = HitasDecimalField(read_only=True)
    purchase_price = HitasDecimalField(required=False, allow_null=True)
    first_purchase_date = serializers.DateField(required=False, allow_null=True)
    latest_purchase_date = serializers.DateField(required=False, allow_null=True)
    construction = ConstructionPrices(source="*", required=False, allow_null=True)
    maximum_prices = serializers.SerializerMethodField()

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
            .order_by("-confirmed_at")
            .order_by("-maximum_price")  # migrated calculations have the same datestamp
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


class ApartmentDetailSerializer(EnumSupportSerializerMixin, HitasModelSerializer):
    state = HitasEnumField(enum=ApartmentState, required=False, allow_null=True)
    type = ReadOnlyApartmentTypeSerializer(source="apartment_type")
    address = ApartmentHitasAddressSerializer(source="*")
    completion_date = serializers.DateField(required=False, allow_null=True)
    surface_area = HitasDecimalField(required=False, allow_null=True)
    rooms = ValueOrNullField(required=False, allow_null=True)
    shares = SharesSerializer(source="*", required=False, allow_null=True)
    prices = PricesSerializer(source="*", required=False, allow_null=True)
    ownerships = OwnershipSerializer(many=True)
    links = serializers.SerializerMethodField()
    building = UUIDRelatedField(queryset=Building.objects.all(), write_only=True)
    improvements = ApartmentImprovementSerializer(source="*")

    @staticmethod
    def get_links(instance: Apartment):
        return create_links(instance)

    def validate_building(self, building: Building):
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

    @staticmethod
    def validate_ownerships(ownerships: OrderedDict):
        if not ownerships:
            return ownerships

        for owner in ownerships:
            op = owner["percentage"]
            if not 0 < op <= 100:
                raise ValidationError(
                    {
                        "percentage": (
                            "Ownership percentage greater than 0 and"
                            f" less than or equal to 100. Given value was {op}."
                        )
                    },
                )

        if (sum_op := sum(o["percentage"] for o in ownerships)) != 100:
            raise ValidationError(
                {
                    "percentage": (
                        "Ownership percentage of all ownerships combined"
                        f" must be equal to 100. Given sum was {sum_op}."
                    )
                }
            )

        return ownerships

    def create(self, validated_data: dict[str, Any]):
        ownerships = validated_data.pop("ownerships")
        mpi = validated_data.pop("market_price_improvements")
        cpi = validated_data.pop("construction_price_improvements")

        instance: Apartment = super().create(validated_data)

        for owner_data in ownerships:
            Ownership.objects.create(apartment=instance, **owner_data)

        for improvement in mpi:
            ApartmentMarketPriceImprovement.objects.create(apartment=instance, **improvement)
        for improvement in cpi:
            ApartmentConstructionPriceImprovement.objects.create(apartment=instance, **improvement)

        return instance

    def update(self, instance: Apartment, validated_data: dict[str, Any]):
        ownerships = validated_data.pop("ownerships")
        mpi = validated_data.pop("market_price_improvements")
        cpi = validated_data.pop("construction_price_improvements")

        instance: Apartment = super().update(instance, validated_data)

        # Ownerships
        merge_model(
            model_class=Ownership,
            existing_qs=instance.ownerships.all(),
            wanted=ownerships,
            create_defaults={"apartment": instance},
            equal_fields=["owner", "start_date", "end_date", "percentage"],
        )

        # Improvements
        merge_model(
            model_class=ApartmentMarketPriceImprovement,
            existing_qs=instance.market_price_improvements.all(),
            wanted=mpi,
            create_defaults={"apartment": instance},
            equal_fields=["value", "completion_date", "name"],
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
        ]


class ApartmentListSerializer(ApartmentDetailSerializer):
    type = serializers.CharField(source="apartment_type.value")

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
            "links",
        ]


class ApartmentViewSet(HitasModelViewSet):
    serializer_class = ApartmentDetailSerializer
    list_serializer_class = ApartmentListSerializer
    model_class = Apartment

    @staticmethod
    def select_index(table: str, pre2011: bool):
        comparison = "<" if pre2011 else ">="

        return f"""
    SELECT
        ROUND(
            (
                a.debt_free_purchase_price + a.primary_loan_amount
            ) * current_{table}.value / NULLIF(original_{table}.value, 0), 2
        ) AS max_price_{table}
    FROM hitas_apartment AS a
    LEFT JOIN hitas_{table} AS original_{table} ON
        a.completion_date {comparison} '2011-01-01' AND original_{table}.month = DATE_TRUNC('month', a.completion_date)
    LEFT JOIN hitas_{table} AS current_{table} ON
        a.completion_date {comparison} '2011-01-01' AND current_{table}.month = DATE_TRUNC('month', NOW())
    WHERE a.id = hitas_apartment.id
"""

    def get_detail_queryset(self):
        return (
            self.get_list_queryset()
            .only(
                "uuid",
                "state",
                "surface_area",
                "street_address",
                "apartment_number",
                "floor",
                "stair",
                "rooms",
                "share_number_start",
                "share_number_end",
                "debt_free_purchase_price",
                "primary_loan_amount",
                "purchase_price",
                "first_purchase_date",
                "latest_purchase_date",
                "additional_work_during_construction",
                "loans_during_construction",
                "interest_during_construction",
                "debt_free_purchase_price_during_construction",
                "notes",
                "completion_date",
                "building__uuid",
                "building__real_estate__uuid",
                "apartment_type__uuid",
                "apartment_type__value",
                "apartment_type__legacy_code_number",
                "apartment_type__description",
                "building__street_address",
                "building__real_estate__housing_company__uuid",
                "building__real_estate__housing_company__display_name",
                "building__real_estate__housing_company__postal_code__value",
                "building__real_estate__housing_company__postal_code__city",
            )
            .extra(
                select={
                    "cpi": self.select_index("constructionpriceindex", pre2011=True),
                    "cpi_2005_100": self.select_index("constructionpriceindex2005equal100", pre2011=False),
                    "mpi": self.select_index("marketpriceindex", pre2011=True),
                    "mpi_2005_100": self.select_index("marketpriceindex2005equal100", pre2011=False),
                    "sapc": """
    SELECT ROUND(a.surface_area * sapc.value, 2)
    FROM hitas_apartment AS a
    LEFT JOIN hitas_surfaceareapriceceiling AS sapc
        ON sapc.month = DATE_TRUNC('month', NOW())
    WHERE a.id = hitas_apartment.id
""",
                }
            )
        )

    def get_list_queryset(self):
        hc_id = self._lookup_model_id_by_uuid(HousingCompany, "housing_company_uuid")

        return (
            Apartment.objects.filter(building__real_estate__housing_company__id=hc_id)
            .prefetch_related(
                Prefetch(
                    "ownerships",
                    Ownership.objects.only("apartment_id", "percentage", "start_date", "end_date", "owner_id"),
                ),
                Prefetch(
                    "ownerships__owner",
                    Owner.objects.only("uuid", "name", "identifier", "email"),
                ),
                Prefetch(
                    "market_price_improvements",
                    ApartmentMarketPriceImprovement.objects.only(
                        "name", "completion_date", "value", "apartment_id"
                    ).order_by("completion_date", "id"),
                ),
                Prefetch(
                    "construction_price_improvements",
                    ApartmentConstructionPriceImprovement.objects.only(
                        "name", "completion_date", "value", "apartment_id", "depreciation_percentage"
                    ).order_by("completion_date", "id"),
                ),
            )
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
                "apartment_type__value",
                "building__uuid",
                "building__real_estate__uuid",
                "building__real_estate__housing_company__uuid",
                "building__real_estate__housing_company__display_name",
                "building__real_estate__housing_company__postal_code__value",
                "building__real_estate__housing_company__postal_code__city",
            )
            .order_by("id")
        )

    @action(detail=True, methods=["POST"], url_path="reports/download-latest-unconfirmed-prices")
    def download_latest_unconfirmed_prices(self, request, **kwargs) -> Union[HttpResponse, Response]:
        apartment = self.get_object()
        apartment_data = ApartmentDetailSerializer(apartment).data
        ump = apartment_data["prices"]["maximum_prices"]["unconfirmed"]
        ump = ump["pre_2011"] if ump["pre_2011"] is not None else ump["onwards_2011"]

        if (
            ump["construction_price_index"]["value"] is None
            or ump["market_price_index"]["value"] is None
            or ump["surface_area_price_ceiling"]["value"] is None
        ):
            return Response(
                {
                    "error": "index_missing",
                    "message": "One or more indices required for max price calculation is missing.",
                    "reason": "Conflict",
                    "status": 409,
                },
                status=HTTPStatus.CONFLICT,
            )

        filename = f"Hinta-arvio {apartment.address}.pdf"
        context = {"apartment": apartment_data, "additional_info": request.data.get("additional_info", "")}
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
