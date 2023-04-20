import json
import uuid
from base64 import urlsafe_b64encode

import pytest
from django.urls import reverse
from rest_framework import status
from social_django.models import UserSocialAuth

from hitas.tests.apis.helpers import HitasAPIClient


@pytest.mark.django_db
def test__api__userinfo__email_only(api_client: HitasAPIClient):
    user = api_client.handler._force_user

    data = {"email": "user@example.com"}
    raw_token = urlsafe_b64encode(json.dumps(data).encode()).decode().replace("=", "")

    UserSocialAuth.objects.create(
        user=user,
        provider="tunnistamo",
        uid=str(uuid.uuid4()),
        extra_data={"id_token": ".".join(["foo", raw_token, "bar"])},
    )

    response = api_client.get(reverse("userinfo"))

    assert response.status_code == status.HTTP_200_OK, response.json()

    assert response.json() == {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": data["email"],
    }


@pytest.mark.django_db
def test__api__userinfo__name_found(api_client: HitasAPIClient):
    user = api_client.handler._force_user

    data = {
        "given_name": "foo",
        "family_name": "bar",
        "email": "user@example.com",
    }
    raw_token = urlsafe_b64encode(json.dumps(data).encode()).decode().replace("=", "")

    UserSocialAuth.objects.create(
        user=user,
        provider="tunnistamo",
        uid=str(uuid.uuid4()),
        extra_data={"id_token": ".".join(["foo", raw_token, "bar"])},
    )

    response = api_client.get(reverse("userinfo"))

    assert response.status_code == status.HTTP_200_OK, response.json()

    assert response.json() == {
        "first_name": data["given_name"],
        "last_name": data["family_name"],
        "email": data["email"],
    }


@pytest.mark.django_db
def test__api__userinfo__info_not_found(api_client: HitasAPIClient):
    response = api_client.get(reverse("userinfo"))
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
