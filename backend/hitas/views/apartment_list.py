from rest_framework import mixins, viewsets

from hitas.models import Apartment
from hitas.views.apartment import ApartmentFilterSet, ApartmentListSerializer, ApartmentViewSet
from hitas.views.utils import HitasModelMixin


class ApartmentListViewSet(HitasModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    model_class = Apartment
    list_serializer_class = ApartmentListSerializer

    def get_list_queryset(self):
        return ApartmentViewSet.get_base_queryset()

    def get_filterset_class(self):
        return ApartmentFilterSet
