import pytest
from django.urls import reverse
from rest_framework import status

from hitas.models.condition_of_sale import ConditionOfSale
from hitas.models.owner import Owner
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import (
    ConditionOfSaleFactory,
    OwnerFactory,
)


@pytest.mark.django_db
def test__api__condition_of_sale__delete__different_owners(api_client: HitasAPIClient, freezer, settings):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    owner_1: Owner = OwnerFactory.create()
    owner_2: Owner = OwnerFactory.create()

    condition_of_sale: ConditionOfSale = ConditionOfSaleFactory.create(
        new_ownership__owner=owner_1,
        old_ownership__owner=owner_2,
    )

    url = reverse(
        "hitas:conditions-of-sale-detail",
        kwargs={
            "uuid": condition_of_sale.uuid.hex,
        },
    )
    response_1 = api_client.delete(url)
    # Deletion is allowed since the old and new owners are not the same (created through a household)
    assert response_1.status_code == status.HTTP_204_NO_CONTENT, response_1.json()

    # The condition of sale is hard deleted
    response_2 = api_client.get(url)
    assert response_2.status_code == status.HTTP_404_NOT_FOUND, response_2.json()


@pytest.mark.django_db
def test__api__condition_of_sale__delete__same_owners(api_client: HitasAPIClient, settings):
    owner: Owner = OwnerFactory.create()

    condition_of_sale: ConditionOfSale = ConditionOfSaleFactory.create(
        new_ownership__owner=owner,
        old_ownership__owner=owner,
    )

    url = reverse(
        "hitas:conditions-of-sale-detail",
        kwargs={
            "uuid": condition_of_sale.uuid.hex,
        },
    )
    response = api_client.delete(url)
    # Deletion is not allowed since the old and new owners are the same (created through a sale)
    assert response.status_code == status.HTTP_409_CONFLICT, response.json()

    assert response.json() == {
        "error": "invalid",
        "message": "Cannot delete condition of sale between the same owner.",
        "reason": "Conflict",
        "status": 409,
    }


@pytest.mark.django_db
def test__api__condition_of_sale__delete__cascade_from_ownership(api_client: HitasAPIClient):
    condition_of_sale: ConditionOfSale = ConditionOfSaleFactory.create()

    assert condition_of_sale.fulfilled is None

    condition_of_sale.new_ownership.delete()
    condition_of_sale.refresh_from_db()
    assert condition_of_sale.fulfilled is not None

    condition_of_sale.new_ownership.undelete()
    condition_of_sale.refresh_from_db()
    assert condition_of_sale.fulfilled is None

    condition_of_sale.old_ownership.delete()
    condition_of_sale.refresh_from_db()
    assert condition_of_sale.fulfilled is not None

    condition_of_sale.old_ownership.undelete()
    condition_of_sale.refresh_from_db()
    assert condition_of_sale.fulfilled is None
