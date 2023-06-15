import pytest
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status

from hitas.models import PropertyManager
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import PropertyManagerFactory

# List tests


@pytest.mark.django_db
def test__api__property_manager__list__empty(api_client: HitasAPIClient):
    url = reverse("hitas:property-manager-list")
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
def test__api__property_manager__list(api_client: HitasAPIClient):
    pm1: PropertyManager = PropertyManagerFactory.create()
    pm2: PropertyManager = PropertyManagerFactory.create()

    url = reverse("hitas:property-manager-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "id": pm1.uuid.hex,
            "name": pm1.name,
            "email": pm1.email,
        },
        {
            "id": pm2.uuid.hex,
            "name": pm2.name,
            "email": pm2.email,
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
def test__api__property_manager__retrieve(api_client: HitasAPIClient):
    pm: PropertyManager = PropertyManagerFactory.create()

    url = reverse("hitas:property-manager-detail", kwargs={"uuid": pm.uuid.hex})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": pm.uuid.hex,
        "name": pm.name,
        "email": pm.email,
    }


@pytest.mark.django_db
def test__api__property_manager__retrieve__invalid_id(api_client: HitasAPIClient):
    PropertyManagerFactory.create()

    url = reverse("hitas:property-manager-detail", kwargs={"uuid": "foo"})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "property_manager_not_found",
        "message": "Property manager not found",
        "reason": "Not Found",
        "status": 404,
    }


# Create tests


@pytest.mark.django_db
def test__api__property_manager__create(api_client: HitasAPIClient):
    data = {
        "name": "Charlie Day",
        "email": "charlie@paddys.com",
    }

    url = reverse("hitas:property-manager-list")
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()

    url = reverse("hitas:property-manager-detail", kwargs={"uuid": PropertyManager.objects.first().uuid.hex})
    get_response = api_client.get(url)
    assert response.json() == get_response.json()


@pytest.mark.django_db
def test__api__property_manager__create__empty_email(api_client: HitasAPIClient):
    data = {
        "name": "Charlie Day",
        "email": "",
    }

    url = reverse("hitas:property-manager-list")
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()


@pytest.mark.parametrize(
    "invalid_data",
    [
        {"name": ""},
        {"email": 123},
        {"email": "foo"},
    ],
)
@pytest.mark.django_db
def test__api__property_manager__create__invalid_data(api_client: HitasAPIClient, invalid_data):
    data = {
        "name": "Frank Reynolds",
        "email": "frank@paddys.com",
    }
    data.update(invalid_data)

    url = reverse("hitas:property-manager-list")
    response = api_client.post(url, data=data, format="json", openapi_validate_request=False)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()


# Update tests


@pytest.mark.django_db
def test__api__property_manager__update(api_client: HitasAPIClient):
    pm: PropertyManager = PropertyManagerFactory.create()
    data = {
        "name": "Ronald McDonald",
        "email": "mac@paddys.com",
    }

    url = reverse("hitas:property-manager-detail", kwargs={"uuid": pm.uuid.hex})
    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": pm.uuid.hex,
        "name": data["name"],
        "email": data["email"],
    }

    get_response = api_client.get(url)
    assert response.json() == get_response.json()


# Delete tests


@pytest.mark.django_db
def test__api__property_manager__delete(api_client: HitasAPIClient):
    pm: PropertyManager = PropertyManagerFactory.create()

    url = reverse("hitas:property-manager-detail", kwargs={"uuid": pm.uuid.hex})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()

    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


# Filter tests


@pytest.mark.parametrize(
    ["selected_filter", "results"],
    [
        [{"name": "TestName"}, 1],
        [{"name": "TestN"}, 1],
        [{"name": "testname"}, 1],
        [{"name": "stNa"}, 1],
        [{"email": "test@email.com"}, 1],
        [{"email": "test@email.fi"}, 1],
        [{"email": "test@email"}, 2],
    ],
)
@pytest.mark.django_db
def test__api__property_manager__filter(api_client: HitasAPIClient, selected_filter, results):
    PropertyManagerFactory.create(name="TestName", email="test@email.com")
    PropertyManagerFactory.create(name="foo", email="test@email.fi")

    url = reverse("hitas:property-manager-list") + "?" + urlencode(selected_filter)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == results, response.json()
