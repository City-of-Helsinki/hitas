from contextlib import contextmanager
from typing import Any, NamedTuple, TypedDict, TypeVar

import pytest
import sqlparse
import yaml
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.db import connection
from jsonschema_path import SchemaPath
from openapi_core.casting.schemas import oas30_read_schema_casters_factory, oas30_write_schema_casters_factory
from openapi_core.casting.schemas.casters import BooleanCaster
from openapi_core.contrib.django import DjangoOpenAPIRequest, DjangoOpenAPIResponse
from openapi_core.templating.paths.datatypes import PathOperationServer
from openapi_core.unmarshalling.schemas import (
    oas30_read_schema_validators_factory,
    oas30_write_schema_validators_factory,
)
from openapi_core.util import forcebool
from openapi_core.validation.request.protocols import Request
from openapi_core.validation.request.validators import APICallRequestValidator
from openapi_core.validation.response import V30ResponseValidator
from openapi_spec_validator.validation import OpenAPIV30SpecValidator
from rest_framework.response import Response
from rest_framework.test import APIClient

with open(f"{settings.BASE_DIR}/openapi.yaml", "r") as spec_file:
    openapi_spec_data = yaml.safe_load(spec_file)
    OpenAPIV30SpecValidator(openapi_spec_data).validate()
    _openapi_spec = SchemaPath.from_dict(openapi_spec_data)


class BooleanCasterWorkaround(BooleanCaster):
    # After upgrading past openapi-core 0.16.x the boolean validator
    # behavior changes to only allow `'true'` and `'false'`.
    # This workaround returns the old behavior of allowing `'1'`.
    def validate(self, value):
        try:
            value = forcebool(value)
        except ValueError:
            pass
        return super().validate(value)


oas30_read_schema_casters_factory.types_caster.casters["boolean"] = BooleanCasterWorkaround
oas30_write_schema_casters_factory.types_caster.casters["boolean"] = BooleanCasterWorkaround


class DjangoOpenAPIResponseWorkaround(DjangoOpenAPIResponse):
    @property
    def data(self) -> str:
        if self.response.headers.get("content-type") == "application/json":
            return self.response.content.decode("utf-8")
        else:
            return self.response.content


def validate_openapi(
    method: str, request_body: str, response: Response, validate_request: bool = True, validate_response: bool = True
) -> None:
    global _openapi_spec

    if not validate_request and not validate_response:
        return

    # Validate request
    if validate_request:
        is_read = method.lower() == "get"
        if is_read:
            schema_validators_factory = oas30_read_schema_validators_factory
            schema_casters_factory = oas30_read_schema_casters_factory
        else:
            schema_validators_factory = oas30_write_schema_validators_factory
            schema_casters_factory = oas30_write_schema_casters_factory
        RequestValidatorWorkaround(
            _openapi_spec,
            schema_validators_factory=schema_validators_factory,
            schema_casters_factory=schema_casters_factory,
        ).validate(
            WSGIRequestWorkaround(response.wsgi_request, request_body),
        )

    # Validate response
    if validate_response:
        V30ResponseValidator(
            _openapi_spec,
        ).validate(
            DjangoOpenAPIRequest(response.wsgi_request),
            DjangoOpenAPIResponseWorkaround(response),
        )


class RequestValidatorWorkaround(APICallRequestValidator):
    def _find_path(self, request: Request) -> PathOperationServer:
        result = super()._find_path(request)

        # Workaround
        for k, v in result[3].variables.items():
            if k not in request.parameters.path:
                request.parameters.path[k] = v

        return result


class WSGIRequestWorkaround(DjangoOpenAPIRequest):
    """
    Body is only readable once so keep a copy of it for validation purposes. DRF reads it once before us
    """

    def __init__(self, request: WSGIRequest, request_body: str):
        self.request_body = request_body
        super().__init__(request)

    @property
    def body(self) -> bytes:
        return self.request_body


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

        if content_type and content_type.startswith("multipart/form-data"):
            # openapi-core 0.16.6 can not validate multipart/form-data requests
            # and there are issues with upgrading to a newer openapi-core versions.
            # Until the openapi-core can be upgraded, disable request validation for file uploads.
            openapi_validate_request = False

        validate_openapi(
            method,
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
