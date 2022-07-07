from typing import Any, Optional, TypedDict
from uuid import UUID

from django.http import Http404
from rest_framework import viewsets

from hitas.views.paginator import HitasPagination


def value_or_none(s: str) -> Optional[str]:
    return s if s != "" else None


class Address(TypedDict):
    street: str
    postal_code: str
    city: str


def address_obj(obj: Any) -> Address:
    return {
        "street": obj.street_address,
        "postal_code": obj.postal_code.value,
        "city": obj.city,
    }


class HitasModelViewSet(viewsets.ModelViewSet):
    serializer_class = None
    list_serializer_class = None
    not_found_exception_class = None
    permission_classes = []
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
            raise self.not_found_exception_class()

    def get_serializer_class(self):
        if self.action == "list":
            return self.list_serializer_class
        return self.serializer_class

    def _lookup_id_to_uuid(self, s: str) -> UUID:
        try:
            return UUID(hex=s)
        except ValueError:
            raise self.not_found_exception_class()
