import openapi_core
import yaml
from crum import impersonate
from django.contrib.auth import get_user_model
from openapi_core.contrib.django import DjangoOpenAPIRequest, DjangoOpenAPIResponse
from openapi_core.validation.request.datatypes import OpenAPIRequest
from openapi_core.validation.response.validators import ResponseValidator
from rest_framework.response import Response

from hitas.models import Building, HousingCompany, RealEstate

with open("openapi.yaml", "r") as spec_file:
    _openapi_spec = openapi_core.create_spec(yaml.safe_load(spec_file))


from django.core.handlers.wsgi import WSGIRequest


class WSGIRequestWorkaround:
    def __init__(self, r: WSGIRequest):
        self.r = r

    def __getattr__(self, item):
        if item == "body":
            return self.r.META["wsgi.input"].read()

        return getattr(self.r, item)


def validate_openapi(response: Response) -> None:
    global _openapi_spec

    result = ResponseValidator(_openapi_spec).validate(
        _openapi_url_pattern_workaround(DjangoOpenAPIRequest(WSGIRequestWorkaround(response.wsgi_request))),
        DjangoOpenAPIResponse(response),
    )

    result.raise_for_errors()


def _openapi_url_pattern_workaround(original: OpenAPIRequest):
    full_url_pattern = original.full_url_pattern
    # For list view, DefaultRouter creates routes likes this:
    # /api/v1/housing-companies$
    # openapi-core does not understand the last $ when trying to look up the correct OpenAPI definition. let's remove it
    if full_url_pattern[-1:] == "$":
        full_url_pattern = full_url_pattern[:-1]
    # For detail view, DefaultRouter creates routes likes this:
    # - /api/v1/housing-companies/(?P<housing_company_id>[^/.]+)$
    # openapi-core tries to simplify the URL so it can look the correct OpenAPI definition but fails and ends up with:
    # - http://testserver/api/v1/housing-companies/{housing_company_id}/.]+)$
    # Let's remove the /.]+) from the end of the url pattern if it's there ($ was removed in the previous step)
    if full_url_pattern[-5:] == "/.]+)":
        full_url_pattern = full_url_pattern[:-5]

    return OpenAPIRequest(
        full_url_pattern=full_url_pattern,
        method=original.method,
        parameters=original.parameters,
        body=original.body,
        mimetype=original.mimetype,
    )


def create_test_housing_company(idx: int) -> HousingCompany:
    with impersonate(get_user_model().objects.first()):
        return HousingCompany.objects.create(
            display_name=f"test-housing-company-{idx}",
            official_name=f"test-housing-company-{idx}-as-oy",
            street_address=f"test-street-address-{idx}",
            business_id="1234567-8",
            acquisition_price=10.0,
            primary_loan=10.0,
            building_type_id=1,
            developer_id=1,
            financing_method_id=1,
            postal_code_id=1,
            property_manager_id=1,
        )


def create_test_real_estate(hc: HousingCompany, idx: int) -> RealEstate:
    return RealEstate.objects.create(
        housing_company=hc,
        postal_code_id=1,
        property_identifier="091-020-0015-0003",
        street_address=f"test-re-street-address-{idx}",
    )


def create_test_building(re: RealEstate, idx: int, completion_date=None) -> Building:
    return Building.objects.create(
        real_estate=re,
        postal_code_id=1,
        street_address=f"test-b-street-address-{idx}",
        completion_date=completion_date,
    )
