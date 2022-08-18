from uuid import UUID

from hitas.exceptions import HitasModelNotFound
from hitas.models import HousingCompany, RealEstate
from hitas.views.building import BuildingSerializer
from hitas.views.utils import HitasAddressSerializer, HitasModelSerializer, HitasModelViewSet


class RealEstateSerializer(HitasModelSerializer):
    address = HitasAddressSerializer(source="*")
    buildings = BuildingSerializer(many=True, read_only=True)

    @property
    def validated_data(self):
        """Inject related Housing Company ID to the validated data"""
        validated_data = super().validated_data
        try:
            housing_company_uuid = UUID(hex=self.context["view"].kwargs.get("housing_company_uuid"))
            housing_company_id = HousingCompany.objects.get(uuid=housing_company_uuid).id
        except (HousingCompany.DoesNotExist, ValueError):
            raise HitasModelNotFound(model=HousingCompany)

        validated_data["housing_company_id"] = housing_company_id
        return validated_data

    class Meta:
        model = RealEstate
        fields = [
            "id",
            "address",
            "property_identifier",
            "buildings",
        ]


class RealEstateViewSet(HitasModelViewSet):
    serializer_class = RealEstateSerializer
    model_class = RealEstate

    def get_queryset(self):
        uuid = self._lookup_id_to_uuid(self.kwargs["housing_company_uuid"])
        return RealEstate.objects.filter(housing_company__uuid=uuid).select_related("postal_code")
