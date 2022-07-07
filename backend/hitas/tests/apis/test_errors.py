from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from hitas.tests.apis.helpers import validate_openapi


class ExceptionApiCases(APITestCase):
    maxDiff = None

    def test_400_invalid_json(self):
        response = self.client.post(reverse("hitas:housing-company-list"), data="foo", content_type="application/json")

        validate_openapi(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.json(),
            {
                "error": "bad_request",
                "message": "Bad request",
                "reason": "Bad Request",
                "status": 400,
            },
        )

    def test_404(self):
        response = self.client.get("/foo")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(
            response.json(),
            {
                "error": "not_found",
                "message": "Resource not found",
                "reason": "Not Found",
                "status": 404,
            },
        )

    def test_405(self):
        response = self.client.generic("FOO", reverse("hitas:housing-company-list"))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertDictEqual(
            response.json(),
            {
                "error": "method_not_allowed",
                "message": "Method not allowed",
                "reason": "Method Not Allowed",
                "status": 405,
            },
        )

    def test_406(self):
        response = self.client.get(reverse("hitas:housing-company-list"), HTTP_ACCEPT="text/plain")

        validate_openapi(response)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertDictEqual(
            response.json(),
            {
                "error": "not_acceptable",
                "message": "Not acceptable",
                "reason": "Not Acceptable",
                "status": 406,
            },
        )

    def test_415(self):
        response = self.client.post(reverse("hitas:housing-company-list"), data="foo", content_type="text/plain")

        validate_openapi(response)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        self.assertDictEqual(
            response.json(),
            {
                "error": "unsupported_media_type",
                "message": "Unsupported media type",
                "reason": "Unsupported Media Type",
                "status": 415,
            },
        )
