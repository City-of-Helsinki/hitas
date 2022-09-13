from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

from hitas.models import Ownership, Person
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

    def destroy(self, request, *args, **kwargs):
        instance: Person = self.get_object()

        number_of_ownerships = Ownership.objects.filter(owner__id=instance.id).count()
        if number_of_ownerships > 0:
            return Response(
                {
                    "error": "person_in_use",
                    "message": "Person has active ownerships and cannot be removed.",
                    "reason": "Conflict",
                    "status": 409,
                },
                status=status.HTTP_409_CONFLICT,
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        return Person.objects.all().order_by("id")

    def get_filterset_class(self):
        return PersonFilterSet
