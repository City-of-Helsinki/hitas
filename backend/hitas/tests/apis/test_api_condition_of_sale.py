from typing import NamedTuple

import pytest
from django.urls import reverse
from rest_framework import status

from hitas.models import Apartment, ConditionOfSale, Owner, Ownership
from hitas.models.condition_of_sale import GracePeriod
from hitas.tests.apis.helpers import HitasAPIClient, parametrize_helper
from hitas.tests.factories import ApartmentFactory, ConditionOfSaleFactory, OwnerFactory, OwnershipFactory
from hitas.views.condition_of_sale import ConditionOfSaleSerializer

# List tests


@pytest.mark.django_db
def test__api__condition_of_sale__list__empty(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()

    url = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner.uuid.hex,
        },
    )
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
def test__api__condition_of_sale__list(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(owner=owner)
    old_ownership: Ownership = OwnershipFactory.create(owner=owner)
    condition_of_sale: ConditionOfSale = ConditionOfSaleFactory.create(
        new_ownership=new_ownership,
        old_ownership=old_ownership,
    )

    url = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner.uuid.hex,
        },
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "id": condition_of_sale.uuid.hex,
            "grace_period": str(condition_of_sale.grace_period.value),
            "fulfilled": condition_of_sale.fulfilled,
            "new_ownership": {
                "id": new_ownership.uuid.hex,
                "percentage": float(new_ownership.percentage),
                "apartment": {
                    "id": new_ownership.apartment.uuid.hex,
                    "street_address": new_ownership.apartment.street_address,
                    "apartment_number": new_ownership.apartment.apartment_number,
                    "floor": new_ownership.apartment.floor,
                    "stair": new_ownership.apartment.stair,
                },
                "owner": {
                    "id": new_ownership.owner.uuid.hex,
                    "name": new_ownership.owner.name,
                    "identifier": new_ownership.owner.identifier,
                    "email": new_ownership.owner.email,
                },
            },
            "old_ownership": {
                "id": old_ownership.uuid.hex,
                "percentage": float(old_ownership.percentage),
                "apartment": {
                    "id": old_ownership.apartment.uuid.hex,
                    "street_address": old_ownership.apartment.street_address,
                    "apartment_number": old_ownership.apartment.apartment_number,
                    "floor": old_ownership.apartment.floor,
                    "stair": old_ownership.apartment.stair,
                },
                "owner": {
                    "id": old_ownership.owner.uuid.hex,
                    "name": old_ownership.owner.name,
                    "identifier": old_ownership.owner.identifier,
                    "email": old_ownership.owner.email,
                },
            },
        }
    ]
    assert response.json()["page"] == {
        "size": 1,
        "current_page": 1,
        "total_items": 1,
        "total_pages": 1,
        "links": {
            "next": None,
            "previous": None,
        },
    }


# TODO: Test that old fulfilled conditions of sale won't show up


# Retrieve tests


@pytest.mark.django_db
def test__api__condition_of_sale__retrieve(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(owner=owner)
    old_ownership: Ownership = OwnershipFactory.create(owner=owner)
    condition_of_sale: ConditionOfSale = ConditionOfSaleFactory.create(
        new_ownership=new_ownership,
        old_ownership=old_ownership,
    )

    url = reverse(
        "hitas:conditions-of-sale-detail",
        kwargs={
            "owner_uuid": owner.uuid.hex,
            "uuid": condition_of_sale.uuid.hex,
        },
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": condition_of_sale.uuid.hex,
        "grace_period": str(condition_of_sale.grace_period.value),
        "fulfilled": condition_of_sale.fulfilled,
        "new_ownership": {
            "id": new_ownership.uuid.hex,
            "percentage": float(new_ownership.percentage),
            "apartment": {
                "id": new_ownership.apartment.uuid.hex,
                "street_address": new_ownership.apartment.street_address,
                "apartment_number": new_ownership.apartment.apartment_number,
                "floor": new_ownership.apartment.floor,
                "stair": new_ownership.apartment.stair,
            },
            "owner": {
                "id": new_ownership.owner.uuid.hex,
                "name": new_ownership.owner.name,
                "identifier": new_ownership.owner.identifier,
                "email": new_ownership.owner.email,
            },
        },
        "old_ownership": {
            "id": old_ownership.uuid.hex,
            "percentage": float(old_ownership.percentage),
            "apartment": {
                "id": old_ownership.apartment.uuid.hex,
                "street_address": old_ownership.apartment.street_address,
                "apartment_number": old_ownership.apartment.apartment_number,
                "floor": old_ownership.apartment.floor,
                "stair": old_ownership.apartment.stair,
            },
            "owner": {
                "id": old_ownership.owner.uuid.hex,
                "name": old_ownership.owner.name,
                "identifier": old_ownership.owner.identifier,
                "email": old_ownership.owner.email,
            },
        },
    }


# Create tests


@pytest.mark.django_db
def test__api__condition_of_sale__create(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    new_apartment: Apartment = ApartmentFactory.create(first_purchase_date=None, latest_purchase_date=None)
    old_apartment: Apartment = ApartmentFactory.create()
    OwnershipFactory.create(owner=owner, apartment=new_apartment)
    OwnershipFactory.create(owner=owner, apartment=old_apartment)

    url_1 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data={}, format="json")
    assert response_1.status_code == status.HTTP_201_CREATED, response_1.json()

    assert "created" in response_1.json(), response_1.json()
    assert len(response_1.json()["created"]) == 1, response_1.json()["created"]

    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 1
    assert conditions_of_sale[0].uuid.hex == response_1.json()["created"][0]["id"]

    url_2 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner.uuid.hex,
        },
    )
    response_2 = api_client.get(url_2)
    assert response_2.status_code == status.HTTP_200_OK, response_2.json()
    assert response_2.json()["contents"] == response_1.json()["created"]


