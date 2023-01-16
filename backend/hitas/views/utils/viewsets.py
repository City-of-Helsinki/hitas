from django.http import Http404
from rest_framework import viewsets

from hitas.exceptions import HitasModelNotFound
from hitas.utils import lookup_id_to_uuid
from hitas.views.utils import HitasPagination


class HitasModelMixin:
    serializer_class = None
    list_serializer_class = None
    model_class = None
    lookup_field = "uuid"
    pagination_class = HitasPagination

    def get_list_queryset(self):
        return super().get_queryset()

    def get_detail_queryset(self):
        return super().get_queryset()

    def get_queryset(self):
        if self.action == "list":
            return self.get_list_queryset()
        else:
            return self.get_detail_queryset()

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if lookup_url_kwarg == "uuid":
            self.kwargs[lookup_url_kwarg] = lookup_id_to_uuid(self.kwargs[lookup_url_kwarg], self.model_class)
        try:
            return super().get_object()
        except Http404:
            raise HitasModelNotFound(model=self.model_class)

    def get_serializer_class(self):
        if self.action == "list" and self.list_serializer_class is not None:
            return self.list_serializer_class
        return self.serializer_class


class HitasModelViewSet(HitasModelMixin, viewsets.ModelViewSet):
    pass
