from copy import deepcopy

from django_filters import CharFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, filterset

# By default exact matches are used
# Set a lookup expression for all text-type fields
FILTER_FOR_DBFIELD_DEFAULTS = deepcopy(filterset.FILTER_FOR_DBFIELD_DEFAULTS)
for (field_class, filter_class) in FILTER_FOR_DBFIELD_DEFAULTS.items():
    if filter_class["filter_class"] == CharFilter:
        FILTER_FOR_DBFIELD_DEFAULTS[field_class]["extra"] = lambda f: {"lookup_expr": "icontains"}


class HitasFilterSet(FilterSet):
    FILTER_DEFAULTS = FILTER_FOR_DBFIELD_DEFAULTS


class HitasFilterBackend(DjangoFilterBackend):
    def get_filterset_class(self, view, queryset=None):
        """Allow setting the filterset_class through a method"""
        get_filterset_class_method = getattr(view, "get_filterset_class", None)

        if get_filterset_class_method:
            # If get_filterset_class method is defined, override filterset_class property
            view.filterset_class = get_filterset_class_method()

        return super().get_filterset_class(view, queryset)
