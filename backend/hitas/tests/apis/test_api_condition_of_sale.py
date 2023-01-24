import uuid
from typing import Any, NamedTuple

import pytest
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from hitas.models import Apartment, ConditionOfSale, Owner, Ownership
from hitas.models.condition_of_sale import GracePeriod
from hitas.tests.apis.helpers import HitasAPIClient, InvalidInput, parametrize_helper
from hitas.tests.factories import (
    ApartmentFactory,
    ApartmentSaleFactory,
    ConditionOfSaleFactory,
    OwnerFactory,
    OwnershipFactory,
)
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
def test__api__condition_of_sale__list__single(api_client: HitasAPIClient):
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


@pytest.mark.django_db
def test__api__condition_of_sale__list__multiple(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(owner=owner)
    old_ownership_1: Ownership = OwnershipFactory.create(owner=owner)
    old_ownership_2: Ownership = OwnershipFactory.create(owner=owner)
    condition_of_sale_1: ConditionOfSale = ConditionOfSaleFactory.create(
        new_ownership=new_ownership,
        old_ownership=old_ownership_1,
    )
    condition_of_sale_2: ConditionOfSale = ConditionOfSaleFactory.create(
        new_ownership=new_ownership,
        old_ownership=old_ownership_2,
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
            "id": condition_of_sale_1.uuid.hex,
            "grace_period": str(condition_of_sale_1.grace_period.value),
            "fulfilled": condition_of_sale_1.fulfilled,
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
                "id": old_ownership_1.uuid.hex,
                "percentage": float(old_ownership_1.percentage),
                "apartment": {
                    "id": old_ownership_1.apartment.uuid.hex,
                    "street_address": old_ownership_1.apartment.street_address,
                    "apartment_number": old_ownership_1.apartment.apartment_number,
                    "floor": old_ownership_1.apartment.floor,
                    "stair": old_ownership_1.apartment.stair,
                },
                "owner": {
                    "id": old_ownership_1.owner.uuid.hex,
                    "name": old_ownership_1.owner.name,
                    "identifier": old_ownership_1.owner.identifier,
                    "email": old_ownership_1.owner.email,
                },
            },
        },
        {
            "id": condition_of_sale_2.uuid.hex,
            "grace_period": str(condition_of_sale_2.grace_period.value),
            "fulfilled": condition_of_sale_2.fulfilled,
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
                "id": old_ownership_2.uuid.hex,
                "percentage": float(old_ownership_2.percentage),
                "apartment": {
                    "id": old_ownership_2.apartment.uuid.hex,
                    "street_address": old_ownership_2.apartment.street_address,
                    "apartment_number": old_ownership_2.apartment.apartment_number,
                    "floor": old_ownership_2.apartment.floor,
                    "stair": old_ownership_2.apartment.stair,
                },
                "owner": {
                    "id": old_ownership_2.owner.uuid.hex,
                    "name": old_ownership_2.owner.name,
                    "identifier": old_ownership_2.owner.identifier,
                    "email": old_ownership_2.owner.email,
                },
            },
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


@pytest.mark.django_db
def test__api__condition_of_sale__list__fulfilled_under_x_months(api_client: HitasAPIClient, freezer, settings):
    freezer.move_to("2023-01-01 00:00:00+00:00")
    old_time = timezone.now()
    old_time_str = old_time.replace(tzinfo=None).isoformat(timespec="seconds") + "Z"

    owner: Owner = OwnerFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(owner=owner)
    old_ownership_1: Ownership = OwnershipFactory.create(owner=owner)
    old_ownership_2: Ownership = OwnershipFactory.create(owner=owner)
    ConditionOfSaleFactory.create(
        new_ownership=new_ownership,
        old_ownership=old_ownership_1,
    )
    condition_of_sale_2: ConditionOfSale = ConditionOfSaleFactory.create(
        new_ownership=new_ownership,
        old_ownership=old_ownership_2,
    )
    condition_of_sale_2.delete()

    freezer.move_to(old_time + settings.SHOW_FULFILLED_CONDITIONS_OF_SALE_FOR_MONTHS)

    url = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner.uuid.hex,
        },
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == 2
    assert response.json()["contents"][1]["id"] == condition_of_sale_2.uuid.hex
    assert response.json()["contents"][1]["fulfilled"] == old_time_str


