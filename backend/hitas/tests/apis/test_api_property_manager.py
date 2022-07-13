import pytest
from django.urls import reverse
from rest_framework import status

from hitas.models import PostalCode, PropertyManager
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import PostalCodeFactory, PropertyManagerFactory

# List tests


@pytest.mark.django_db
def test__api__property_manager__list__empty(api_client: HitasAPIClient):
    url = reverse("hitas:property-manager-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
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
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["contents"] == [
        {
            "id": pm1.uuid.hex,
            "address": {
                "city": "Helsinki",
                "postal_code": pm1.postal_code.value,
                "street": pm1.street_address,
            },
            "name": pm1.name,
            "email": pm1.email,
        },
        {
            "id": pm2.uuid.hex,
            "address": {
                "city": "Helsinki",
                "postal_code": pm2.postal_code.value,
                "street": pm2.street_address,
            },
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
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": pm.uuid.hex,
        "address": {
            "city": "Helsinki",
            "postal_code": pm.postal_code.value,
            "street": pm.street_address,
        },
        "name": pm.name,
        "email": pm.email,
    }


@pytest.mark.django_db
def test__api__property_manager__retrieve__invalid_id(api_client: HitasAPIClient):
    PropertyManagerFactory.create()

    url = reverse("hitas:property-manager-detail", kwargs={"uuid": "foo"})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


# Create tests


@pytest.mark.django_db
def test__api__property_manager__create(api_client: HitasAPIClient):
    pc: PostalCode = PostalCodeFactory.create()

    data = {
        "address": {
            "postal_code": pc.value,
            "street": "test-street-address-1",
        },
        "name": "Charlie Day",
        "email": "charlie@paddys.com",
    }

    url = reverse("hitas:property-manager-list")
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    url = reverse("hitas:property-manager-detail", kwargs={"uuid": PropertyManager.objects.first().uuid.hex})
    get_response = api_client.get(url)
    assert response.json() == get_response.json()


@pytest.mark.parametrize(
    "invalid_data",
    [
        {"address": {"postal_code": "00100", "street": ""}},
        {"name": ""},
        {"email": ""},
        {"email": 123},
        {"email": "foo"},
    ],
)
@pytest.mark.django_db
def test__api__property_manager__create__invalid_data(api_client: HitasAPIClient, invalid_data):
    pc: PostalCode = PostalCodeFactory.create(value="00100")
    data = {
        "address": {
            "postal_code": pc.value,
            "street": "test-street-address-1",
        },
        "name": "Frank Reynolds",
        "email": "frank@paddys.com",
    }
    data.update(invalid_data)

    url = reverse("hitas:property-manager-list")
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()


# Update tests


@pytest.mark.django_db
def test__api__property_manager__update(api_client: HitasAPIClient):
    pm: PropertyManager = PropertyManagerFactory.create()
    data = {
        "address": {
            "postal_code": pm.postal_code.value,
            "street": "test-street-address-1",
        },
        "name": "Ronald McDonald",
        "email": "mac@paddys.com",
    }

    url = reverse("hitas:property-manager-detail", kwargs={"uuid": pm.uuid.hex})
    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": pm.uuid.hex,
        "address": {
            "city": "Helsinki",
            "postal_code": data["address"]["postal_code"],
            "street": data["address"]["street"],
        },
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
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
