from typing import Any, Dict, List, Union

from django.http.response import JsonResponse
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import exception_handler as drf_exc_handler
from rest_framework.views import set_rollback


def exception_handler(exc, context):
    if isinstance(exc, HitasException):
        set_rollback()
        return exc.to_response()
    else:
        if isinstance(exc, exceptions.ValidationError):
            fields = []

            for field_name, error in exc.get_full_details().items():
                fields.extend(_convert_fields(field_name, error))

            return BadRequestException(fields).to_response()

        if isinstance(exc, exceptions.MethodNotAllowed):
            return MethodNotAllowed().to_response()

        if isinstance(exc, exceptions.UnsupportedMediaType):
            return UnsupportedMediaType().to_response()

        if isinstance(exc, exceptions.NotAcceptable):
            return NotAcceptable().to_response()

        if isinstance(exc, exceptions.ParseError):
            return BadRequestException().to_response()

        return drf_exc_handler(exc, context)


class HitasException(Exception):
    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data

    def to_response(self) -> Response:
        return Response(self.data, status=self.status_code)


class GenericNotFound(JsonResponse):
    def __init__(self):
        super().__init__(
            status=404,
            data={
                "status": 404,
                "reason": "Not Found",
                "message": "Resource not found",
                "error": "not_found",
            },
        )


class InternalServerError(JsonResponse):
    def __init__(self):
        super().__init__(
            status=500,
            data={
                "status": 500,
                "reason": "Internal Server Error",
                "message": "Internal server error. Please try again.",
                "error": "internal_server_error",
            },
        )


class UnsupportedMediaType(HitasException):
    def __init__(self):
        super().__init__(
            status_code=415,
            data={
                "status": 415,
                "reason": "Unsupported Media Type",
                "message": "Unsupported media type",
                "error": "unsupported_media_type",
            },
        )


class NotAcceptable(HitasException):
    def __init__(self):
        super().__init__(
            status_code=406,
            data={
                "status": 406,
                "reason": "Not Acceptable",
                "message": "Not acceptable",
                "error": "not_acceptable",
            },
        )


class MethodNotAllowed(HitasException):
    def __init__(self):
        super().__init__(
            status_code=405,
            data={
                "status": 405,
                "reason": "Method Not Allowed",
                "message": "Method not allowed",
                "error": "method_not_allowed",
            },
        )


class BadRequestException(HitasException):
    def __init__(self, fields=None):
        super().__init__(
            status_code=400,
            data={
                "status": 400,
                "reason": "Bad Request",
                "message": "Bad request",
                "error": "bad_request",
            },
        )

        if fields is not None:
            self.data["fields"] = fields


class HitasModelNotFound(HitasException):
    def __init__(self, model=None):
        if model is None:
            verbose_name = "Object"
        else:
            verbose_name = model._meta.verbose_name

        super().__init__(
            status_code=404,
            data={
                "status": 404,
                "reason": "Not Found",
                "message": f"{verbose_name} not found",
                "error": f"{verbose_name.lower().replace(' ','_')}_not_found",
            },
        )


class InvalidPage(HitasException):
    def __init__(self):
        super().__init__(
            status_code=400,
            data={
                "status": 400,
                "reason": "Bad Request",
                "message": "Bad request",
                "error": "bad_request",
                "fields": [{"field": "page_number", "message": "Page number must be a positive integer."}],
            },
        )


def _convert_fields(field_name: str, error: Union[Dict[str, Any], List[Dict[str, Any]]]):
    if isinstance(error, list):
        return _convert_field_errors(field_name, error)
    elif isinstance(error, dict):
        retval = []

        for subfield_name, suberror in error.items():
            if subfield_name == api_settings.NON_FIELD_ERRORS_KEY:
                retval.extend(_convert_field_errors(field_name, suberror))
            else:
                retval.extend(_convert_fields(f"{field_name}.{subfield_name}", suberror))

        return retval


def _convert_field_errors(field_name: str, errors: List[Dict[str, Any]]):
    retval = []

    for error in errors:
        # Skip empty values, which may happen in certain cases when using nested serializers
        if not error:
            continue

        formatted_field_name = field_name
        # Handle nested serializer field errors where error message be in a nested dict
        if "code" not in error:
            nested_field_name = next(iter(error))
            formatted_field_name = f"{field_name}.{nested_field_name}"
            error = error[nested_field_name][0]

        if error["code"] in ["required", "null", "blank"]:
            retval.append({"field": formatted_field_name, "message": "This field is mandatory and cannot be blank."})
        elif error["code"] in ["invalid", "invalid_choice", "min_value", "max_value"]:
            retval.append({"field": formatted_field_name, "message": error["message"]})
        else:
            raise Exception(f"Unhandled error code '{error['code']}'.")

    return retval
