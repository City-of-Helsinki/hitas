from typing import Any

import pytest
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status

from hitas.models import Person
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import PersonFactory

# List tests


@pytest.mark.django_db
def test__api__person__list__empty(api_client: HitasAPIClient):
    url = reverse("hitas:person-list")
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
def test__api__person__list(api_client: HitasAPIClient):
    person1: Person = PersonFactory.create()
    person2: Person = PersonFactory.create()

    url = reverse("hitas:person-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "id": person1.uuid.hex,
            "first_name": person1.first_name,
            "last_name": person1.last_name,
            "social_security_number": person1.social_security_number,
            "email": person1.email,
        },
        {
            "id": person2.uuid.hex,
            "first_name": person2.first_name,
            "last_name": person2.last_name,
            "social_security_number": person2.social_security_number,
            "email": person2.email,
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
def test__api__person__retrieve(api_client: HitasAPIClient):
    person: Person = PersonFactory.create()

    url = reverse("hitas:person-detail", kwargs={"uuid": person.uuid.hex})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": person.uuid.hex,
        "first_name": person.first_name,
        "last_name": person.last_name,
        "social_security_number": person.social_security_number,
        "email": person.email,
    }


@pytest.mark.django_db
def test__api__person__retrieve__invalid_id(api_client: HitasAPIClient):
    PersonFactory.create()

    url = reverse("hitas:person-detail", kwargs={"uuid": "foo"})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


# Create tests


def get_person_create_data() -> dict[str, Any]:
    return {
        "first_name": "fake-first-name",
        "last_name": "fake-last-name",
        "social_security_number": "010199-123Y",
        "email": "test@hitas.com",
    }


@pytest.mark.parametrize("minimal_data", [False, True])
@pytest.mark.django_db
def test__api__person__create(api_client: HitasAPIClient, minimal_data: bool):
    data = get_person_create_data()
    if minimal_data:
        data.update(
            {
                "social_security_number": "",
                "email": "",
            }
        )

    url = reverse("hitas:person-list")
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()

    url = reverse("hitas:person-detail", kwargs={"uuid": Person.objects.first().uuid.hex})
    get_response = api_client.get(url)
    assert response.json() == get_response.json()


@pytest.mark.parametrize(
    "invalid_data",
    [
        {"first_name": ""},
        {"last_name": ""},
        {"email": "foo"},
    ],
)
@pytest.mark.django_db
def test__api__person__create__invalid_data(api_client: HitasAPIClient, invalid_data):
    data = get_person_create_data()
    data.update(invalid_data)

    url = reverse("hitas:person-list")
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()


# Update tests


@pytest.mark.django_db
def test__api__person__update(api_client: HitasAPIClient):
    person: Person = PersonFactory.create()
    data = {
        "first_name": "Matti Matias",
        "last_name": "Meikäläinen",
        "social_security_number": "010199-123Y",
        "email": "test@hitas.com",
    }

    url = reverse("hitas:person-detail", kwargs={"uuid": person.uuid.hex})
    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": person.uuid.hex,
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "social_security_number": data["social_security_number"],
        "email": data["email"],
    }

    get_response = api_client.get(url)
    assert response.json() == get_response.json()


# Delete tests


@pytest.mark.django_db
def test__api__person__delete(api_client: HitasAPIClient):
    person: Person = PersonFactory.create()

    url = reverse("hitas:person-detail", kwargs={"uuid": person.uuid.hex})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()

    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


# Filter tests


@pytest.mark.parametrize(
    "selected_filter",
    [
        {"first_name": "fake-first"},
        {"first_name": "first-name"},
        {"last_name": "fake-last"},
        {"social_security_number": "010199-123Y"},
        {"email": "hitas"},
    ],
)
@pytest.mark.django_db
def test__api__person__filter(api_client: HitasAPIClient, selected_filter):
    data = get_person_create_data()
    PersonFactory.create(first_name=data["first_name"])
    PersonFactory.create(last_name=data["last_name"])
    PersonFactory.create(social_security_number=data["social_security_number"])
    PersonFactory.create(email=data["email"])

    url = reverse("hitas:person-list") + "?" + urlencode(selected_filter)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == 1, response.json()