# Update tests


class ConditionOfSaleUpdateArgs(NamedTuple):
    grace_period: GracePeriod = ...


@pytest.mark.parametrize(
    **parametrize_helper(
        {
            "Change grace period to three months": ConditionOfSaleUpdateArgs(
                grace_period=GracePeriod.THREE_MONTHS,
            ),
            "Change grace period to six months": ConditionOfSaleUpdateArgs(
                grace_period=GracePeriod.SIX_MONTHS,
            ),
        },
    ),
)
@pytest.mark.django_db
def test__api__condition_of_sale__update(api_client: HitasAPIClient, grace_period: GracePeriod):
    owner: Owner = OwnerFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(owner=owner)
    old_ownership: Ownership = OwnershipFactory.create(owner=owner)
    condition_of_sale: ConditionOfSale = ConditionOfSaleFactory.create(
        new_ownership=new_ownership,
        old_ownership=old_ownership,
        grace_period=GracePeriod.NOT_GIVEN,
    )

    data = ConditionOfSaleSerializer(condition_of_sale).data
    del data["id"]
    del data["new_ownership"]
    del data["old_ownership"]
    del data["fulfilled"]
    if grace_period is not ...:
        data["grace_period"] = str(grace_period.value)

    url = reverse(
        "hitas:conditions-of-sale-detail",
        kwargs={
            "owner_uuid": owner.uuid.hex,
            "uuid": condition_of_sale.uuid.hex,
        },
    )
    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": condition_of_sale.uuid.hex,
        "grace_period": str(grace_period.value),
        "fulfilled": condition_of_sale.fulfilled,
        "new_ownership": {
            "id": new_ownership.uuid.hex,
            "percentage": float(new_ownership.percentage),
            "apartment": {
                "id": new_ownership.apartment.uuid.hex,
                "street_address": new_ownership.apartment.street_address,
                "apartment_number": new_ownership.apartment.apartment_number,
                "floor": new_ownership.apartment.floor,
                "stair": new_ownership.apartment.stair,
            },
            "owner": {
                "id": new_ownership.owner.uuid.hex,
                "name": new_ownership.owner.name,
                "identifier": new_ownership.owner.identifier,
                "email": new_ownership.owner.email,
            },
        },
        "old_ownership": {
            "id": old_ownership.uuid.hex,
            "percentage": float(old_ownership.percentage),
            "apartment": {
                "id": old_ownership.apartment.uuid.hex,
                "street_address": old_ownership.apartment.street_address,
                "apartment_number": old_ownership.apartment.apartment_number,
                "floor": old_ownership.apartment.floor,
                "stair": old_ownership.apartment.stair,
            },
            "owner": {
                "id": old_ownership.owner.uuid.hex,
                "name": old_ownership.owner.name,
                "identifier": old_ownership.owner.identifier,
                "email": old_ownership.owner.email,
            },
        },
    }


# Delete tests


@pytest.mark.django_db
def test__api__apartment_sale__delete(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(owner=owner)
    old_ownership: Ownership = OwnershipFactory.create(owner=owner)
    condition_of_sale: ConditionOfSale = ConditionOfSaleFactory.create(
        new_ownership=new_ownership,
        old_ownership=old_ownership,
        grace_period=GracePeriod.NOT_GIVEN,
    )

    url = reverse(
        "hitas:conditions-of-sale-detail",
        kwargs={
            "owner_uuid": owner.uuid.hex,
            "uuid": condition_of_sale.uuid.hex,
        },
    )
    response_1 = api_client.delete(url)
    assert response_1.status_code == status.HTTP_204_NO_CONTENT, response_1.json()

    response_2 = api_client.get(url)
    assert response_2.status_code == status.HTTP_404_NOT_FOUND, response_2.json()
