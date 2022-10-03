from typing import Optional

import yaml
from django.conf import settings
from openapi_core import Spec
from openapi_core.contrib.django import DjangoOpenAPIRequest, DjangoOpenAPIResponse
from openapi_core.validation.response import openapi_response_validator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

with open(f"{settings.BASE_DIR}/openapi.yaml", "r") as spec_file:
    _openapi_spec = Spec.create(yaml.safe_load(spec_file))


def validate_openapi(response: Response) -> None:
    global _openapi_spec

    # Add the `Content-Type` key to response, so DjangoOpenAPIResponseFactory doesn't crash on DELETE requests
    if response.status_code == status.HTTP_204_NO_CONTENT:
        response["Content-Type"] = None

    result = openapi_response_validator.validate(
        _openapi_spec,
        OpenAPIUrlPatternWorkaround(response.wsgi_request),
        DjangoOpenAPIResponse(response),
    )

    result.raise_for_errors()


class OpenAPIUrlPatternWorkaround(DjangoOpenAPIRequest):
    @property
    def path_pattern(self) -> Optional[str]:
        if self.request.resolver_match is None:
            return None

        route = self.request.resolver_match.route

        # For detail view, DefaultRouter creates routes likes this:
        # - /api/v1/housing-companies/(?P<housing_company_id>[^/.]+)$
        # openapi-core tries to simplify the URL so it can look the
        # correct OpenAPI definition but fails and ends up with:
        # - http://testserver/api/v1/housing-companies/{housing_company_id}/.]+)$
        # - http://testserver/api/v1/housing-companies/{housing_company_id}/.]+)/real-estates$
        # Let's remove the /.]+) from the url pattern if it's there ($ was removed in the previous step)
        if route.find("/.]+)"):
            route = route.replace("/.]+)", "")

        route = self.path_regex.sub(r"{\1}", route)
        # Delete start and end marker to allow concatenation.
        if route[:1] == "^":
            route = route[1:]
        if route[-1:] == "$":
            route = route[:-1]
        return "/" + route


class HitasAPIClient(APIClient):
    def generic(
        self, method, path, data="", content_type="json", secure=False, openapi_validate=True, **kwargs
    ) -> Response:
        response: Response = super().generic(method, path, data, content_type, secure=False, **kwargs)

        if openapi_validate:
            validate_openapi(response)

        return response
