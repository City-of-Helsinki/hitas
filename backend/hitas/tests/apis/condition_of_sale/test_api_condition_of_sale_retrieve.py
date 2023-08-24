import uuid

import pytest
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from hitas.models.condition_of_sale import ConditionOfSale
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import (
    ConditionOfSaleFactory,
    OwnerFactory,
)


def format_condition_of_sale(cos: ConditionOfSale) -> dict:
    return {
        "id": cos.uuid.hex,
        "grace_period": str(cos.grace_period.value),
        "fulfilled": cos.fulfilled,
        "new_ownership": {
            "percentage": float(cos.new_ownership.percentage),
            "apartment": {
                "id": cos.new_ownership.apartment.uuid.hex,
                "address": {
                    "street_address": cos.new_ownership.apartment.street_address,
                    "apartment_number": cos.new_ownership.apartment.apartment_number,
                    "floor": cos.new_ownership.apartment.floor,
                    "stair": cos.new_ownership.apartment.stair,
                    "city": "Helsinki",
                    "postal_code": cos.new_ownership.apartment.postal_code.value,
                },
                "housing_company": {
                    "id": cos.new_ownership.apartment.housing_company.uuid.hex,
                    "display_name": cos.new_ownership.apartment.housing_company.display_name,
                },
            },
            "owner": {
                "id": cos.new_ownership.owner.uuid.hex,
                "name": cos.new_ownership.owner.name,
                "identifier": cos.new_ownership.owner.identifier,
                "email": cos.new_ownership.owner.email,
                "non_disclosure": cos.new_ownership.owner.non_disclosure,
            },
        },
        "old_ownership": {
            "percentage": float(cos.old_ownership.percentage),
            "apartment": {
                "id": cos.old_ownership.apartment.uuid.hex,
                "address": {
                    "street_address": cos.old_ownership.apartment.street_address,
                    "apartment_number": cos.old_ownership.apartment.apartment_number,
                    "floor": cos.old_ownership.apartment.floor,
                    "stair": cos.old_ownership.apartment.stair,
                    "city": "Helsinki",
                    "postal_code": cos.old_ownership.apartment.postal_code.value,
                },
                "housing_company": {
                    "id": cos.old_ownership.apartment.housing_company.uuid.hex,
                    "display_name": cos.old_ownership.apartment.housing_company.display_name,
                },
            },
            "owner": {
                "id": cos.old_ownership.owner.uuid.hex,
                "name": cos.old_ownership.owner.name,
                "identifier": cos.old_ownership.owner.identifier,
                "email": cos.old_ownership.owner.email,
                "non_disclosure": cos.old_ownership.owner.non_disclosure,
            },
        },
    }


# List tests


@pytest.mark.django_db
def test__api__condition_of_sale__list__empty(api_client: HitasAPIClient):
    OwnerFactory.create()

    url = reverse("hitas:conditions-of-sale-list")
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
    cos: ConditionOfSale = ConditionOfSaleFactory.create()

    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        format_condition_of_sale(cos),
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
    cos_1: ConditionOfSale = ConditionOfSaleFactory.create()
    cos_2: ConditionOfSale = ConditionOfSaleFactory.create()

    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        format_condition_of_sale(cos_1),
        format_condition_of_sale(cos_2),
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

    ConditionOfSaleFactory.create()
    condition_of_sale_2: ConditionOfSale = ConditionOfSaleFactory.create()
    condition_of_sale_2.delete()

    freezer.move_to(old_time + settings.SHOW_FULFILLED_CONDITIONS_OF_SALE_FOR_MONTHS)

    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == 2
    assert response.json()["contents"][1]["fulfilled"] == old_time_str


@pytest.mark.django_db
def test__api__condition_of_sale__list__fulfilled_over_x_months(api_client: HitasAPIClient, freezer, settings):
    freezer.move_to("2023-01-01 00:00:00+00:00")
    old_time = timezone.now()

    condition_of_sale_1: ConditionOfSale = ConditionOfSaleFactory.create()
    condition_of_sale_2: ConditionOfSale = ConditionOfSaleFactory.create()
    condition_of_sale_2.delete()

    freezer.move_to(old_time + settings.SHOW_FULFILLED_CONDITIONS_OF_SALE_FOR_MONTHS + relativedelta(seconds=1))

    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == 1

    alive_conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(alive_conditions_of_sale) == 1
    assert alive_conditions_of_sale[0].uuid.hex == condition_of_sale_1.uuid.hex
    assert alive_conditions_of_sale[0].fulfilled is None

    deleted_conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.deleted_objects.all())
    assert len(deleted_conditions_of_sale) == 1
    assert deleted_conditions_of_sale[0].uuid.hex == condition_of_sale_2.uuid.hex
    assert deleted_conditions_of_sale[0].fulfilled == old_time


# Retrieve tests


@pytest.mark.django_db
def test__api__condition_of_sale__retrieve(api_client: HitasAPIClient):
    cos: ConditionOfSale = ConditionOfSaleFactory.create()

    url = reverse(
        "hitas:conditions-of-sale-detail",
        kwargs={
            "uuid": cos.uuid.hex,
        },
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == format_condition_of_sale(cos)


@pytest.mark.django_db
def test__api__condition_of_sale__retrieve__fulfilled_over_x_months(api_client: HitasAPIClient, freezer, settings):
    freezer.move_to("2023-01-01 00:00:00+00:00")
    old_time = timezone.now()

    condition_of_sale: ConditionOfSale = ConditionOfSaleFactory.create()
    condition_of_sale.delete()

    freezer.move_to(old_time + settings.SHOW_FULFILLED_CONDITIONS_OF_SALE_FOR_MONTHS + relativedelta(seconds=1))

    url = reverse(
        "hitas:conditions-of-sale-detail",
        kwargs={
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
    url = reverse(
        "hitas:conditions-of-sale-detail",
        kwargs={
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
