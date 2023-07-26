import datetime
from typing import ClassVar

from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.http import HttpResponse
from rest_framework import mixins, serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework.request import Request
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
from hitas.models.indices import AbstractIndex, SurfaceAreaPriceCeilingCalculationData
from hitas.services.indices import (
    build_surface_area_price_ceiling_report_excel,
    calculate_surface_area_price_ceiling,
    get_surface_area_price_ceiling_results,
)
from hitas.utils import from_iso_format_or_today_if_none
from hitas.views.utils import (
    HitasDecimalField,
    HitasFilterSet,
    HitasIntegerFilter,
    HitasModelMixin,
    HitasModelSerializer,
)
from hitas.views.utils.excel import get_excel_response
from hitas.views.utils.serializers import YearMonthSerializer

# Indices


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

    def create(self, request: Request, *args, **kwargs) -> Response:
        try:
            calculation_date = from_iso_format_or_today_if_none(request.query_params.get("calculation_date"))
        except ValueError as error:
            raise ValidationError({"calculation_date": str(error)}) from error

        result = calculate_surface_area_price_ceiling(calculation_date)
        return Response(data=result, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        url_path=r"reports/download-surface-area-price-ceiling-results",
        url_name="results",
    )
    def surface_area_price_ceiling_results(self, request: Request, *args, **kwargs) -> HttpResponse:
        try:
            calculation_date = from_iso_format_or_today_if_none(request.query_params.get("calculation_date"))
        except ValueError as error:
            raise ValidationError({"calculation_date": str(error)}) from error

        results = get_surface_area_price_ceiling_results(calculation_date)
        workbook = build_surface_area_price_ceiling_report_excel(results)
        filename = (
            f"Rajaneliöhinnan laskentaraportti ({results.calculation_month.strftime('%Y-%m')} - "
            f"{(results.calculation_month + relativedelta(months=2)).strftime('%Y-%m')}).xlsx"
        )
        return get_excel_response(filename=filename, excel=workbook)


# SAPC Calculation


class SurfaceAreaPriceCeilingCalculationDataFilterSet(HitasFilterSet):
    year = HitasIntegerFilter(method="year_filter", min_value=1970, max_value=2099)

    def year_filter(self, queryset, name, value):
        return queryset.filter(
            Q(calculation_month__gte=datetime.date(value, month=1, day=1))
            & Q(calculation_month__lt=datetime.date(value + 1, month=1, day=1))
        )

    class Meta:
        model = SurfaceAreaPriceCeilingCalculationData
        fields = ["year"]


class CreatedSAPCSerializer(serializers.Serializer):
    month = serializers.DateField()
    value = HitasDecimalField()


class HousingCompanyDataSerializer(serializers.Serializer):
    name = serializers.CharField()
    completion_date = serializers.DateField()
    surface_area = HitasDecimalField()
    realized_acquisition_price = HitasDecimalField()
    unadjusted_average_price_per_square_meter = HitasDecimalField()
    adjusted_average_price_per_square_meter = HitasDecimalField()
    completion_month_index = HitasDecimalField()
    calculation_month_index = HitasDecimalField()


class CalculationDataSerializer(serializers.Serializer):
    housing_company_data = HousingCompanyDataSerializer(many=True)
    created_surface_area_price_ceilings = CreatedSAPCSerializer(many=True)


class SurfaceAreaPriceCeilingCalculationDataSerializer(HitasModelSerializer):
    calculation_month = serializers.DateField()
    data = CalculationDataSerializer()

    class Meta:
        model = SurfaceAreaPriceCeilingCalculationData
        fields = [
            "calculation_month",
            "data",
        ]


class SurfaceAreaPriceCeilingCalculationDataViewSet(
    HitasModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    serializer_class = SurfaceAreaPriceCeilingCalculationDataSerializer
    lookup_field = "calculation_month"

    @staticmethod
    def get_filterset_class():
        return SurfaceAreaPriceCeilingCalculationDataFilterSet

    def get_default_queryset(self):
        return SurfaceAreaPriceCeilingCalculationData.objects.order_by("-calculation_month")

    def get_object(self):
        try:
            self.kwargs["calculation_month"] = datetime.date.fromisoformat(self.kwargs["calculation_month"])
        except (KeyError, ValueError):
            raise ValidationError(
                detail={"calculation_month": "Field has to be a valid month in format 'yyyy-mm'."},
                code="invalid",
            )

        return super().get_object()
