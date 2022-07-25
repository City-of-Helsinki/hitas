from hitas.models import Person
from hitas.views.utils import AddressSerializer, HitasModelSerializer, HitasModelViewSet


class PersonSerializer(HitasModelSerializer):
    address = AddressSerializer(source="*")

    class Meta:
        model = Person
        fields = [
            "id",
            "first_name",
            "last_name",
            "social_security_number",
            "email",
            "address",
        ]


class PersonViewSet(HitasModelViewSet):
    serializer_class = PersonSerializer
    model_class = Person

    def get_queryset(self):
        return Person.objects.select_related("postal_code")
