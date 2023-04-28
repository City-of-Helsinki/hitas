from typing import Any, Optional

from django.db.models import QuerySet
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from hitas.models import Apartment
from hitas.services.apartment import check_current_owners_for_non_disclosure
from hitas.views.apartment import ApartmentFilterSet, ApartmentListSerializer, ApartmentViewSet
from hitas.views.utils import HitasModelMixin


class ApartmentListViewSet(HitasModelMixin, GenericViewSet):
    model_class = Apartment
    list_serializer_class = ApartmentListSerializer

    def get_list_queryset(self):
        return ApartmentViewSet.get_base_queryset()

    def get_filterset_class(self):
        return ApartmentFilterSet

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset: QuerySet[Apartment] = self.filter_queryset(self.get_queryset())

        page: Optional[list[Apartment]] = self.paginate_queryset(queryset)
        if page is not None:
            for apartment in page:
                check_current_owners_for_non_disclosure(apartment)

            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        for apartment in queryset:
            check_current_owners_for_non_disclosure(apartment)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
