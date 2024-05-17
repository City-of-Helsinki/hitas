from typing import Any

import pytest
from auditlog.models import LogEntry
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status

from hitas.models import Owner
from hitas.models.utils import deobfuscate
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
    non_disclosure_owner = OwnerFactory.create(non_disclosure=True)
    deobfuscate(non_disclosure_owner)
    url = reverse("hitas:owner-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "id": owner1.uuid.hex,
            "name": owner1.name,
            "identifier": owner1.identifier,
            "email": owner1.email,
            "non_disclosure": owner1.non_disclosure,
        },
        {
            "id": owner2.uuid.hex,
            "name": owner2.name,
            "identifier": owner2.identifier,
            "email": owner2.email,
            "non_disclosure": owner2.non_disclosure,
        },
        {
            "id": non_disclosure_owner.uuid.hex,
            "name": non_disclosure_owner.name,
            "identifier": non_disclosure_owner.identifier,
            "email": non_disclosure_owner.email,
            "non_disclosure": non_disclosure_owner.non_disclosure,
        },
    ]
    assert response.json()["page"] == {
        "size": 3,
        "current_page": 1,
        "total_items": 3,
        "total_pages": 1,
        "links": {
            "next": None,
            "previous": None,
        },
    }


# Retrieve tests


@pytest.mark.django_db
@pytest.mark.parametrize("non_disclosure", [False, True])
def test__api__owner__retrieve(api_client: HitasAPIClient, non_disclosure):
    owner: Owner = OwnerFactory.create(non_disclosure=non_disclosure)
    deobfuscate(owner)
    url = reverse("hitas:owner-detail", kwargs={"uuid": owner.uuid.hex})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": owner.uuid.hex,
        "name": owner.name,
        "identifier": owner.identifier,
        "email": owner.email,
        "non_disclosure": owner.non_disclosure,
    }


@pytest.mark.django_db
def test__api__owner__retrieve__invalid_id(api_client: HitasAPIClient):
    OwnerFactory.create()

    url = reverse("hitas:owner-detail", kwargs={"uuid": "foo"})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert {
        "error": "non_obfuscated_owner_not_found",
        "message": "non obfuscated owner not found",
        "reason": "Not Found",
        "status": 404,
    } == response.json()


# Create tests


