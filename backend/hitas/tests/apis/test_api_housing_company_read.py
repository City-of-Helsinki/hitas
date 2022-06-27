import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from hitas.tests.apis.helpers import (
    create_test_building,
    create_test_housing_company,
    create_test_real_estate,
    validate_openapi,
)


class ReadHousingCompanyTests(APITestCase):
    fixtures = ["hitas/tests/apis/testdata.json"]
    maxDiff = None

    def test_read(self):
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
        response = self.client.get(reverse("read-housing-company", args=[hc1.uuid.hex]))

        # Validate response
        validate_openapi(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            dict(response.data),
            {
                "id": hc1.uuid.hex,
                "business_id": "1234567-8",
                "name": {
                    "display": "test-housing-company-1",
                    "official": "test-housing-company-1-as-oy",
                },
                "state": "not_ready",
                "address": {
                    "street": "test-street-address-1",
                    "postal_code": "00100",
                    "city": "Helsinki",
                },
                "area": {"name": "Helsinki Keskusta - Etu-Töölö", "cost_area": 1},
                "date": datetime.date(2021, 1, 1),
                "real_estates": [
                    # First real estate
                    {
                        "address": {"city": "Helsinki", "postal_code": "00100", "street": "test-re-street-address-1"},
                        "property_identifier": "091-020-0015-0003",
                        "buildings": [
                            # First building
                            {
                                "address": {
                                    "city": "Helsinki",
                                    "postal_code": "00100",
                                    "street": "test-b-street-address-1",
                                },
                                "building_identifier": None,
                                "completion_date": datetime.date(2022, 1, 1),
                            },
                            # Second building
                            {
                                "address": {
                                    "city": "Helsinki",
                                    "postal_code": "00100",
                                    "street": "test-b-street-address-2",
                                },
                                "building_identifier": None,
                                "completion_date": datetime.date(2021, 1, 1),
                            },
                        ],
                    },
                    # Second real estate
                    {
                        "address": {"city": "Helsinki", "postal_code": "00100", "street": "test-re-street-address-2"},
                        "property_identifier": "091-020-0015-0003",
                        "buildings": [
                            {
                                "address": {
                                    "city": "Helsinki",
                                    "postal_code": "00100",
                                    "street": "test-b-street-address-3",
                                },
                                "building_identifier": None,
                                "completion_date": datetime.date(2021, 5, 1),
                            }
                        ],
                    },
                ],
            },
        )

    def test_not_found(self):
        self._test_not_found("38432c233a914dfb9c2f54d9f5ad9063")

    def test_not_found_invalid_id(self):
        self._test_not_found("foo")

    def _test_not_found(self, id):
        # Create housing company
        create_test_housing_company(1)

        # Make the request
        response = self.client.get(reverse("read-housing-company", args=[id]))

        # Validate response
        validate_openapi(response)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(
            dict(response.data),
            {
                "error": "housing_company_not_found",
                "message": "Housing company not found",
                "reason": "Not Found",
                "status": 404,
            },
        )
