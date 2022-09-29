from rest_framework import serializers

from hitas.models import HitasPostalCode
from hitas.views.utils import HitasCharFilter, HitasFilterSet, HitasModelSerializer, HitasModelViewSet


class HitasPostalCodeFilterSet(HitasFilterSet):
    value = HitasCharFilter(lookup_expr="contains")

    class Meta:
        model = HitasPostalCode
        fields = ["value"]


class HitasPostalCodeSerializer(HitasModelSerializer):
    value = serializers.CharField()
    city = serializers.CharField()
    cost_area = serializers.IntegerField(min_value=1, max_value=4)

    class Meta:
        model = HitasPostalCode
        fields = ["id", "value", "city", "cost_area"]


class HitasPostalCodeViewSet(HitasModelViewSet):
    serializer_class = HitasPostalCodeSerializer
    model_class = HitasPostalCode

    def get_queryset(self):
        return HitasPostalCode.objects.all().order_by("value")

    def get_filterset_class(self):
        return HitasPostalCodeFilterSet
