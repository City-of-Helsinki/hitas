from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class ExceptionApiCases(APITestCase):
    maxDiff = None

    def test__api__exception__400_bad_request__invalid_json(self):
        response = self.client.post(reverse("hitas:housing-company-list"), data="foo", content_type="application/json")
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

    def test__api__exception__404_not_found(self):
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

    def test__api__exception__405_method_not_allowed(self):
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

    def test__api__exception__406_not_acceptable(self):
        response = self.client.get(reverse("hitas:housing-company-list"), HTTP_ACCEPT="text/plain")
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

    def test__api__exception__415_unsupported_media_type(self):
        response = self.client.post(reverse("hitas:housing-company-list"), data="foo", content_type="text/plain")
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
