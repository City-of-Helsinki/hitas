from hitas.models import Person
from hitas.views.utils import HitasModelSerializer, HitasModelViewSet


class PersonSerializer(HitasModelSerializer):
    class Meta:
        model = Person
        fields = [
            "id",
            "first_name",
            "last_name",
            "social_security_number",
            "email",
        ]


class PersonViewSet(HitasModelViewSet):
    serializer_class = PersonSerializer
    model_class = Person

    def get_queryset(self):
        return Person.objects.all().order_by("id")
