from typing import Optional

import yaml
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from openapi_core import Spec
from openapi_core.contrib.django import DjangoOpenAPIRequest, DjangoOpenAPIResponse
from openapi_core.templating.paths.datatypes import ServerOperationPath
from openapi_core.unmarshalling.schemas import oas30_request_schema_unmarshallers_factory
from openapi_core.validation.request.protocols import Request
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response import openapi_response_validator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

with open(f"{settings.BASE_DIR}/openapi.yaml", "r") as spec_file:
    _openapi_spec = Spec.create(yaml.safe_load(spec_file))


class WSGIRequestWorkaround:
    """
    Body is only readable once so keep a copy of it for validation purposes. DRF reads it once before us
    """

    def __init__(self, r: WSGIRequest, request_body: str):
        self.r = r
        self.request_body = request_body

    def __getattr__(self, item):
        if item == "body":
            return self.request_body

        return getattr(self.r, item)


def validate_openapi(
    request_body: str, response: Response, validate_request: bool = True, validate_response: bool = True
) -> None:
    global _openapi_spec

    if not validate_request and not validate_response:
        return

    # Add the `Content-Type` key to response, so DjangoOpenAPIResponseFactory doesn't crash on DELETE requests
    if response.status_code == status.HTTP_204_NO_CONTENT:
        response["Content-Type"] = None

    # Validate request
    if validate_request:
        result = RequestValidatorWorkaround(
            schema_unmarshallers_factory=oas30_request_schema_unmarshallers_factory
        ).validate(
            _openapi_spec, OpenAPIUrlPatternWorkaround(WSGIRequestWorkaround(response.wsgi_request, request_body))
        )

        result.raise_for_errors()

    # Validate response
    if validate_response:
        result = openapi_response_validator.validate(
            _openapi_spec,
            OpenAPIUrlPatternWorkaround(response.wsgi_request),
            DjangoOpenAPIResponse(response),
        )
        result.raise_for_errors()


class RequestValidatorWorkaround(RequestValidator):
    def _find_path(self, spec: Spec, request: Request, base_url: Optional[str] = None) -> ServerOperationPath:
        result = super()._find_path(spec, request, base_url)

        # Workaround
        for k, v in result[3].variables.items():
            if k not in request.parameters.path:
                request.parameters.path[k] = v

        return result


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
        self,
        method,
        path,
        data="",
        content_type="json",
        secure=False,
        openapi_validate=True,
        openapi_validate_request=True,
        openapi_validate_response=True,
        **kwargs,
    ) -> Response:
        response: Response = super().generic(method, path, data, content_type, secure=False, **kwargs)

        validate_openapi(
            data,
            response,
            openapi_validate and openapi_validate_request,
            openapi_validate and openapi_validate_response,
        )

        return response
