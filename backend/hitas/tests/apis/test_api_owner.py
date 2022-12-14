from typing import Any

import pytest
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status

from hitas.models import Owner
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import OwnerFactory, OwnershipFactory

# List tests


@pytest.mark.django_db
def test__api__owner__list__empty(api_client: HitasAPIClient):
    url = reverse("hitas:owner-list")
    response = api_client.get(url)
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
def test__api__owner__list(api_client: HitasAPIClient):
    owner1: Owner = OwnerFactory.create()
    owner2: Owner = OwnerFactory.create()

    url = reverse("hitas:owner-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "id": owner1.uuid.hex,
            "name": owner1.name,
            "identifier": owner1.identifier,
            "email": owner1.email,
        },
        {
            "id": owner2.uuid.hex,
            "name": owner2.name,
            "identifier": owner2.identifier,
            "email": owner2.email,
        },
    ]
    assert response.json()["page"] == {
        "size": 2,
        "current_page": 1,
        "total_items": 2,
        "total_pages": 1,
        "links": {
            "next": None,
            "previous": None,
        },
    }


# Retrieve tests


@pytest.mark.django_db
def test__api__owner__retrieve(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()

    url = reverse("hitas:owner-detail", kwargs={"uuid": owner.uuid.hex})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": owner.uuid.hex,
        "name": owner.name,
        "identifier": owner.identifier,
        "email": owner.email,
    }


@pytest.mark.django_db
def test__api__owner__retrieve__invalid_id(api_client: HitasAPIClient):
    OwnerFactory.create()

    url = reverse("hitas:owner-detail", kwargs={"uuid": "foo"})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert {
        "error": "owner_not_found",
        "message": "Owner not found",
        "reason": "Not Found",
        "status": 404,
    } == response.json()


# Create tests


def get_owner_create_data() -> dict[str, Any]:
    return {
        "name": "fake-first-name fake-last-name",
        "identifier": "010199-123Y",
        "email": "hitas@example.com",
    }


@pytest.mark.parametrize("minimal_data", [False, True])
@pytest.mark.django_db
def test__api__owner__create(api_client: HitasAPIClient, minimal_data: bool):
    data = get_owner_create_data()
    if minimal_data:
        data.update(
            {
                "identifier": "",
                "email": "",
            }
        )

    url = reverse("hitas:owner-list")
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()

    url = reverse("hitas:owner-detail", kwargs={"uuid": Owner.objects.first().uuid.hex})
    get_response = api_client.get(url)
    assert response.json() == get_response.json()


@pytest.mark.parametrize(
    "invalid_data,field",
    [
        ({"email": "foo"}, {"field": "email", "message": "Enter a valid email address."}),
    ],
)
@pytest.mark.django_db
def test__api__owner__create__invalid_data(api_client: HitasAPIClient, invalid_data, field):
    data = get_owner_create_data()
    data.update(invalid_data)

    url = reverse("hitas:owner-list")
    response = api_client.post(url, data=data, format="json", openapi_validate_request=False)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert {
        "error": "bad_request",
        "fields": [field],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    } == response.json()


# Update tests


@pytest.mark.django_db
def test__api__owner__update(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    data = {
        "name": "Matti Meikäläinen",
        "identifier": "010199-123Y",
        "email": "test@example.com",
    }

    url = reverse("hitas:owner-detail", kwargs={"uuid": owner.uuid.hex})
    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": owner.uuid.hex,
        "name": data["name"],
        "identifier": data["identifier"],
        "email": data["email"],
    }

    get_response = api_client.get(url)
    assert response.json() == get_response.json()


# Delete tests


@pytest.mark.django_db
def test__api__owner__delete(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()

    url = reverse("hitas:owner-detail", kwargs={"uuid": owner.uuid.hex})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()

    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


@pytest.mark.django_db
def test__api__owner__delete__active_ownerships(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    OwnershipFactory.create(owner=owner)

    url = reverse("hitas:owner-detail", kwargs={"uuid": owner.uuid.hex})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert {
        "error": "owner_in_use",
        "message": "Owner has active ownerships and cannot be removed.",
        "reason": "Conflict",
        "status": 409,
    } == response.json()


# Filter tests


@pytest.mark.parametrize(
    "selected_filter",
    [
        {"name": "fake-first"},
        {"name": "first-name"},
        {"name": "fake-last"},
        {"identifier": "010199-123Y"},
        {"identifier": "010199-123y"},
        {"email": "hitas@example.com"},
        {"email": "HITAS@EXAMPLE.com"},
    ],
)
@pytest.mark.django_db
def test__api__owner__filter(api_client: HitasAPIClient, selected_filter):
    data = get_owner_create_data()
    OwnerFactory.create(name=data["name"])
    OwnerFactory.create(identifier=data["identifier"])
    OwnerFactory.create(email=data["email"])

    url = reverse("hitas:owner-list") + "?" + urlencode(selected_filter)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == 1, response.json()
