import pytest
from django.urls import reverse
from rest_framework import status

from hitas.tests.apis.helpers import HitasAPIClient


@pytest.mark.django_db
def test__api__csrf__refreshes_csrf_cookie(api_client: HitasAPIClient):
    response = api_client.get(reverse("csrf"))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert "csrftoken" in response.cookies