@pytest.mark.django_db
def test__api__condition_of_sale__list__fulfilled_over_x_months(api_client: HitasAPIClient, freezer, settings):
    freezer.move_to("2023-01-01 00:00:00+00:00")
    old_time = timezone.now()

    owner: Owner = OwnerFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(owner=owner)
    old_ownership_1: Ownership = OwnershipFactory.create(owner=owner)
    old_ownership_2: Ownership = OwnershipFactory.create(owner=owner)
    condition_of_sale_1: ConditionOfSale = ConditionOfSaleFactory.create(
        new_ownership=new_ownership,
        old_ownership=old_ownership_1,
    )
    condition_of_sale_2: ConditionOfSale = ConditionOfSaleFactory.create(
        new_ownership=new_ownership,
        old_ownership=old_ownership_2,
    )
    condition_of_sale_2.delete()

    freezer.move_to(old_time + settings.SHOW_FULFILLED_CONDITIONS_OF_SALE_FOR_MONTHS + relativedelta(seconds=1))

    url = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner.uuid.hex,
        },
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == 1
    assert response.json()["contents"][0]["id"] == condition_of_sale_1.uuid.hex

    alive_conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(alive_conditions_of_sale) == 1

    all_conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.all_objects.all())
    assert len(all_conditions_of_sale) == 2

    deleted_conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.deleted_objects.all())
    assert len(deleted_conditions_of_sale) == 1
    assert deleted_conditions_of_sale[0].fulfilled == old_time


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


@pytest.mark.django_db
def test__api__condition_of_sale__retrieve__fulfilled_over_x_months(api_client: HitasAPIClient, freezer, settings):
    freezer.move_to("2023-01-01 00:00:00+00:00")
    old_time = timezone.now()

    owner: Owner = OwnerFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(owner=owner)
    old_ownership: Ownership = OwnershipFactory.create(owner=owner)
    condition_of_sale: ConditionOfSale = ConditionOfSaleFactory.create(
        new_ownership=new_ownership,
        old_ownership=old_ownership,
    )
    condition_of_sale.delete()

    freezer.move_to(old_time + settings.SHOW_FULFILLED_CONDITIONS_OF_SALE_FOR_MONTHS + relativedelta(seconds=1))

    url = reverse(
        "hitas:conditions-of-sale-detail",
        kwargs={
            "owner_uuid": owner.uuid.hex,
            "uuid": condition_of_sale.uuid.hex,
        },
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "condition_of_sale_not_found",
        "message": "Condition of Sale not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__condition_of_sale__retrieve__invalid_id(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()

    url = reverse(
        "hitas:conditions-of-sale-detail",
        kwargs={
            "owner_uuid": owner.uuid.hex,
            "uuid": uuid.uuid4().hex,
        },
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "condition_of_sale_not_found",
        "message": "Condition of Sale not found",
        "reason": "Not Found",
        "status": 404,
    }


# Create tests


@pytest.mark.django_db
def test__api__condition_of_sale__create(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    new_apartment: Apartment = ApartmentFactory.create(first_purchase_date=None)
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

    assert "conditions_of_sale" in response_1.json(), response_1.json()
    assert len(response_1.json()["conditions_of_sale"]) == 1, response_1.json()["conditions_of_sale"]

    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 1
    assert conditions_of_sale[0].uuid.hex == response_1.json()["conditions_of_sale"][0]["id"]

    url_2 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner.uuid.hex,
        },
    )
    response_2 = api_client.get(url_2)
    assert response_2.status_code == status.HTTP_200_OK, response_2.json()
    assert response_2.json()["contents"] == response_1.json()["conditions_of_sale"]


