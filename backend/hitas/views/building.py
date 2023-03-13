from typing import Optional
from uuid import UUID

from django.db.models import Count
from rest_framework import serializers

from hitas.exceptions import HitasModelNotFound, ModelConflict
from hitas.models import Building, HousingCompany, RealEstate
from hitas.models.utils import validate_building_id
from hitas.services.validation import lookup_model_id_by_uuid
from hitas.views.utils import HitasModelSerializer, HitasModelViewSet, ValueOrNullField


class BuildingHitasAddressSerializer(serializers.Serializer):
    street_address = serializers.CharField()
    postal_code = serializers.CharField(source="real_estate.housing_company.postal_code.value", read_only=True)
    city = serializers.CharField(source="real_estate.housing_company.city", read_only=True)


class BuildingSerializer(HitasModelSerializer):
    address = BuildingHitasAddressSerializer(source="*")
    building_identifier = ValueOrNullField(required=False, allow_null=True)
    apartment_count = serializers.SerializerMethodField()

    def get_apartment_count(self, instance: Building) -> int:
        apartment_count: Optional[int] = getattr(instance, "apartment_count", None)
        if apartment_count is not None:
            return apartment_count

        return instance.apartments.count()

    def validate_building_identifier(self, value):
        if value == "":
            value = None
        validate_building_id(value)
        return value

    @property
    def validated_data(self):
        """Inject related Real Estate ID to the validated data"""
        validated_data = super().validated_data
        try:
            real_estate_uuid = UUID(hex=self.context["view"].kwargs.get("real_estate_uuid"))
            real_estate_id = RealEstate.objects.only("id").get(uuid=real_estate_uuid).id
        except (RealEstate.DoesNotExist, ValueError) as error:
            raise HitasModelNotFound(model=RealEstate) from error

        validated_data["real_estate_id"] = real_estate_id
        return validated_data

    class Meta:
        model = Building
        fields = [
            "id",
            "address",
            "apartment_count",
            "building_identifier",
        ]


class BuildingViewSet(HitasModelViewSet):
    serializer_class = BuildingSerializer
    model_class = Building

    def perform_destroy(self, instance: Building) -> None:
        if instance.apartments.exists():
            raise ModelConflict("Cannot delete a building with apartments.", error_code="apartments_on_building")

        super().perform_destroy(instance)

    def get_queryset(self):
        hc_id = lookup_model_id_by_uuid(self.kwargs["housing_company_uuid"], HousingCompany)
        re_id = lookup_model_id_by_uuid(self.kwargs["real_estate_uuid"], RealEstate, housing_company_id=hc_id)

        return (
            Building.objects.filter(real_estate__id=re_id)
            .select_related("real_estate__housing_company__postal_code")
            .annotate(
                apartment_count=Count("apartments"),
            )
            .only(
                "uuid",
                "street_address",
                "building_identifier",
                "real_estate__housing_company__postal_code__value",
                "real_estate__housing_company__postal_code__city",
            )
            .order_by("id")
        )
