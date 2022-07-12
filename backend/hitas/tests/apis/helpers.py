import openapi_core
import yaml
from django.conf import settings
from openapi_core.contrib.django import DjangoOpenAPIRequest, DjangoOpenAPIResponse
from openapi_core.validation.request.datatypes import OpenAPIRequest
from openapi_core.validation.response.validators import ResponseValidator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

with open(f"{settings.BASE_DIR}/openapi.yaml", "r") as spec_file:
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

    # Add the `Content-Type` key to response, so DjangoOpenAPIResponseFactory doesn't crash on DELETE requests
    if response.status_code == status.HTTP_204_NO_CONTENT:
        response["Content-Type"] = None

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
    # - http://testserver/api/v1/housing-companies/{housing_company_id}/.]+)/real-estates$
    # Let's remove the /.]+) from the url pattern if it's there ($ was removed in the previous step)
    if full_url_pattern.find("/.]+)"):
        full_url_pattern = full_url_pattern.replace("/.]+)", "")

    return OpenAPIRequest(
        full_url_pattern=full_url_pattern,
        method=original.method,
        parameters=original.parameters,
        body=original.body,
        mimetype=original.mimetype,
    )


class HitasAPIClient(APIClient):
    def generic(self, method, path, data="", content_type="json", secure=False, **kwargs):
        response = super().generic(method, path, data, content_type, secure=False, **kwargs)
        validate_openapi(response)
        return response
