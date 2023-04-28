from contextlib import contextmanager
from typing import Any, NamedTuple, Optional, TypedDict, TypeVar

import pytest
import sqlparse
import yaml
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.db import connection
from openapi_core import Spec
from openapi_core.contrib.django import DjangoOpenAPIRequest, DjangoOpenAPIResponse
from openapi_core.templating.paths.datatypes import ServerOperationPath
from openapi_core.unmarshalling.schemas import oas30_request_schema_unmarshallers_factory
from openapi_core.unmarshalling.schemas.exceptions import InvalidSchemaValue
from openapi_core.validation.request.protocols import Request
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response import openapi_response_validator
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


class DjangoOpenAPIResponseWorkaround(DjangoOpenAPIResponse):
    @property
    def data(self) -> str:
        if self.response.headers["content-type"] == "application/json":
            return self.response.content.decode("utf-8")
        else:
            return self.response.content


def validate_openapi(
    request_body: str, response: Response, validate_request: bool = True, validate_response: bool = True
) -> None:
    global _openapi_spec

    if not validate_request and not validate_response:
        return

    # Validate request
    if validate_request:
        result = RequestValidatorWorkaround(
            schema_unmarshallers_factory=oas30_request_schema_unmarshallers_factory
        ).validate(
            _openapi_spec, OpenAPIUrlPatternWorkaround(WSGIRequestWorkaround(response.wsgi_request, request_body))
        )
        handle_result(result)

    # Validate response
    if validate_response:
        result = openapi_response_validator.validate(
            _openapi_spec,
            OpenAPIUrlPatternWorkaround(response.wsgi_request),
            DjangoOpenAPIResponseWorkaround(response),
        )
        handle_result(result)


def handle_result(result):
    for error in result.errors:
        if isinstance(error, InvalidSchemaValue):
            for suberror in error.schema_errors:
                print(suberror)  # noqa: T201

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


def parametrize_invalid_foreign_key(field, nullable=False):
    parameters = [
        ({field: "foo"}, [{"field": field, "message": "Invalid data. Expected a dictionary, but got str."}]),
        ({field: {}}, [{"field": f"{field}.id", "message": "This field is mandatory and cannot be null."}]),
        ({field: {"id": None}}, [{"field": f"{field}.id", "message": "This field is mandatory and cannot be null."}]),
        ({field: {"id": ""}}, [{"field": f"{field}.id", "message": "This field is mandatory and cannot be blank."}]),
        ({field: {"id": "foo"}}, [{"field": f"{field}.id", "message": "Object does not exist with given id 'foo'."}]),
    ]
    if not nullable:
        parameters.append(
            ({field: None}, [{"field": field, "message": "This field is mandatory and cannot be null."}]),
        )
    return parameters


T = TypeVar("T", bound=NamedTuple)


class ParametrizeArgs(TypedDict):
    argnames: list[str]
    argvalues: list[T]
    ids: list[str]


class InvalidInput(NamedTuple):
    invalid_data: dict[str, Any]
    fields: list[dict[str, str]]


def parametrize_helper(__tests: dict[str, T], /) -> ParametrizeArgs:
    """Construct parametrize input while setting test IDs."""
    assert __tests, "I need some tests, please!"
    values = list(__tests.values())
    try:
        return ParametrizeArgs(
            argnames=list(values[0].__class__.__annotations__),
            argvalues=values,
            ids=list(__tests),
        )
    except Exception as error:  # noqa
        raise RuntimeError("Improper configuration. Did you use a NamedTuple for T?") from error


@contextmanager
def count_queries(expected: int, *, list_queries_on_failure: bool = True, count_audit_log: bool = False):
    orig_debug = settings.DEBUG
    try:
        settings.DEBUG = True
        connection.queries_log.clear()
        yield
        database_queries = [
            query["sql"]
            for query in connection.queries
            if "sql" in query
            and not query["sql"].startswith("SAVEPOINT")
            and not query["sql"].startswith("RELEASE SAVEPOINT")
        ]
        if not count_audit_log:
            database_queries = [
                sql
                for sql in database_queries
                # audit log also tries to fetch django content types for its deletion rules
                if not any(table in sql for table in ["auditlog_logentry", "django_content_type"])
            ]

        number_of_queries = len(database_queries)
        if number_of_queries != expected:
            msg = f"Unexpected database query count, {number_of_queries} instead of {expected}."
            if list_queries_on_failure:
                msg += " Queries:\n"
                for index, query in enumerate(database_queries):
                    msg += (
                        f"{index + 1}) ---------------------------------------------------------------------------\n"
                        f"{sqlparse.format(query, reindent=True)}\n"
                    )
            pytest.fail(msg)
    finally:
        connection.queries_log.clear()
        settings.DEBUG = orig_debug
