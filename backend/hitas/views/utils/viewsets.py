from uuid import UUID

from django.db import models
from django.http import Http404
from django_filters.rest_framework import filters
from rest_framework import viewsets

from hitas.exceptions import HitasModelNotFound
from hitas.views.utils import HitasFilterSet, HitasPagination


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
            self.kwargs[lookup_url_kwarg] = self._lookup_id_to_uuid(self.kwargs[lookup_url_kwarg])
        try:
            return super().get_object()
        except Http404:
            raise HitasModelNotFound(model=self.model_class)

    def get_serializer_class(self):
        if self.action == "list" and self.list_serializer_class is not None:
            return self.list_serializer_class
        return self.serializer_class

    def _lookup_id_to_uuid(self, s: str, model_class=None) -> UUID:
        try:
            return UUID(hex=str(s))
        except ValueError:
            raise HitasModelNotFound(model=model_class if model_class else self.model_class)

    def _lookup_model_id_by_uuid(self, model_class, arg_name, **kwargs):
        uuid = self._lookup_id_to_uuid(self.kwargs[arg_name], model_class)

        try:
            return model_class.objects.only("id").get(uuid=uuid, **kwargs).id
        except model_class.DoesNotExist:
            raise HitasModelNotFound(model=model_class)

    def get_filterset_class(self):
        """Automagically generate a Filter Set class for subclassing ViewSets"""

        class HitasModelFilterSet(HitasFilterSet):

            if (
                hasattr(self.model_class, "postal_code")
                and hasattr(self.model_class.postal_code, "field")
                and self.model_class.postal_code.field.__class__ == models.ForeignKey
            ):
                postal_code = filters.CharFilter(field_name="postal_code__value")

            class Meta:
                model = self.model_class
                fields = "__all__"

        HitasModelFilterSet.__name__ = f"{self.model_class}FilterSet"

        return HitasModelFilterSet


class HitasModelViewSet(HitasModelMixin, viewsets.ModelViewSet):
    pass
