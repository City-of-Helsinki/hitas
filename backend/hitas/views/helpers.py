from typing import Optional
from uuid import UUID

from django.http import Http404
from rest_framework import serializers, viewsets
from rest_framework.relations import SlugRelatedField

from hitas.exceptions import HitasModelNotFound
from hitas.models import PostalCode
from hitas.views.paginator import HitasPagination


def value_or_none(s: str) -> Optional[str]:
    return s if s != "" else None


class HitasModelViewSet(viewsets.ModelViewSet):
    serializer_class = None
    list_serializer_class = None
    permission_classes = []
    lookup_field = "uuid"
    pagination_class = HitasPagination

    def get_model_class(self):
        # Simplest way of getting the viewset model without explicitly declaring it
        return self.get_queryset().model

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
            raise HitasModelNotFound(model=self.get_model_class())

    def get_serializer_class(self):
        if self.action == "list":
            return self.list_serializer_class
        return self.serializer_class

    def _lookup_id_to_uuid(self, s: str) -> UUID:
        try:
            return UUID(hex=str(s))
        except ValueError:
            raise HitasModelNotFound(model=self.get_model_class())


class ValueOrNullField(serializers.Field):
    def to_representation(self, value):
        return value_or_none(value)

    def to_internal_value(self, data):
        return data


class UUIDRelatedField(SlugRelatedField):
    def __init__(self, **kwargs):
        super().__init__(slug_field="uuid", **kwargs)

    def to_representation(self, obj):
        return getattr(obj, self.slug_field).hex

    def to_internal_value(self, data: str):
        try:
            return super().to_internal_value(data=UUID(hex=str(data)))
        except ValueError:
            raise HitasModelNotFound(model=self.get_queryset().model)


class PostalCodeField(SlugRelatedField):
    def __init__(self, **kwargs):
        super().__init__(slug_field="value", queryset=PostalCode.objects.all(), **kwargs)

    def to_representation(self, instance: PostalCode):
        return instance.value

    def to_internal_value(self, data: str):
        try:
            return super().to_internal_value(data=data)
        except ValueError:
            raise HitasModelNotFound(model=PostalCode)


class HitasDecimalField(serializers.DecimalField):
    def __init__(self, max_digits=15, decimal_places=2, min_value=0, **kwargs):
        super().__init__(max_digits, decimal_places, min_value, **kwargs)


class AddressSerializer(serializers.Serializer):
    street = serializers.CharField(source="street_address")
    postal_code = PostalCodeField()
    city = serializers.CharField(read_only=True)
