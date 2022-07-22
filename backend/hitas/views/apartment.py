from enumfields.drf import EnumSupportSerializerMixin

from hitas.models import Apartment
from hitas.views.utils import AddressSerializer, HitasModelSerializer, HitasModelViewSet


class ApartmentSerializer(EnumSupportSerializerMixin, HitasModelSerializer):
    address = AddressSerializer(source="*")

    class Meta:
        model = Apartment
        fields = [
            "id",
            "building",
            "state",
            "apartment_type",
            "surface_area",
            "share_number_start",
            "share_number_end",
            "address",
            "postal_code",
            "apartment_number",
            "floor",
            "stair",
            "debt_free_purchase_price",
            "purchase_price",
            "acquisition_price",
            "primary_loan_amount",
            "loans_during_construction",
            "interest_during_construction",
        ]


class ApartmentViewSet(HitasModelViewSet):
    serializer_class = ApartmentSerializer
    model_class = Apartment

    def get_queryset(self):
        return Apartment.objects.select_related("postal_code")
