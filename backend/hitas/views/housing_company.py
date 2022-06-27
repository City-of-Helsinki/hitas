from django.core.paginator import EmptyPage, PageNotAnInteger
from enumfields.drf.serializers import EnumSupportSerializerMixin
from rest_framework import serializers, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from hitas.exceptions import InvalidPage
from hitas.models.housing_company import HousingCompany


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


class HousingCompanyListSerializer(EnumSupportSerializerMixin, serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.CharField(source="display_name", max_length=1024)
    state = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    area = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.uuid.hex

    def get_state(self, obj):
        return obj.state.name.lower()

    def get_address(self, obj):
        return {
            "street": obj.street_address,
            "postal_code": obj.postal_code.value,
            "city": obj.city,
        }

    def get_area(self, obj):
        return {"name": obj.postal_code.description, "cost_area": obj.area}

    def get_date(self, obj):
        return obj.date

    class Meta:
        model = HousingCompany
        fields = ["id", "name", "state", "address", "area", "date"]


class HousingCompanyListApiView(APIView):
    def get(self, request, *args, **kwargs):
        housing_companies = (
            HousingCompany.objects.extra(
                select={
                    "date": """
SELECT MIN(completion_date) FROM hitas_building AS b
    LEFT JOIN hitas_realestate AS re ON b.real_estate_id = re.id
    WHERE re.housing_company_id = hitas_housingcompany.id
"""
                }
            )
            .select_related("postal_code")
            .only("uuid", "state", "postal_code__value", "postal_code__description", "display_name", "street_address")
        )

        paginator = HitasPagination()
        paginator.page_size = 10
        paginator.page_size_query_param = "limit"
        paginator.max_page_size = 100
        result_page = paginator.paginate_queryset(housing_companies, request)
        serializer = HousingCompanyListSerializer(result_page, many=True)

        return Response(
            {
                "page": {
                    "current_page": paginator.page.number,
                    "size": len(result_page),
                    "total_items": paginator.page.paginator.count,
                    "total_pages": paginator.page.paginator.num_pages,
                    "links": {
                        "next": paginator.get_next_link(),
                        "previous": paginator.get_previous_link(),
                    },
                },
                "contents": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