@pytest.mark.django_db
def test__api__condition_of_sale__create__no_ownerships(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()

    url_1 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner.uuid.hex,
        },
    )
    response = api_client.post(url_1, data={}, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()

    assert "conditions_of_sale" in response.json(), response.json()
    assert len(response.json()["conditions_of_sale"]) == 0, response.json()["conditions_of_sale"]

    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 0


@pytest.mark.django_db
def test__api__condition_of_sale__create__no_new_apartments(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    apartment_1: Apartment = ApartmentFactory.create()
    apartment_2: Apartment = ApartmentFactory.create()
    OwnershipFactory.create(owner=owner, apartment=apartment_1)
    OwnershipFactory.create(owner=owner, apartment=apartment_2)

    url_1 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner.uuid.hex,
        },
    )
    response = api_client.post(url_1, data={}, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()

    assert "conditions_of_sale" in response.json(), response.json()
    assert len(response.json()["conditions_of_sale"]) == 0, response.json()["conditions_of_sale"]

    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 0


@pytest.mark.django_db
def test__api__condition_of_sale__create__some_already_exist(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    new_apartment: Apartment = ApartmentFactory.create(first_purchase_date=None)
    old_apartment_1: Apartment = ApartmentFactory.create()
    old_apartment_2: Apartment = ApartmentFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(owner=owner, apartment=new_apartment)
    old_ownership_1: Ownership = OwnershipFactory.create(owner=owner, apartment=old_apartment_1)
    OwnershipFactory.create(owner=owner, apartment=old_apartment_2)
    ConditionOfSaleFactory.create(
        new_ownership=new_ownership,
        old_ownership=old_ownership_1,
    )

    url_1 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data={}, format="json")
    assert response_1.status_code == status.HTTP_201_CREATED, response_1.json()

    assert "conditions_of_sale" in response_1.json(), response_1.json()
    assert len(response_1.json()["conditions_of_sale"]) == 2, response_1.json()["conditions_of_sale"]

    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 2

    url_2 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner.uuid.hex,
        },
    )
    response_2 = api_client.get(url_2)
    assert response_2.status_code == status.HTTP_200_OK, response_2.json()
    assert response_2.json()["contents"] == response_1.json()["conditions_of_sale"]


@pytest.mark.django_db
def test__api__condition_of_sale__create__all_already_exist(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    new_apartment: Apartment = ApartmentFactory.create(first_purchase_date=None)
    old_apartment_1: Apartment = ApartmentFactory.create()
    old_apartment_2: Apartment = ApartmentFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(owner=owner, apartment=new_apartment)
    old_ownership_1: Ownership = OwnershipFactory.create(owner=owner, apartment=old_apartment_1)
    old_ownership_2: Ownership = OwnershipFactory.create(owner=owner, apartment=old_apartment_2)
    ConditionOfSaleFactory.create(
        new_ownership=new_ownership,
        old_ownership=old_ownership_1,
    )
    ConditionOfSaleFactory.create(
        new_ownership=new_ownership,
        old_ownership=old_ownership_2,
    )

    url_1 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data={}, format="json")
    assert response_1.status_code == status.HTTP_201_CREATED, response_1.json()

    assert "conditions_of_sale" in response_1.json(), response_1.json()
    assert len(response_1.json()["conditions_of_sale"]) == 2, response_1.json()["conditions_of_sale"]

    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 2

    url_2 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner.uuid.hex,
        },
    )
    response_2 = api_client.get(url_2)
    assert response_2.status_code == status.HTTP_200_OK, response_2.json()
    assert response_2.json()["contents"] == response_1.json()["conditions_of_sale"]


@pytest.mark.django_db
def test__api__condition_of_sale__create__has_sales__in_the_future(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    new_apartment: Apartment = ApartmentFactory.create(first_purchase_date=None)
    old_apartment: Apartment = ApartmentFactory.create()
    ownership_1: Ownership = OwnershipFactory.create(owner=owner, apartment=new_apartment)
    OwnershipFactory.create(owner=owner, apartment=old_apartment)
    ApartmentSaleFactory.create(
        apartment=new_apartment,
        ownerships=[ownership_1],
        purchase_date=timezone.now() + relativedelta(days=1),
    )

    url_1 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data={}, format="json")
    assert response_1.status_code == status.HTTP_201_CREATED, response_1.json()

    assert "conditions_of_sale" in response_1.json(), response_1.json()
    assert len(response_1.json()["conditions_of_sale"]) == 1, response_1.json()["conditions_of_sale"]

    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 1
    assert conditions_of_sale[0].uuid.hex == response_1.json()["conditions_of_sale"][0]["id"]

    url_2 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner.uuid.hex,
        },
    )
    response_2 = api_client.get(url_2)
    assert response_2.status_code == status.HTTP_200_OK, response_2.json()
    assert response_2.json()["contents"] == response_1.json()["conditions_of_sale"]


@pytest.mark.django_db
def test__api__condition_of_sale__create__has_sales__in_the_past(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    new_apartment: Apartment = ApartmentFactory.create(first_purchase_date=None)
    old_apartment: Apartment = ApartmentFactory.create()
    ownership_1: Ownership = OwnershipFactory.create(owner=owner, apartment=new_apartment)
    OwnershipFactory.create(owner=owner, apartment=old_apartment)
    ApartmentSaleFactory.create(
        apartment=new_apartment,
        ownerships=[ownership_1],
        purchase_date=timezone.now() - relativedelta(days=1),
    )

    url_1 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data={}, format="json")
    assert response_1.status_code == status.HTTP_201_CREATED, response_1.json()

    assert "conditions_of_sale" in response_1.json(), response_1.json()
    assert len(response_1.json()["conditions_of_sale"]) == 0, response_1.json()["conditions_of_sale"]

    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 0


