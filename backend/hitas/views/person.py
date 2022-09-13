from django.db.models import Q

from hitas.models import Person
from hitas.views.utils import HitasCharFilter, HitasFilterSet, HitasModelSerializer, HitasModelViewSet, HitasSSNFilter


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


class PersonFilterSet(HitasFilterSet):
    name = HitasCharFilter(method="name_filter")
    social_security_number = HitasSSNFilter(lookup_expr="iexact")
    email = HitasCharFilter(lookup_expr="iexact")

    def name_filter(self, queryset, name, value):
        return queryset.filter(Q(first_name__icontains=value) | Q(last_name__icontains=value))

    class Meta:
        model = Person
        fields = ["name", "social_security_number", "email"]


class PersonViewSet(HitasModelViewSet):
    serializer_class = PersonSerializer
    model_class = Person

    def get_queryset(self):
        return Person.objects.all().order_by("id")

    def get_filterset_class(self):
        return PersonFilterSet
