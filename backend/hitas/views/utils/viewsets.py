from django.db import models
from django.http import Http404
from rest_framework import serializers, viewsets

from hitas.exceptions import HitasModelNotFound
from hitas.utils import lookup_id_to_uuid
from hitas.views.utils import HitasPagination


class HitasModelMixin:
    serializer_class: type[serializers.Serializer] = None
    list_serializer_class: type[serializers.Serializer] = None
    detail_serializer_class: type[serializers.Serializer] = None
    create_serializer_class: type[serializers.Serializer] = None
    update_serializer_class: type[serializers.Serializer] = None
    partial_update_serializer_class: type[serializers.Serializer] = None

    model_class: type[models.Model] = None
    lookup_field = "uuid"
    pagination_class = HitasPagination

    def get_default_queryset(self):
        return self.model_class.objects.all()

    def get_list_queryset(self):
        return self.get_default_queryset()

    def get_detail_queryset(self):
        return self.get_default_queryset()

    def get_create_queryset(self):
        return self.get_detail_queryset()

    def get_update_queryset(self):
        return self.get_detail_queryset()

    def get_partial_update_queryset(self):
        return self.get_update_queryset()

    def get_delete_queryset(self):
        return self.get_detail_queryset()

    def get_queryset(self):
        if self.action == "list":
            return self.get_list_queryset()
        if self.action == "retrieve":
            return self.get_detail_queryset()
        if self.action == "create":
            return self.get_create_queryset()
        if self.action == "update":
            return self.get_update_queryset()
        if self.action == "partial_update":
            return self.get_partial_update_queryset()
        if self.action == "delete":
            return self.get_delete_queryset()

        if self.detail:
            return self.get_detail_queryset()
        return self.get_list_queryset()

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if lookup_url_kwarg == "uuid":
            self.kwargs[lookup_url_kwarg] = lookup_id_to_uuid(self.kwargs[lookup_url_kwarg], self.model_class)
        try:
            return super().get_object()
        except Http404 as error:
            raise HitasModelNotFound(model=self.model_class) from error

    def get_serializer_class(self):
        if self.action == "list" and self.list_serializer_class is not None:
            return self.list_serializer_class

        if self.action == "retrieve" and self.detail_serializer_class is not None:
            return self.detail_serializer_class

        if self.action == "create" and self.create_serializer_class is not None:
            return self.create_serializer_class

        if self.action == "update":
            if self.update_serializer_class is not None:
                return self.update_serializer_class

        if self.action == "partial_update":
            if self.partial_update_serializer_class is not None:
                return self.partial_update_serializer_class
            if self.update_serializer_class is not None:
                return self.update_serializer_class

        return self.serializer_class


class HitasModelViewSet(HitasModelMixin, viewsets.ModelViewSet):
    pass
