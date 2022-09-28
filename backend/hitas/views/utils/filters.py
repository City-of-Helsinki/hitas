from copy import deepcopy
from uuid import UUID

from django.core.validators import RegexValidator
from django_filters import CharFilter
from django_filters.constants import EMPTY_VALUES
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, filters, filterset

# By default exact matches are used
# Set a lookup expression for all text-type fields
from hitas.exceptions import HitasModelNotFound

FILTER_FOR_DBFIELD_DEFAULTS = deepcopy(filterset.FILTER_FOR_DBFIELD_DEFAULTS)
for (field_class, filter_class) in FILTER_FOR_DBFIELD_DEFAULTS.items():
    if filter_class["filter_class"] == CharFilter:
        FILTER_FOR_DBFIELD_DEFAULTS[field_class]["extra"] = lambda f: {"lookup_expr": "icontains"}


class HitasFilterSet(FilterSet):
    FILTER_DEFAULTS = FILTER_FOR_DBFIELD_DEFAULTS


class HitasCharFilter(filters.CharFilter):
    def __init__(self, *args, **kwargs):
        kwargs["min_length"] = 3
        super().__init__(*args, **kwargs)


class HitasPostalCodeFilter(filters.CharFilter):
    def __init__(self, *args, **kwargs):
        kwargs["validators"] = [RegexValidator(r"^\d{5}$")]
        super().__init__(*args, **kwargs)


class HitasSSNFilter(filters.CharFilter):
    def __init__(self, *args, **kwargs):
        kwargs["min_length"] = 6
        kwargs["max_length"] = 11
        super().__init__(*args, **kwargs)


class HitasFilterBackend(DjangoFilterBackend):
    def get_filterset_class(self, view, queryset=None):
        """Allow setting the filterset_class through a method"""
        get_filterset_class_method = getattr(view, "get_filterset_class", None)

        if get_filterset_class_method:
            # If get_filterset_class method is defined, override filterset_class property
            view.filterset_class = get_filterset_class_method()

        return super().get_filterset_class(view, queryset)


class HitasUUIDFilter(CharFilter):
    def filter(self, qs, value):
        """Convert passed hex value to uuid4 format, which is used for filtering"""
        if value in EMPTY_VALUES:
            return qs

        try:
            value = UUID(hex=str(value))
        except ValueError:
            raise HitasModelNotFound(model=qs.model)
        return super().filter(qs, value)
