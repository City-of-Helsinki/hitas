from django.core.paginator import EmptyPage, PageNotAnInteger
from rest_framework.pagination import PageNumberPagination

from hitas.exceptions import InvalidPage


def get_default_paginator():
    paginator = HitasPagination()
    paginator.page_size = 10
    paginator.page_size_query_param = "limit"
    paginator.max_page_size = 100

    return paginator


class HitasPagination(PageNumberPagination):
    def get_page_number(self, request, paginator):
        """
        Overwrite this function from PageNumberPagination so that
        the errors are handled a bit differently.

        `PageNumberPagination.paginate_queryset` will first call this and then eventually call `Paginator.page()` which
        will validate the page number as well. if that raises an error then `PageNumberPagination` will raise `Http404`
        which we don't want.
        """

        number = super(HitasPagination, self).get_page_number(request, paginator)

        try:
            paginator.validate_number(number)
        except PageNotAnInteger:
            raise InvalidPage()
        except EmptyPage:
            if int(number) < 1:
                # If the given page number is an integer but not a positive one, then we throw the invalid page
                # exception as well
                raise InvalidPage()
            else:
                # if the given page is higher than maximum number of pages then let's just return the last page
                number = paginator.num_pages

        return number