@pytest.mark.django_db
def test__api__condition_of_sale__create__only_one_old_apartment(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    old_apartment: Apartment = ApartmentFactory.create()

    OwnershipFactory.create(owner=owner, apartment=old_apartment)

    url_1 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data={}, format="json")
    assert response_1.status_code == status.HTTP_201_CREATED, response_1.json()

    assert "conditions_of_sale" in response_1.json(), response_1.json()
    assert len(response_1.json()["conditions_of_sale"]) == 0, response_1.json()["conditions_of_sale"]

    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 0


@pytest.mark.django_db
def test__api__condition_of_sale__create__only_one_new_apartment(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    new_apartment: Apartment = ApartmentFactory.create(first_purchase_date=None)
    OwnershipFactory.create(owner=owner, apartment=new_apartment)

    url_1 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data={}, format="json")
    assert response_1.status_code == status.HTTP_201_CREATED, response_1.json()

    assert "conditions_of_sale" in response_1.json(), response_1.json()
    assert len(response_1.json()["conditions_of_sale"]) == 0, response_1.json()["conditions_of_sale"]

    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 0


@pytest.mark.django_db
def test__api__condition_of_sale__create__additional_ownerships__single(api_client: HitasAPIClient):
    owner_1: Owner = OwnerFactory.create()
    old_apartment: Apartment = ApartmentFactory.create()
    old_ownership: Ownership = OwnershipFactory.create(owner=owner_1, apartment=old_apartment)

    # Additional ownership to add
    owner_2: Owner = OwnerFactory.create()
    other_apartment: Apartment = ApartmentFactory.create(first_purchase_date=None)
    other_ownership: Ownership = OwnershipFactory.create(owner=owner_2, apartment=other_apartment)

    data = {
        "additional_ownerships": [
            other_ownership.uuid.hex,
        ]
    }

    url_1 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner_1.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data=data, format="json")
    assert response_1.status_code == status.HTTP_201_CREATED, response_1.json()

    assert "conditions_of_sale" in response_1.json(), response_1.json()
    assert len(response_1.json()["conditions_of_sale"]) == 1, response_1.json()["conditions_of_sale"]

    assert len(ConditionOfSale.objects.all()) == 1
    assert ConditionOfSale.objects.filter(new_ownership=other_ownership, old_ownership=old_ownership).exists()

    url_2 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner_1.uuid.hex,
        },
    )
    response_2 = api_client.get(url_2)
    assert response_2.status_code == status.HTTP_200_OK, response_2.json()
    assert response_2.json()["contents"] == response_1.json()["conditions_of_sale"]


@pytest.mark.django_db
def test__api__condition_of_sale__create__additional_ownerships__multiple(api_client: HitasAPIClient):
    owner_1: Owner = OwnerFactory.create()
    old_apartment: Apartment = ApartmentFactory.create()
    old_ownership: Ownership = OwnershipFactory.create(owner=owner_1, apartment=old_apartment)

    # Additional ownerships to add
    owner_2: Owner = OwnerFactory.create()
    other_apartment_1: Apartment = ApartmentFactory.create(first_purchase_date=None)
    other_apartment_2: Apartment = ApartmentFactory.create(first_purchase_date=None)
    other_ownership_1: Ownership = OwnershipFactory.create(owner=owner_2, apartment=other_apartment_1)
    other_ownership_2: Ownership = OwnershipFactory.create(owner=owner_2, apartment=other_apartment_2)

    data = {
        "additional_ownerships": [
            other_ownership_1.uuid.hex,
            other_ownership_2.uuid.hex,
        ]
    }

    url_1 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner_1.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data=data, format="json")
    assert response_1.status_code == status.HTTP_201_CREATED, response_1.json()

    assert "conditions_of_sale" in response_1.json(), response_1.json()
    # Conditions of sale between the additional ownerships should not be created
    assert len(response_1.json()["conditions_of_sale"]) == 2, response_1.json()["conditions_of_sale"]

    assert len(ConditionOfSale.objects.all()) == 2
    assert ConditionOfSale.objects.filter(new_ownership=other_ownership_1, old_ownership=old_ownership).exists()
    assert ConditionOfSale.objects.filter(new_ownership=other_ownership_2, old_ownership=old_ownership).exists()

    url_2 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner_1.uuid.hex,
        },
    )
    response_2 = api_client.get(url_2)
    assert response_2.status_code == status.HTTP_200_OK, response_2.json()
    assert response_2.json()["contents"] == response_1.json()["conditions_of_sale"]


