import datetime

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
from hitas.views.utils import HitasDecimalField, HitasModelMixin, HitasModelSerializer
from hitas.views.utils.serializers import YearMonthSerializer


class IndicesSerializer(HitasModelSerializer):
    month = YearMonthSerializer(read_only=True)
    value = HitasDecimalField(allow_null=True)

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
    serializer_class = IndicesSerializer
    lookup_field = "month"

    def __init__(self, model_class, **kwargs):
        self.model_class = model_class
        super().__init__(**kwargs)

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
        return self.model_class.objects.only("month", "value").all().order_by("month")

    def _get_month(self):
        return datetime.datetime.strptime(self.kwargs["month"], "%Y-%m").date()


class MaximumPriceIndexViewSet(_AbstractIndicesViewSet):
    def __init__(self, **kwargs):
        super().__init__(MaximumPriceIndex, **kwargs)


class MarketPriceIndexViewSet(_AbstractIndicesViewSet):
    def __init__(self, **kwargs):
        super().__init__(MarketPriceIndex, **kwargs)


class MarketPriceIndex2005Equal100ViewSet(_AbstractIndicesViewSet):
    def __init__(self, **kwargs):
        super().__init__(MarketPriceIndex2005Equal100, **kwargs)


class ConstructionPriceIndexViewSet(_AbstractIndicesViewSet):
    def __init__(self, **kwargs):
        super().__init__(ConstructionPriceIndex, **kwargs)


class ConstructionPriceIndex2005Equal100ViewSet(_AbstractIndicesViewSet):
    def __init__(self, **kwargs):
        super().__init__(ConstructionPriceIndex2005Equal100, **kwargs)


class SurfaceAreaPriceCeilingViewSet(_AbstractIndicesViewSet):
    def __init__(self, **kwargs):
        super().__init__(SurfaceAreaPriceCeiling, **kwargs)
