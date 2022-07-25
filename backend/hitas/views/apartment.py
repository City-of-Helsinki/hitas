from django_filters.rest_framework import filters
from enumfields.drf import EnumSupportSerializerMixin
from rest_framework import serializers

from hitas.models import Apartment, Building
from hitas.models.apartment import ApartmentState
from hitas.models.utils import validate_share_numbers
from hitas.views.codes import ApartmentTypeSerializer
from hitas.views.housing_company import HousingCompanyListSerializer
from hitas.views.owner import OwnerSerializer
from hitas.views.utils import (
    AddressSerializer,
    HitasDecimalField,
    HitasModelSerializer,
    HitasModelViewSet,
)
from hitas.views.utils.fields import HitasEnumField, UUIDRelatedField


class ApartmentDetailSerializer(EnumSupportSerializerMixin, HitasModelSerializer):
    state = HitasEnumField(enum=ApartmentState)
    apartment_type = ApartmentTypeSerializer()
    address = AddressSerializer(source="*")
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
    housing_company = HousingCompanyListSerializer(source="building.real_estate.housing_company", read_only=True)
    owners = OwnerSerializer(many=True, read_only=True)

    def get_real_estate(self, instance: Apartment) -> str:
        return instance.building.real_estate.uuid.hex

    def validate(self, data):
        validate_share_numbers(start=data["share_number_start"], end=data["share_number_end"])
        return data

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
    housing_company = serializers.CharField(source="building.real_estate.housing_company.display_name")

    class Meta:
        model = Apartment
        fields = [
            "id",
            "state",
            "apartment_type",
            "surface_area",
            "address",
            "apartment_number",
            "date",
            "housing_company",
            "owners",
        ]


class ApartmentViewSet(HitasModelViewSet):
    serializer_class = ApartmentDetailSerializer
    list_serializer_class = ApartmentListSerializer
    model_class = Apartment

    def get_queryset(self):
        return Apartment.objects.select_related("postal_code")