@pytest.mark.django_db
def test__api__condition_of_sale__create__additional_ownerships__not_new(api_client: HitasAPIClient):
    owner_1: Owner = OwnerFactory.create()
    old_apartment: Apartment = ApartmentFactory.create()
    OwnershipFactory.create(owner=owner_1, apartment=old_apartment)

    # Additional ownership to add
    owner_2: Owner = OwnerFactory.create()
    other_apartment: Apartment = ApartmentFactory.create()
    other_ownership: Ownership = OwnershipFactory.create(owner=owner_2, apartment=other_apartment)

    data = {
        "additional_ownerships": [
            other_ownership.uuid.hex,
        ]
    }

    url_1 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner_1.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data=data, format="json")
    assert response_1.status_code == status.HTTP_201_CREATED, response_1.json()

    assert "conditions_of_sale" in response_1.json(), response_1.json()
    assert len(response_1.json()["conditions_of_sale"]) == 0, response_1.json()["conditions_of_sale"]

    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 0


@pytest.mark.django_db
def test__api__condition_of_sale__create__additional_ownerships__also_own_new_apartment(api_client: HitasAPIClient):
    owner_1: Owner = OwnerFactory.create()
    new_apartment: Apartment = ApartmentFactory.create(first_purchase_date=None)
    old_apartment: Apartment = ApartmentFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(owner=owner_1, apartment=new_apartment)
    old_ownership: Ownership = OwnershipFactory.create(owner=owner_1, apartment=old_apartment)

    # Additional ownership to add
    owner_2: Owner = OwnerFactory.create()
    other_apartment: Apartment = ApartmentFactory.create(first_purchase_date=None)
    other_ownership: Ownership = OwnershipFactory.create(owner=owner_2, apartment=other_apartment)

    data = {
        "additional_ownerships": [
            other_ownership.uuid.hex,
        ]
    }

    url_1 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner_1.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data=data, format="json")
    assert response_1.status_code == status.HTTP_201_CREATED, response_1.json()

    assert "conditions_of_sale" in response_1.json(), response_1.json()
    assert len(response_1.json()["conditions_of_sale"]) == 4, response_1.json()["conditions_of_sale"]

    assert len(ConditionOfSale.objects.all()) == 4
    assert ConditionOfSale.objects.filter(new_ownership=new_ownership, old_ownership=old_ownership).exists()
    assert ConditionOfSale.objects.filter(new_ownership=new_ownership, old_ownership=other_ownership).exists()
    assert ConditionOfSale.objects.filter(new_ownership=other_ownership, old_ownership=old_ownership).exists()
    assert ConditionOfSale.objects.filter(new_ownership=other_ownership, old_ownership=new_ownership).exists()

    url_2 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner_1.uuid.hex,
        },
    )
    response_2 = api_client.get(url_2)
    assert response_2.status_code == status.HTTP_200_OK, response_2.json()
    assert response_2.json()["contents"] == response_1.json()["conditions_of_sale"]


@pytest.mark.django_db
def test__api__condition_of_sale__create__additional_ownerships__not_exist(api_client: HitasAPIClient):
    owner_1: Owner = OwnerFactory.create()
    old_apartment: Apartment = ApartmentFactory.create()
    OwnershipFactory.create(owner=owner_1, apartment=old_apartment)

    data = {
        "additional_ownerships": [
            uuid.uuid4().hex,
        ]
    }

    url_1 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner_1.uuid.hex,
        },
    )
    response_1 = api_client.post(url_1, data=data, format="json")
    assert response_1.status_code == status.HTTP_201_CREATED, response_1.json()

    assert "conditions_of_sale" in response_1.json(), response_1.json()
    assert len(response_1.json()["conditions_of_sale"]) == 0, response_1.json()["conditions_of_sale"]

    assert len(ConditionOfSale.objects.all()) == 0


