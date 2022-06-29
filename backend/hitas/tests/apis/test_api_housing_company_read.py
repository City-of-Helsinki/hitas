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


def assert_about_now(data, path) -> datetime.datetime:
    value = _get_value(data, path, mandatory=True)
    now = datetime.datetime.now(datetime.timezone.utc)
    diff = now - value
    if -1 < diff.total_seconds() < 5:
        return value
    else:
        raise Exception(f"Too big difference. Value: '{value}', now: '{now}', difference: {diff} seconds.")


def _get_value(data, path, mandatory=True):
    current_value = data
    current_path = ""

    for part in path.split("."):
        current_path += part
        if getattr(current_value, "get", None) is None:
            raise Exception(f"Data not not dict for path '{current_path}'.")

        current_value = current_value.get(part)
        if current_value is None:
            if mandatory:
                raise Exception(f"Data not found for path '{path}'.")
            else:
                return None
        current_path += "."

    return current_value


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
        now = assert_about_now(response.data, "last_modified.datetime")
        self.assertDictEqual(
            dict(response.data),
            {
                "acquisition_price": {"initial": 10.00, "realized": None},
                "address": {
                    "street": "test-street-address-1",
                    "postal_code": "00100",
                    "city": "Helsinki",
                },
                "area": {"name": "Helsinki Keskusta - Etu-Töölö", "cost_area": 1},
                "building_type": {
                    "code": "001",
                    "value": "tuntematon",
                    "description": None,
                },
                "business_id": "1234567-8",
                "date": datetime.date(2021, 1, 1),
                "developer": {
                    "code": "000",
                    "value": "Tuntematon",
                    "description": None,
                },
                "financing_method": {
                    "code": "000",
                    "value": "tuntematon",
                    "description": None,
                },
                "id": hc1.uuid.hex,
                "last_modified": {
                    "user": {
                        "first_name": None,
                        "last_name": None,
                        "username": "hitas",
                    },
                    "datetime": now,
                },
                "legacy_id": None,
                "name": {
                    "display": "test-housing-company-1",
                    "official": "test-housing-company-1-as-oy",
                },
                "notes": None,
                "notification_date": None,
                "primary_loan": 10.00,
                "property_manager": {
                    "address": {"city": "Helsinki", "postal_code": "00100", "street": "Fakestreet 123"},
                    "email": "iskonen@example.com",
                    "name": "Isännöitsijä Iskonen Oy",
                },
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
                                "completion_date": "2022-01-01",
                            },
                            # Second building
                            {
                                "address": {
                                    "city": "Helsinki",
                                    "postal_code": "00100",
                                    "street": "test-b-street-address-2",
                                },
                                "building_identifier": None,
                                "completion_date": "2021-01-01",
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
                                "completion_date": "2021-05-01",
                            }
                        ],
                    },
                ],
                "state": "not_ready",
                "sales_price_catalogue_confirmation_date": None,
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
