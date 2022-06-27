from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exc_handler
from rest_framework.views import set_rollback


def exception_handler(exc, context):
    if isinstance(exc, HitasException):
        set_rollback()
        return Response(exc.data, status=exc.status_code)
    else:
        return drf_exc_handler(exc, context)


class HitasException(Exception):
    pass


class HousingCompanyNotFound(HitasException):
    def __init__(self):
        self.status_code = 404

        self.data = {
            "status": 404,
            "reason": "Not Found",
            "message": "Housing company not found",
            "error": "housing_company_not_found",
        }


class InvalidPage(HitasException):
    def __init__(self):
        self.status_code = 400

        self.data = {
            "status": 400,
            "reason": "Bad Request",
            "message": "Bad request",
            "error": "bad_request",
            "fields": [{"field": "page_number", "message": "Page number must be a positive integer."}],
        }