@pytest.mark.parametrize(
    **parametrize_helper(
        {
            "Some other string": InvalidInput(
                invalid_data={"additional_ownerships": ["foo"]},
                fields=[{"field": "additional_ownerships", "message": "Not a valid UUID hex."}],
            ),
            "Empty String.": InvalidInput(
                invalid_data={"additional_ownerships": [""]},
                fields=[{"field": "additional_ownerships", "message": "Not a valid UUID hex."}],
            ),
            "Some other type": InvalidInput(
                invalid_data={"additional_ownerships": [1]},
                fields=[{"field": "additional_ownerships", "message": "Not a valid UUID hex."}],
            ),
            "Not a list": InvalidInput(
                invalid_data={"additional_ownerships": "foo"},
                fields=[{"field": "additional_ownerships", "message": 'Expected a list of items but got type "str".'}],
            ),
            "Null value in list": InvalidInput(
                invalid_data={"additional_ownerships": [None]},
                fields=[{"field": "additional_ownerships.0", "message": "This field is mandatory and cannot be null."}],
            ),
            "Null value": InvalidInput(
                invalid_data={"additional_ownerships": None},
                fields=[{"field": "additional_ownerships", "message": "This field is mandatory and cannot be null."}],
            ),
        },
    ),
)
@pytest.mark.django_db
def test__api__condition_of_sale__create__additional_ownerships__invalid(
    api_client: HitasAPIClient,
    invalid_data: dict[str, Any],
    fields: list[dict[str, str]],
):
    owner: Owner = OwnerFactory.create()

    url_1 = reverse(
        "hitas:conditions-of-sale-list",
        kwargs={
            "owner_uuid": owner.uuid.hex,
        },
    )
    response = api_client.post(url_1, data=invalid_data, format="json", openapi_validate_request=False)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": fields,
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


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


@pytest.mark.parametrize(
    **parametrize_helper(
        {
            "Grace period cannot be null": InvalidInput(
                invalid_data={"grace_period": None},
                fields=[
                    {
                        "field": "grace_period",
                        "message": "This field is mandatory and cannot be null.",
                    },
                ],
            ),
            "Not a valid value for grace period": InvalidInput(
                invalid_data={"grace_period": "foo"},
                fields=[
                    {
                        "field": "grace_period",
                        "message": '"foo" is not a valid choice.',
                    },
                ],
            ),
        },
    ),
)
@pytest.mark.django_db
def test__api__condition_of_sale__update__invalid(api_client: HitasAPIClient, invalid_data: dict, fields: list):
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

    data.update(invalid_data)

    url = reverse(
        "hitas:conditions-of-sale-detail",
        kwargs={
            "owner_uuid": owner.uuid.hex,
            "uuid": condition_of_sale.uuid.hex,
        },
    )
    response = api_client.put(url, data=data, format="json", openapi_validate_request=False)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": fields,
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


# Delete tests


@pytest.mark.django_db
def test__api__condition_of_sale__delete(api_client: HitasAPIClient, freezer, settings):
    freezer.move_to("2023-01-01 00:00:00+00:00")
    old_time = timezone.now()

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
    response_1 = api_client.delete(url)
    assert response_1.status_code == status.HTTP_204_NO_CONTENT, response_1.json()

    freezer.move_to(old_time + settings.SHOW_FULFILLED_CONDITIONS_OF_SALE_FOR_MONTHS)

    # You can still find it 3 months after
    response_2 = api_client.get(url)
    assert response_2.status_code == status.HTTP_200_OK, response_2.json()

    freezer.move_to(old_time + settings.SHOW_FULFILLED_CONDITIONS_OF_SALE_FOR_MONTHS + relativedelta(seconds=1))

    # Can't find it over 3 months after
    response_2 = api_client.get(url)
    assert response_2.status_code == status.HTTP_404_NOT_FOUND, response_2.json()


@pytest.mark.django_db
def test__api__condition_of_sale__delete__cascade_from_ownership(api_client: HitasAPIClient):
    owner: Owner = OwnerFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(owner=owner)
    old_ownership: Ownership = OwnershipFactory.create(owner=owner)
    condition_of_sale: ConditionOfSale = ConditionOfSaleFactory.create(
        new_ownership=new_ownership,
        old_ownership=old_ownership,
    )

    assert condition_of_sale.fulfilled is None

    new_ownership.delete()
    condition_of_sale.refresh_from_db()
    assert condition_of_sale.fulfilled is not None

    new_ownership.undelete()
    condition_of_sale.refresh_from_db()
    assert condition_of_sale.fulfilled is None

    old_ownership.delete()
    condition_of_sale.refresh_from_db()
    assert condition_of_sale.fulfilled is not None

    old_ownership.undelete()
    condition_of_sale.refresh_from_db()
    assert condition_of_sale.fulfilled is None