def get_owner_create_data() -> dict[str, Any]:
    return {
        "name": "fake-first-name fake-last-name",
        "identifier": "010199-123Y",
        "email": "hitas@example.com",
        "non_disclosure": False,
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


@pytest.mark.django_db
def test__api__owner__create__existing_valid_identifier(api_client: HitasAPIClient):
    data = get_owner_create_data()
    OwnerFactory.create(identifier=data["identifier"])

    url = reverse("hitas:owner-list")
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert {
        "error": "bad_request",
        "fields": [
            {
                "field": "identifier",
                "message": "An owner with this identifier already exists.",
            }
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    } == response.json()


@pytest.mark.django_db
def test__api__owner__create__existing_invalid_identifier(api_client: HitasAPIClient):
    data = get_owner_create_data()
    data["identifier"] = "foo"
    owner: Owner = OwnerFactory.create(identifier=data["identifier"])

    url = reverse("hitas:owner-list")
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()

    url = reverse("hitas:owner-detail", kwargs={"uuid": Owner.objects.exclude(id=owner.id).first().uuid.hex})
    get_response = api_client.get(url)
    assert response.json() == get_response.json()


@pytest.mark.django_db
def test__api__owner__create__null_identifier(api_client: HitasAPIClient):
    data = get_owner_create_data()
    data["identifier"] = None
    owner: Owner = OwnerFactory.create(identifier=data["identifier"])

    url = reverse("hitas:owner-list")
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()

    url = reverse("hitas:owner-detail", kwargs={"uuid": Owner.objects.exclude(id=owner.id).first().uuid.hex})
    get_response = api_client.get(url)
    assert response.json() == get_response.json()


# Update tests


@pytest.mark.django_db
def test__api__owner__update(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    data = {
        "name": "Matti Meikäläinen",
        "identifier": "010199-123Y",
        "email": "test@example.com",
        "non_disclosure": False,
    }

    url = reverse("hitas:owner-detail", kwargs={"uuid": owner.uuid.hex})
    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": owner.uuid.hex,
        "name": data["name"],
        "identifier": data["identifier"],
        "email": data["email"],
        "non_disclosure": data["non_disclosure"],
    }

    get_response = api_client.get(url)
    assert response.json() == get_response.json()


@pytest.mark.django_db
def test__api__owner__update__valid_identifier_to_invalid(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    data = {
        "name": "Matti Meikäläinen",
        "identifier": "foo",
        "email": "test@example.com",
        "non_disclosure": False,
    }

    url = reverse("hitas:owner-detail", kwargs={"uuid": owner.uuid.hex})
    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert {
        "error": "bad_request",
        "fields": [
            {
                "field": "identifier",
                "message": "Previous identifier was valid. Cannot update to an invalid one.",
            }
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    } == response.json()


@pytest.mark.django_db
def test__api__owner__update__valid_identifier_to_null(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    data = {
        "name": "Matti Meikäläinen",
        "identifier": None,
        "email": "test@example.com",
        "non_disclosure": False,
    }

    url = reverse("hitas:owner-detail", kwargs={"uuid": owner.uuid.hex})
    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert {
        "error": "bad_request",
        "fields": [
            {
                "field": "identifier",
                "message": "Previous identifier was valid. Cannot update to an invalid one.",
            }
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    } == response.json()


@pytest.mark.django_db
def test__api__owner__update__valid_identifier_to_self(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    data = {
        "name": "Matti Meikäläinen",
        "identifier": owner.identifier,
        "email": "test@example.com",
        "non_disclosure": False,
    }

    url = reverse("hitas:owner-detail", kwargs={"uuid": owner.uuid.hex})
    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert {
        "id": owner.uuid.hex,
        "name": data["name"],
        "identifier": data["identifier"],
        "email": data["email"],
        "non_disclosure": data["non_disclosure"],
    } == response.json()


@pytest.mark.django_db
def test__api__owner__update__valid_identifier_to_existing_valid(api_client: HitasAPIClient):
    owner_1: Owner = OwnerFactory.create(identifier="190782-599C")
    owner_2: Owner = OwnerFactory.create(identifier="220213A364W")
    data = {
        "name": "Matti Meikäläinen",
        "identifier": owner_2.identifier,
        "email": "test@example.com",
        "non_disclosure": False,
    }

    url = reverse("hitas:owner-detail", kwargs={"uuid": owner_1.uuid.hex})
    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert {
        "error": "bad_request",
        "fields": [
            {
                "field": "identifier",
                "message": "An owner with this identifier already exists.",
            }
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    } == response.json()


@pytest.mark.django_db
def test__api__owner__update__invalid_identifier_to_invalid(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create(identifier="foo")
    data = {
        "name": "Matti Meikäläinen",
        "identifier": "foobar",
        "email": "test@example.com",
        "non_disclosure": False,
    }

    url = reverse("hitas:owner-detail", kwargs={"uuid": owner.uuid.hex})
    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": owner.uuid.hex,
        "name": data["name"],
        "identifier": data["identifier"],
        "email": data["email"],
        "non_disclosure": data["non_disclosure"],
    }


@pytest.mark.django_db
def test__api__owner__update__invalid_identifier_to_null(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create(identifier="foo")
    data = {
        "name": "Matti Meikäläinen",
        "identifier": None,
        "email": "test@example.com",
        "non_disclosure": False,
    }

    url = reverse("hitas:owner-detail", kwargs={"uuid": owner.uuid.hex})
    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": owner.uuid.hex,
        "name": data["name"],
        "identifier": data["identifier"],
        "email": data["email"],
        "non_disclosure": data["non_disclosure"],
    }


@pytest.mark.django_db
def test__api__owner__update__invalid_identifier_to_self(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create(identifier="foo")
    data = {
        "name": "Matti Meikäläinen",
        "identifier": owner.identifier,
        "email": "test@example.com",
        "non_disclosure": False,
    }

    url = reverse("hitas:owner-detail", kwargs={"uuid": owner.uuid.hex})
    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert {
        "id": owner.uuid.hex,
        "name": data["name"],
        "identifier": data["identifier"],
        "email": data["email"],
        "non_disclosure": data["non_disclosure"],
    } == response.json()


@pytest.mark.django_db
def test__api__owner__update__invalid_identifier_to_existing_invalid(api_client: HitasAPIClient):
    owner_1: Owner = OwnerFactory.create(identifier="foo")
    owner_2: Owner = OwnerFactory.create(identifier="bar")
    data = {
        "name": "Matti Meikäläinen",
        "identifier": owner_2.identifier,
        "email": "test@example.com",
        "non_disclosure": False,
    }

    url = reverse("hitas:owner-detail", kwargs={"uuid": owner_1.uuid.hex})
    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert {
        "id": owner_1.uuid.hex,
        "name": data["name"],
        "identifier": data["identifier"],
        "email": data["email"],
        "non_disclosure": data["non_disclosure"],
    } == response.json()


@pytest.mark.django_db
def test__api__owner__update__to_non_disclosure(api_client: HitasAPIClient):
    # Owner not under non-disclosure
    owner: Owner = OwnerFactory.create(
        name="Matti Meikäläinen",
        identifier="010199-123Y",
        email="test@example.com",
        bypass_conditions_of_sale=False,
        non_disclosure=False,
    )

    data = {
        "name": "Matti Meikäläinen",
        "identifier": "010199-123Y",
        "email": "test@example.com",
        "non_disclosure": True,
    }

    url = reverse("hitas:owner-detail", kwargs={"uuid": owner.uuid.hex})
    response = api_client.put(url, data=data, format="json")

    # owners api already provides non-obfuscated version of the user
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": owner.uuid.hex,
        "name": owner.name,
        "identifier": owner.identifier,
        "email": owner.email,
        "non_disclosure": True,
    }


@pytest.mark.django_db
def test__api__owner__update__change_fields_while_under_non_disclosure(api_client: HitasAPIClient):
    # Owner not under non-disclosure
    owner: Owner = OwnerFactory.create(
        name="Matti Meikäläinen",
        identifier="010199-123Y",
        email="test@example.com",
        bypass_conditions_of_sale=False,
        non_disclosure=True,
    )

    # Owner is obfuscated
    assert owner.name == ""
    assert owner.identifier is None
    assert owner.email is None
    assert owner.non_disclosure is True

    # Not obfuscated in the API
    url = reverse("hitas:owner-detail", kwargs={"uuid": owner.uuid.hex})
    response = api_client.get(url)
    assert response.json() == {
        "id": owner.uuid.hex,
        "name": "Matti Meikäläinen",
        "identifier": "010199-123Y",
        "email": "test@example.com",
        "non_disclosure": True,
    }

    # Try to update the owner while obfuscated
    data = {
        "name": "Matti Muukalainen",  # name changed
        # Can use obfuscated values here, since they are not changed
        # due to how 'hitas.models.utils.deobfuscate' works (it does not
        # allow changing owner values to their obfuscated values to the database)
        "identifier": "010199-123Y",
        "email": None,  # email changed to None
        "non_disclosure": True,
    }

    url = reverse("hitas:owner-detail", kwargs={"uuid": owner.uuid.hex})
    response = api_client.put(url, data=data, format="json")

    # Get updated non-obfuscated values back
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": owner.uuid.hex,
        "name": "Matti Muukalainen",
        "identifier": "010199-123Y",
        "email": None,
        "non_disclosure": True,
    }

    # Owner fetched via query is still obfuscated
    # (needs to be re-fetched so that '_unobfuscated_data' is populated again).
    owner = Owner.objects.get(uuid=owner.uuid)
    assert owner.name == ""
    assert owner.identifier is None
    assert owner.email is None
    assert owner.non_disclosure is True

    # New owner data is in the database
    deobfuscate(owner)
    assert owner.name == "Matti Muukalainen"  # name changed
    assert owner.email is None  # email changed
    # not changed
    assert owner.identifier == "010199-123Y"
    assert owner.non_disclosure is True


@pytest.mark.django_db
def test__api__owner__update__remove_non_disclosure(api_client: HitasAPIClient):
    # Owner under non-disclosure
    owner: Owner = OwnerFactory.create(
        name="Matti Meikäläinen",
        identifier="010199-123Y",
        email="test@example.com",
        bypass_conditions_of_sale=False,
        non_disclosure=True,
    )

    # Owner from database is obfuscated
    assert owner.name == ""
    assert owner.identifier is None
    assert owner.email is None
    assert owner.non_disclosure is True

    # Not obfuscated in the API
    url = reverse("hitas:owner-detail", kwargs={"uuid": owner.uuid.hex})
    response = api_client.get(url)
    assert response.json() == {
        "id": owner.uuid.hex,
        "name": "Matti Meikäläinen",
        "identifier": "010199-123Y",
        "email": "test@example.com",
        "non_disclosure": True,
    }

    # When non-disclosure is removed, the owner data is restored
    # This can be done with PUT using the obfuscated values, since
    # 'hitas.models.utils.deobfuscate' does not allow changing the
    # obfuscated fields to the values in the obfusation rules
    # (while the owner is obfuscated).
    data = {
        "name": "Matti Meikäläinen",
        "identifier": "010199-123Y",
        "email": "test@example.com",
        "non_disclosure": False,
    }

    response = api_client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": owner.uuid.hex,
        "name": "Matti Meikäläinen",
        "identifier": "010199-123Y",
        "email": "test@example.com",
        "non_disclosure": False,
    }


@pytest.mark.parametrize(
    ["should_use_second_owner_details", "expected_name", "expected_identifier", "expected_email"],
    [
        [False, "Name 1", "123-ID", "name1@mail.test"],
        [True, "Name 2", "456-ID", "name2@mail.test"],
    ],
)
@pytest.mark.django_db
def test__api__owner__merge(
    api_client: HitasAPIClient, should_use_second_owner_details, expected_name, expected_identifier, expected_email
):
    owner_1: Owner = OwnerFactory.create(name="Name 1", identifier="123-ID", email="name1@mail.test")
    owner_2: Owner = OwnerFactory.create(name="Name 2", identifier="456-ID", email="name2@mail.test")
    OwnershipFactory.create(owner=owner_1)
    OwnershipFactory.create(owner=owner_2)

    data = {
        "first_owner_id": owner_1.uuid.hex,
        "second_owner_id": owner_2.uuid.hex,
        "should_use_second_owner_name": should_use_second_owner_details,
        "should_use_second_owner_identifier": should_use_second_owner_details,
        "should_use_second_owner_email": should_use_second_owner_details,
    }

    url = reverse("hitas:owner-merge")
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()

    assert Owner.objects.count() == 1
    assert Owner.objects.first().ownerships.count() == 2

    owner_1 = Owner.objects.first()
    assert owner_1.name == expected_name
    assert owner_1.identifier == expected_identifier
    assert owner_1.email == expected_email


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


# Obfuscated owner endpoint tests


@pytest.mark.django_db
@pytest.mark.parametrize("non_disclosure", [True, False])
def test__api__deobfuscated_owner__retrieve(api_client: HitasAPIClient, non_disclosure):
    owner: Owner = OwnerFactory.create(
        name="Testi Testinen",
        identifier="123456-789A",
        email="testi.testinen.fi",
        non_disclosure=non_disclosure,
    )

    url = reverse("hitas:owner-deobfuscated-detail", kwargs={"uuid": owner.uuid.hex})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": owner.uuid.hex,
        "name": "Testi Testinen",
        "identifier": "123456-789A",
        "email": "testi.testinen.fi",
        "non_disclosure": non_disclosure,
    }

    audit_logs: list[LogEntry] = list(LogEntry.objects.filter(action=LogEntry.Action.ACCESS))
    assert len(audit_logs) == (1 if non_disclosure else 0)
