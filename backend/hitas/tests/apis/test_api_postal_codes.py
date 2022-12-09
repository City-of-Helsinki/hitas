import uuid
from typing import Any, Dict

import pytest
from django.urls import reverse
from rest_framework import status

from hitas.tests import factories
from hitas.tests.apis.helpers import HitasAPIClient

# List tests


@pytest.mark.django_db
def test__api__postal_codes__list__empty(api_client: HitasAPIClient):
    response = api_client.get(reverse("hitas:postal-code-list"))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == []
    assert response.json()["page"] == {
        "size": 0,
        "current_page": 1,
        "total_items": 0,
        "total_pages": 1,
        "links": {
            "next": None,
            "previous": None,
        },
    }


@pytest.mark.django_db
def test__api__postal_code__list(api_client: HitasAPIClient):
    pc1 = factories.HitasPostalCodeFactory.create()
    pc2 = factories.HitasPostalCodeFactory.create()

    response = api_client.get(reverse("hitas:postal-code-list"))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "contents": [
            {
                "id": pc1.uuid.hex,
                "value": pc1.value,
                "city": pc1.city,
                "cost_area": pc1.cost_area,
            },
            {
                "id": pc2.uuid.hex,
                "value": pc2.value,
                "city": pc2.city,
                "cost_area": pc2.cost_area,
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
    }


# Retrieve tests


@pytest.mark.django_db
def test__api__postal_code__retrieve(api_client: HitasAPIClient):
    postal_code = factories.HitasPostalCodeFactory.create()

    response = api_client.get(reverse("hitas:postal-code-detail", kwargs={"uuid": postal_code.uuid.hex}))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": postal_code.uuid.hex,
        "value": postal_code.value,
        "city": postal_code.city,
        "cost_area": postal_code.cost_area,
    }


@pytest.mark.django_db
def test__api__postal_code__retrieve__invalid_id(api_client: HitasAPIClient):
    response = api_client.get(reverse("hitas:postal-code-detail", kwargs={"uuid": "foo"}))
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "postal_code_not_found",
        "message": "Postal code not found",
        "reason": "Not Found",
        "status": 404,
    }


# Create tests


@pytest.mark.django_db
def test__api__postal_code__create(api_client: HitasAPIClient):
    data = {
        "value": "00100",
        "city": "Oulu",
        "cost_area": 2,
    }

    response = api_client.post(reverse("hitas:postal-code-list"), data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert_contains_generated_id(response.json())
    assert response.json() == data


@pytest.mark.parametrize(
    "invalid_data,fields",
    [
        ({"value": None}, [{"field": "value", "message": "This field is mandatory and cannot be null."}]),
        ({"value": ""}, [{"field": "value", "message": "This field is mandatory and cannot be blank."}]),
        ({"city": None}, [{"field": "city", "message": "This field is mandatory and cannot be null."}]),
        ({"city": ""}, [{"field": "city", "message": "This field is mandatory and cannot be blank."}]),
        ({"cost_area": None}, [{"field": "cost_area", "message": "This field is mandatory and cannot be null."}]),
        ({"cost_area": "foo"}, [{"field": "cost_area", "message": "A valid integer is required."}]),
        ({"cost_area": -1}, [{"field": "cost_area", "message": "Ensure this value is greater than or equal to 1."}]),
        ({"cost_area": 0}, [{"field": "cost_area", "message": "Ensure this value is greater than or equal to 1."}]),
        ({"cost_area": 5}, [{"field": "cost_area", "message": "Ensure this value is less than or equal to 4."}]),
    ],
)
@pytest.mark.django_db
def test__api__postal_code__create__invalid_data(api_client: HitasAPIClient, invalid_data, fields):
    data = {
        "value": "00100",
        "city": "Oulu",
        "cost_area": 2,
    }
    data.update(invalid_data)

    response = api_client.post(
        reverse("hitas:postal-code-list"), data=data, format="json", openapi_validate_request=False
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": fields,
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


# Update tests


@pytest.mark.django_db
def test__api__postal_code__update(api_client: HitasAPIClient):
    existing = factories.HitasPostalCodeFactory.create()
    data = {
        "value": "00100",
        "city": "Oulu",
        "cost_area": 2,
    }

    response = api_client.put(
        reverse("hitas:postal-code-detail", kwargs={"uuid": existing.uuid.hex}), data=data, format="json"
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": existing.uuid.hex,
        "value": data["value"],
        "city": data["city"],
        "cost_area": data["cost_area"],
    }


# Delete tests


@pytest.mark.django_db
def test__api__postal_code__delete(api_client: HitasAPIClient):
    existing = factories.HitasPostalCodeFactory.create()

    response = api_client.delete(reverse("hitas:postal-code-detail", kwargs={"uuid": existing.uuid.hex}))
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()


# Helpers


def assert_contains_generated_id(d: Dict[str, Any]) -> None:
    assert d.get("id") is not None, "id missing"

    try:
        uuid.UUID(hex=d["id"])
    except ValueError:
        pytest.fail(f"Generated id is in wrong format! ('{d['id']}')")

    del d["id"]
