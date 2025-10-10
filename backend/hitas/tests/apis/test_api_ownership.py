from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import OwnershipFactory


@pytest.mark.django_db
def test__api__ownership__update(api_client: HitasAPIClient):
    ownership = OwnershipFactory.create(percentage=50)
    # Create a second ownership to ensure other owners remain untouched
    OwnershipFactory.create(percentage=50, sale=ownership.sale)

    url = reverse("hitas:ownership-detail", kwargs={"uuid": ownership.uuid.hex})

    response = api_client.patch(url, data={"percentage": 75.5}, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    ownership.refresh_from_db()
    assert ownership.percentage == Decimal("75.5")
    assert response.json()["id"] == ownership.uuid.hex
    assert float(response.json()["percentage"]) == pytest.approx(75.5)


@pytest.mark.django_db
def test__api__ownership__update__invalid_percentage(api_client_novalidate: APIClient):
    ownership = OwnershipFactory.create(percentage=50)

    url = reverse("hitas:ownership-detail", kwargs={"uuid": ownership.uuid.hex})

    response = api_client_novalidate.patch(url, data={"percentage": 150}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json()["error"] == "bad_request"
    assert any(field["field"] == "percentage" for field in response.json().get("fields", []))
