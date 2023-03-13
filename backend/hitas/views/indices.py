import datetime
from typing import ClassVar

from django.db.models import Q
from rest_framework import mixins
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from hitas.exceptions import HitasModelNotFound
from hitas.models import (
    ConstructionPriceIndex,
    ConstructionPriceIndex2005Equal100,
    MarketPriceIndex,
    MarketPriceIndex2005Equal100,
    MaximumPriceIndex,
    SurfaceAreaPriceCeiling,
)
from hitas.models.indices import AbstractIndex
from hitas.views.utils import (
    HitasDecimalField,
    HitasFilterSet,
    HitasIntegerFilter,
    HitasModelMixin,
    HitasModelSerializer,
)
from hitas.views.utils.serializers import YearMonthSerializer


class IndicesFilterSet(HitasFilterSet):
    year = HitasIntegerFilter(method="year_filter", min_value=1970, max_value=2099)

    def year_filter(self, queryset, name, value):
        return queryset.filter(
            Q(month__gte=datetime.date(value, month=1, day=1)) & Q(month__lt=datetime.date(value + 1, month=1, day=1))
        )

    class Meta:
        model = AbstractIndex
        fields = ["year"]


class IndicesSerializer(HitasModelSerializer):
    month = YearMonthSerializer(read_only=True)
    value = HitasDecimalField(allow_null=True, min_value=1)

    class Meta:
        model = MarketPriceIndex
        fields = [
            "month",
            "value",
        ]


class _AbstractIndicesViewSet(
    HitasModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    model_class: ClassVar[type[AbstractIndex]]
    serializer_class = IndicesSerializer
    lookup_field = "month"

    def update(self, request, *args, **kwargs):
        if request.data["value"] is None:
            month = self._get_month()

            # Delete the object
            self.model_class.objects.filter(month=month).delete()

            # Recreate new empty instance and return that
            instance = self.model_class(month=month)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return super().update(request, *args, **kwargs)

    def get_object(self):
        try:
            self.kwargs["month"] = self._get_month()
        except ValueError:
            raise ValidationError(
                {"month": ErrorDetail("Field has to be a valid month in format 'yyyy-mm'.", "invalid")}
            )

        try:
            return super().get_object()
        except HitasModelNotFound:
            return self.model_class(month=self.kwargs["month"])

    def get_queryset(self):
        return self.model_class.objects.only("month", "value").all().order_by("-month")

    def _get_month(self):
        return datetime.datetime.strptime(self.kwargs["month"], "%Y-%m").date()

    @staticmethod
    def get_filterset_class():
        return IndicesFilterSet


class MaximumPriceIndexViewSet(_AbstractIndicesViewSet):
    model_class = MaximumPriceIndex


class MarketPriceIndexViewSet(_AbstractIndicesViewSet):
    model_class = MarketPriceIndex


class MarketPriceIndex2005Equal100ViewSet(_AbstractIndicesViewSet):
    model_class = MarketPriceIndex2005Equal100


class ConstructionPriceIndexViewSet(_AbstractIndicesViewSet):
    model_class = ConstructionPriceIndex


class ConstructionPriceIndex2005Equal100ViewSet(_AbstractIndicesViewSet):
    model_class = ConstructionPriceIndex2005Equal100


class SurfaceAreaPriceCeilingViewSet(_AbstractIndicesViewSet):
    model_class = SurfaceAreaPriceCeiling
