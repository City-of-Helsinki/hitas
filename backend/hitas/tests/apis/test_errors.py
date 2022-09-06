import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from hitas.tests.factories.user import UserFactory


class ExceptionApiCases(APITestCase):
    maxDiff = None

    @pytest.fixture(autouse=True)
    def setup_user(self, db):
        self.user = UserFactory.create()

    def __init__(self, methodName="runTest"):
        super().__init__(methodName=methodName)

    def test__api__exception__401__missing_token(self):
        response = self.client.get(reverse("hitas:housing-company-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertDictEqual(
            response.json(),
            {
                "error": "unauthorized",
                "message": "The request requires an authentication",
                "reason": "Unauthorized",
                "status": 401,
            },
        )

    def test__api__exception__401__invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer foo")
        response = self.client.get(reverse("hitas:housing-company-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertDictEqual(
            response.json(),
            {
                "error": "unauthorized",
                "message": "The request contained an invalid authentication token",
                "reason": "Unauthorized",
                "status": 401,
            },
        )

    def test__api__exception__400_bad_request__invalid_json(self):
        self.client.force_authenticate(self.user)
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
        self.client.force_authenticate(self.user)
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
        self.client.force_authenticate(self.user)
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

    def test__api__exception__415_unsupported_media_type__plain_text(self):
        self.client.force_authenticate(self.user)
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

    def test__api__exception__415_unsupported_media_type__form_data(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("hitas:housing-company-list"), data="foo", content_type="multipart/form-data"
        )
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

    def test__api__exception__415_unsupported_media_type__form_urlencoded(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("hitas:housing-company-list"), data={"foo": "bar"}, content_type="application/x-www-form-urlencoded"
        )
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
