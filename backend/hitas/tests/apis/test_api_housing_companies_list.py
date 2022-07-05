from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from hitas.tests.apis.helpers import (
    create_test_building,
    create_test_housing_company,
    create_test_real_estate,
    validate_openapi,
)


class ListHousingCompaniesTests(APITestCase):
    fixtures = ["hitas/tests/apis/testdata.json"]
    maxDiff = None

    def test_list_empty(self):
        response = self.client.get(reverse("hitas:housing-company-list"))

        # Validate response
        validate_openapi(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertDictEqual(
            dict(response.data),
            {
                "contents": [],
                "page": {
                    "size": 0,
                    "current_page": 1,
                    "total_items": 0,
                    "total_pages": 1,
                    "links": {
                        "next": None,
                        "previous": None,
                    },
                },
            },
        )

    def test_list(self):
        # Create first housing company
        hc1 = create_test_housing_company(1)
        re1 = create_test_real_estate(hc1, 1)
        create_test_building(re1, 1, "2022-01-01")
        create_test_building(re1, 2, "2021-01-01")
        re2 = create_test_real_estate(hc1, 2)
        create_test_building(re2, 3, "2021-05-01")

        # Create second housing company
        hc2 = create_test_housing_company(2)
        re3 = create_test_real_estate(hc2, 3)
        create_test_building(re3, 4, "2000-01-01")

        # Make the request
        response = self.client.get(reverse("hitas:housing-company-list"))

        # Validate response
        validate_openapi(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            dict(response.data),
            {
                "contents": [
                    {
                        "id": hc1.uuid.hex,
                        "name": "test-housing-company-1",
                        "state": "not_ready",
                        "address": {
                            "street": "test-street-address-1",
                            "postal_code": "00100",
                            "city": "Helsinki",
                        },
                        "area": {"name": "Helsinki Keskusta - Etu-Töölö", "cost_area": 1},
                        "date": "2021-01-01",
                    },
                    {
                        "id": hc2.uuid.hex,
                        "name": "test-housing-company-2",
                        "state": "not_ready",
                        "address": {
                            "street": "test-street-address-2",
                            "postal_code": "00100",
                            "city": "Helsinki",
                        },
                        "area": {"name": "Helsinki Keskusta - Etu-Töölö", "cost_area": 1},
                        "date": "2000-01-01",
                    },
                ],
                "page": {
                    "size": 2,
                    "current_page": 1,
                    "total_items": 2,
                    "total_pages": 1,
                    "links": {
                        "next": None,
                        "previous": None,
                    },
                },
            },
        )

    def test_paging(self):
        for i in range(45):
            create_test_housing_company(i)

        # Make the request
        response = self.client.get(reverse("hitas:housing-company-list"))

        # Validate response
        validate_openapi(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            dict(response.data["page"]),
            {
                "size": 10,
                "current_page": 1,
                "total_items": 45,
                "total_pages": 5,
                "links": {
                    "next": "http://testserver/api/v1/housing-companies?page=2",
                    "previous": None,
                },
            },
        )

        # Make the second page request
        response = self.client.get(reverse("hitas:housing-company-list"), {"page": 2})

        # Validate response
        validate_openapi(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            dict(response.data["page"]),
            {
                "size": 10,
                "current_page": 2,
                "total_items": 45,
                "total_pages": 5,
                "links": {
                    "next": "http://testserver/api/v1/housing-companies?page=3",
                    "previous": "http://testserver/api/v1/housing-companies",
                },
            },
        )

        # Make the last page request
        response = self.client.get(reverse("hitas:housing-company-list"), {"page": 5})

        # Validate response
        validate_openapi(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            dict(response.data["page"]),
            {
                "size": 5,
                "current_page": 5,
                "total_items": 45,
                "total_pages": 5,
                "links": {
                    "next": None,
                    "previous": "http://testserver/api/v1/housing-companies?page=4",
                },
            },
        )

    def test_paging_invalid(self):
        self._test_paging_invalid("a")
        self._test_paging_invalid("#")
        self._test_paging_invalid(" ")
        self._test_paging_invalid("")

    def _test_paging_invalid(self, invalid_value):
        response = self.client.get(reverse("hitas:housing-company-list"), {"page": invalid_value})

        # Validate response
        validate_openapi(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            dict(response.data),
            {
                "status": 400,
                "error": "bad_request",
                "message": "Bad request",
                "reason": "Bad Request",
                "fields": [
                    {
                        "field": "page_number",
                        "message": "Page number must be a positive integer.",
                    },
                ],
            },
        )

    def test_paging_too_high(self):
        response = self.client.get(reverse("hitas:housing-company-list"), {"page": 2})

        # Validate response
        validate_openapi(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            dict(response.data),
            {
                "contents": [],
                "page": {
                    "size": 0,
                    "current_page": 1,
                    "total_items": 0,
                    "total_pages": 1,
                    "links": {
                        "next": None,
                        "previous": None,
                    },
                },
            },
        )
