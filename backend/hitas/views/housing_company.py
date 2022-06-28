from collections import defaultdict
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist
from enumfields.drf.serializers import EnumSupportSerializerMixin
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from hitas.exceptions import HousingCompanyNotFound
from hitas.models.housing_company import Building, HousingCompany
from hitas.views.paginator import get_default_paginator


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


class HousingCompanyDetailSerializer(EnumSupportSerializerMixin, serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    area = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    real_estates = serializers.SerializerMethodField()

    def get_name(self, obj):
        return {
            "display": obj.display_name,
            "official": obj.official_name,
        }

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

    def get_real_estates(self, obj):
        # Select all buildings for this housing company with one query instead
        # of having one query per property
        buildings_by_real_estate = defaultdict(list)
        for b in (
            Building.objects.select_related("postal_code")
            .only(
                "street_address",
                "postal_code__value",
                "building_identifier",
                "real_estate__id",
                "completion_date",
            )
            .filter(housing_company__id=obj.id)
        ):
            buildings_by_real_estate[b.real_estate_id].append(b)

        # Fetch real estates
        query = obj.realestate_set.select_related("postal_code").only(
            "street_address",
            "postal_code__value",
            "property_identifier",
            "housing_company__id",
        )

        return list(
            map(
                lambda re: {
                    "address": {
                        "street": re.street_address,
                        "postal_code": re.postal_code.value,
                        "city": re.city,
                    },
                    "property_identifier": re.property_identifier,
                    "buildings": list(
                        map(
                            lambda b: {
                                "address": {
                                    "street": b.street_address,
                                    "postal_code": b.postal_code.value,
                                    "city": b.city,
                                },
                                "building_identifier": b.building_identifier if b.building_identifier != "" else None,
                                "completion_date": b.completion_date,
                            },
                            buildings_by_real_estate[re.id],
                        )
                    ),
                },
                query,
            )
        )

    class Meta:
        model = HousingCompany
        fields = ["id", "business_id", "name", "state", "address", "area", "date", "real_estates"]


class HousingCompanyDetailApiView(APIView):
    def get(self, request, housing_company_id, *args, **kwargs):
        try:
            uuid = UUID(hex=housing_company_id)
        except ValueError:
            raise HousingCompanyNotFound()

        try:
            housing_company = (
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
                .only(
                    "uuid",
                    "state",
                    "postal_code__value",
                    "postal_code__description",
                    "display_name",
                    "street_address",
                    "business_id",
                    "official_name",
                )
                .get(uuid=uuid)
            )
        except ObjectDoesNotExist:
            raise HousingCompanyNotFound()

        serializer = HousingCompanyDetailSerializer(housing_company)
        return Response(serializer.data, status=status.HTTP_200_OK)


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

        paginator = get_default_paginator()
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
