from uuid import UUID

from rest_framework import serializers

from hitas.exceptions import HitasModelNotFound
from hitas.models import Building, HousingCompany, RealEstate
from hitas.models.utils import validate_building_id
from hitas.views.utils import HitasModelSerializer, HitasModelViewSet, ValueOrNullField


class BuildingHitasAddressSerializer(serializers.Serializer):
    street_address = serializers.CharField()
    postal_code = serializers.CharField(source="real_estate.housing_company.postal_code.value", read_only=True)
    city = serializers.CharField(source="real_estate.housing_company.city", read_only=True)


class BuildingSerializer(HitasModelSerializer):
    address = BuildingHitasAddressSerializer(source="*")
    building_identifier = ValueOrNullField(required=False, allow_null=True)

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
        except (RealEstate.DoesNotExist, ValueError):
            raise HitasModelNotFound(model=RealEstate)

        validated_data["real_estate_id"] = real_estate_id
        return validated_data

    class Meta:
        model = Building
        fields = [
            "id",
            "address",
            "building_identifier",
        ]


class BuildingViewSet(HitasModelViewSet):
    serializer_class = BuildingSerializer
    model_class = Building

    def get_queryset(self):
        hc_id = self._lookup_model_id_by_uuid(HousingCompany, "housing_company_uuid")
        re_id = self._lookup_model_id_by_uuid(RealEstate, "real_estate_uuid", housing_company_id=hc_id)

        return (
            Building.objects.filter(real_estate__id=re_id)
            .select_related("real_estate__housing_company__postal_code")
            .only(
                "uuid",
                "street_address",
                "building_identifier",
                "real_estate__housing_company__postal_code__value",
                "real_estate__housing_company__postal_code__city",
            )
            .order_by("id")
        )
