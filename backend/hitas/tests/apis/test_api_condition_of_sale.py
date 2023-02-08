import uuid
from typing import Any, NamedTuple, TypedDict

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
        {
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
    cos_1: ConditionOfSale = ConditionOfSaleFactory.create()
    cos_2: ConditionOfSale = ConditionOfSaleFactory.create()

    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "id": cos_1.uuid.hex,
            "grace_period": str(cos_1.grace_period.value),
            "fulfilled": cos_1.fulfilled,
            "new_ownership": {
                "percentage": float(cos_1.new_ownership.percentage),
                "apartment": {
                    "id": cos_1.new_ownership.apartment.uuid.hex,
                    "address": {
                        "street_address": cos_1.new_ownership.apartment.street_address,
                        "apartment_number": cos_1.new_ownership.apartment.apartment_number,
                        "floor": cos_1.new_ownership.apartment.floor,
                        "stair": cos_1.new_ownership.apartment.stair,
                        "city": "Helsinki",
                        "postal_code": cos_1.new_ownership.apartment.postal_code.value,
                    },
                    "housing_company": {
                        "id": cos_1.new_ownership.apartment.housing_company.uuid.hex,
                        "display_name": cos_1.new_ownership.apartment.housing_company.display_name,
                    },
                },
                "owner": {
                    "id": cos_1.new_ownership.owner.uuid.hex,
                    "name": cos_1.new_ownership.owner.name,
                    "identifier": cos_1.new_ownership.owner.identifier,
                    "email": cos_1.new_ownership.owner.email,
                },
            },
            "old_ownership": {
                "percentage": float(cos_1.old_ownership.percentage),
                "apartment": {
                    "id": cos_1.old_ownership.apartment.uuid.hex,
                    "address": {
                        "street_address": cos_1.old_ownership.apartment.street_address,
                        "apartment_number": cos_1.old_ownership.apartment.apartment_number,
                        "floor": cos_1.old_ownership.apartment.floor,
                        "stair": cos_1.old_ownership.apartment.stair,
                        "city": "Helsinki",
                        "postal_code": cos_1.old_ownership.apartment.postal_code.value,
                    },
                    "housing_company": {
                        "id": cos_1.old_ownership.apartment.housing_company.uuid.hex,
                        "display_name": cos_1.old_ownership.apartment.housing_company.display_name,
                    },
                },
                "owner": {
                    "id": cos_1.old_ownership.owner.uuid.hex,
                    "name": cos_1.old_ownership.owner.name,
                    "identifier": cos_1.old_ownership.owner.identifier,
                    "email": cos_1.old_ownership.owner.email,
                },
            },
        },
        {
            "id": cos_2.uuid.hex,
            "grace_period": str(cos_2.grace_period.value),
            "fulfilled": cos_2.fulfilled,
            "new_ownership": {
                "percentage": float(cos_2.new_ownership.percentage),
                "apartment": {
                    "id": cos_2.new_ownership.apartment.uuid.hex,
                    "address": {
                        "street_address": cos_2.new_ownership.apartment.street_address,
                        "apartment_number": cos_2.new_ownership.apartment.apartment_number,
                        "floor": cos_2.new_ownership.apartment.floor,
                        "stair": cos_2.new_ownership.apartment.stair,
                        "city": "Helsinki",
                        "postal_code": cos_2.new_ownership.apartment.postal_code.value,
                    },
                    "housing_company": {
                        "id": cos_2.new_ownership.apartment.housing_company.uuid.hex,
                        "display_name": cos_2.new_ownership.apartment.housing_company.display_name,
                    },
                },
                "owner": {
                    "id": cos_2.new_ownership.owner.uuid.hex,
                    "name": cos_2.new_ownership.owner.name,
                    "identifier": cos_2.new_ownership.owner.identifier,
                    "email": cos_2.new_ownership.owner.email,
                },
            },
            "old_ownership": {
                "percentage": float(cos_2.old_ownership.percentage),
                "apartment": {
                    "id": cos_2.old_ownership.apartment.uuid.hex,
                    "address": {
                        "street_address": cos_2.old_ownership.apartment.street_address,
                        "apartment_number": cos_2.old_ownership.apartment.apartment_number,
                        "floor": cos_2.old_ownership.apartment.floor,
                        "stair": cos_2.old_ownership.apartment.stair,
                        "city": "Helsinki",
                        "postal_code": cos_2.old_ownership.apartment.postal_code.value,
                    },
                    "housing_company": {
                        "id": cos_2.old_ownership.apartment.housing_company.uuid.hex,
                        "display_name": cos_2.old_ownership.apartment.housing_company.display_name,
                    },
                },
                "owner": {
                    "id": cos_2.old_ownership.owner.uuid.hex,
                    "name": cos_2.old_ownership.owner.name,
                    "identifier": cos_2.old_ownership.owner.identifier,
                    "email": cos_2.old_ownership.owner.email,
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
    assert response.json() == {
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
            },
        },
    }


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


# Create tests


@pytest.mark.django_db
def test__api__condition_of_sale__create__single(api_client: HitasAPIClient):
    # given:
    # - An owner with ownerships to one new and one old apartment
    owner: Owner = OwnerFactory.create()
    new_apartment: Apartment = ApartmentFactory.create(first_purchase_date=None)
    old_apartment: Apartment = ApartmentFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(owner=owner, apartment=new_apartment)
    old_ownership: Ownership = OwnershipFactory.create(owner=owner, apartment=old_apartment)

    # when:
    # - New conditions of sale are created for this owner as a household
    data = {"household": [owner.uuid.hex]}
    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.post(url, data=data, format="json")

    # then:
    # - The response contains a single condition of sale
    # - The database contains a single condition of sale
    # - The condition of sale is between the old and the new ownership for the given owner
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert len(response.json().get("conditions_of_sale", [])) == 1, response.json()
    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 1
    assert conditions_of_sale[0].new_ownership == new_ownership
    assert conditions_of_sale[0].old_ownership == old_ownership


@pytest.mark.django_db
def test__api__condition_of_sale__create__no_ownerships(api_client: HitasAPIClient):
    # given:
    # - An owner with no ownerships
    owner: Owner = OwnerFactory.create()

    # when:
    # - New conditions of sale are created for this owner as a household
    data = {"household": [owner.uuid.hex]}
    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.post(url, data=data, format="json")

    # then:
    # - The response contains no conditions of sale
    # - The database contains no conditions of sale
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert len(response.json().get("conditions_of_sale", [])) == 0, response.json()
    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 0


@pytest.mark.django_db
def test__api__condition_of_sale__create__no_new_apartments(api_client: HitasAPIClient):
    # given:
    # - An owner with no ownerships to new apartments
    owner: Owner = OwnerFactory.create()
    apartment_1: Apartment = ApartmentFactory.create()
    apartment_2: Apartment = ApartmentFactory.create()
    OwnershipFactory.create(owner=owner, apartment=apartment_1)
    OwnershipFactory.create(owner=owner, apartment=apartment_2)

    # when:
    # - New conditions of sale are created for this owner as a household
    data = {"household": [owner.uuid.hex]}
    url_1 = reverse("hitas:conditions-of-sale-list")
    response = api_client.post(url_1, data=data, format="json")

    # then:
    # - The response contains no conditions of sale
    # - The database contains no conditions of sale
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert len(response.json().get("conditions_of_sale", [])) == 0, response.json()
    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 0


@pytest.mark.django_db
def test__api__condition_of_sale__create__some_already_exist(api_client: HitasAPIClient):
    # given:
    # - An owner with ownerships to one new and two old apartment
    # - A condition of sale already exists between one new and old apartment, but not the other
    owner: Owner = OwnerFactory.create()
    new_apartment: Apartment = ApartmentFactory.create(first_purchase_date=None)
    old_apartment_1: Apartment = ApartmentFactory.create()
    old_apartment_2: Apartment = ApartmentFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(owner=owner, apartment=new_apartment)
    old_ownership_1: Ownership = OwnershipFactory.create(owner=owner, apartment=old_apartment_1)
    old_ownership_2: Ownership = OwnershipFactory.create(owner=owner, apartment=old_apartment_2)
    ConditionOfSaleFactory.create(new_ownership=new_ownership, old_ownership=old_ownership_1)

    # when:
    # - New conditions of sale are created for this owner as a household
    data = {"household": [owner.uuid.hex]}
    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.post(url, data=data, format="json")

    # then:
    # - The response contains two conditions of sale
    # - The database contains two conditions of sale
    # - The conditions of sale are between new ownership and the two old ownerships
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert len(response.json().get("conditions_of_sale", [])) == 2, response.json()
    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 2
    assert conditions_of_sale[0].new_ownership == new_ownership
    assert conditions_of_sale[0].old_ownership == old_ownership_1
    assert conditions_of_sale[1].new_ownership == new_ownership
    assert conditions_of_sale[1].old_ownership == old_ownership_2


@pytest.mark.django_db
def test__api__condition_of_sale__create__all_already_exist(api_client: HitasAPIClient):
    # given:
    # - An owner with ownerships to one new and two old apartment
    # - Conditions of sale already exists between the new and both old apartments
    owner: Owner = OwnerFactory.create()
    new_apartment: Apartment = ApartmentFactory.create(first_purchase_date=None)
    old_apartment_1: Apartment = ApartmentFactory.create()
    old_apartment_2: Apartment = ApartmentFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(owner=owner, apartment=new_apartment)
    old_ownership_1: Ownership = OwnershipFactory.create(owner=owner, apartment=old_apartment_1)
    old_ownership_2: Ownership = OwnershipFactory.create(owner=owner, apartment=old_apartment_2)
    ConditionOfSaleFactory.create(new_ownership=new_ownership, old_ownership=old_ownership_1)
    ConditionOfSaleFactory.create(new_ownership=new_ownership, old_ownership=old_ownership_2)

    # when:
    # - New conditions of sale are created for this owner as a household
    data = {"household": [owner.uuid.hex]}
    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.post(url, data=data, format="json")

    # then:
    # - The response contains two conditions of sale
    # - The database contains two conditions of sale
    # - The conditions of sale are between new ownership and the two old ownerships
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert len(response.json().get("conditions_of_sale", [])) == 2, response.json()
    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 2
    assert conditions_of_sale[0].new_ownership == new_ownership
    assert conditions_of_sale[0].old_ownership == old_ownership_1
    assert conditions_of_sale[1].new_ownership == new_ownership
    assert conditions_of_sale[1].old_ownership == old_ownership_2


@pytest.mark.django_db
def test__api__condition_of_sale__create__has_sales__in_the_future(api_client: HitasAPIClient):
    # given:
    # - An owner with ownerships to one new and two old apartment
    # - the new apartment has apartment sales in the future (apartment is still new)
    owner: Owner = OwnerFactory.create()
    new_apartment: Apartment = ApartmentFactory.create(first_purchase_date=None)
    old_apartment: Apartment = ApartmentFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(owner=owner, apartment=new_apartment)
    old_ownership: Ownership = OwnershipFactory.create(owner=owner, apartment=old_apartment)
    ApartmentSaleFactory.create(
        apartment=new_apartment,
        ownerships=[new_ownership],
        purchase_date=timezone.now() + relativedelta(days=1),
    )

    # when:
    # - New conditions of sale are created for this owner as a household
    data = {"household": [owner.uuid.hex]}
    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.post(url, data=data, format="json")

    # then:
    # - The response contains a single condition of sale
    # - The database contains a single condition of sale
    # - The condition of sale is between new ownership and the old ownership
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert len(response.json().get("conditions_of_sale", [])) == 1, response.json()
    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 1
    assert conditions_of_sale[0].new_ownership == new_ownership
    assert conditions_of_sale[0].old_ownership == old_ownership


@pytest.mark.django_db
def test__api__condition_of_sale__create__has_sales__in_the_past(api_client: HitasAPIClient):
    # given:
    # - An owner with ownerships to one new and two old apartment
    # - the new apartment has apartment sales in the past (apartment is no longer new)
    owner: Owner = OwnerFactory.create()
    new_apartment: Apartment = ApartmentFactory.create(first_purchase_date=None)
    old_apartment: Apartment = ApartmentFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(owner=owner, apartment=new_apartment)
    OwnershipFactory.create(owner=owner, apartment=old_apartment)
    ApartmentSaleFactory.create(
        apartment=new_apartment,
        ownerships=[new_ownership],
        purchase_date=timezone.now() - relativedelta(days=1),
    )

    # when:
    # - New conditions of sale are created for this owner as a household
    data = {"household": [owner.uuid.hex]}
    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.post(url, data=data, format="json")

    # then:
    # - The response contains no conditions of sale
    # - The database contains no conditions of sale
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert len(response.json().get("conditions_of_sale", [])) == 0, response.json()
    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 0


@pytest.mark.django_db
def test__api__condition_of_sale__create__only_one_old_apartment(api_client: HitasAPIClient):
    # given:
    # - An owner with ownerships to a single old apartment
    owner: Owner = OwnerFactory.create()
    old_apartment: Apartment = ApartmentFactory.create()
    OwnershipFactory.create(owner=owner, apartment=old_apartment)

    # when:
    # - New conditions of sale are created for this owner as a household
    data = {"household": [owner.uuid.hex]}
    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.post(url, data=data, format="json")

    # then:
    # - The response contains no conditions of sale
    # - The database contains no conditions of sale
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert len(response.json().get("conditions_of_sale", [])) == 0, response.json()
    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 0


@pytest.mark.django_db
def test__api__condition_of_sale__create__only_one_new_apartment(api_client: HitasAPIClient):
    # given:
    # - An owner with ownerships to a single new apartment
    owner: Owner = OwnerFactory.create()
    new_apartment: Apartment = ApartmentFactory.create(first_purchase_date=None)
    OwnershipFactory.create(owner=owner, apartment=new_apartment)

    # when:
    # - New conditions of sale are created for this owner as a household
    data = {"household": [owner.uuid.hex]}
    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.post(url, data=data, format="json")

    # then:
    # - The response contains no conditions of sale
    # - The database contains no conditions of sale
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert len(response.json().get("conditions_of_sale", [])) == 0, response.json()
    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 0


@pytest.mark.django_db
def test__api__condition_of_sale__create__household_of_two__one_has_new(api_client: HitasAPIClient):
    # given:
    # - Two owners:
    #   - Owner 1 has a single ownership to an old apartment
    #   - Owner 2 has a single ownership to a new apartment
    owner_1: Owner = OwnerFactory.create()
    owner_2: Owner = OwnerFactory.create()
    old_apartment: Apartment = ApartmentFactory.create()
    new_apartment: Apartment = ApartmentFactory.create(first_purchase_date=None)
    old_ownership: Ownership = OwnershipFactory.create(owner=owner_1, apartment=old_apartment)
    new_ownership: Ownership = OwnershipFactory.create(owner=owner_2, apartment=new_apartment)

    # when:
    # - New conditions of sale are created for these two owners as a household
    data = {"household": [owner_1.uuid.hex, owner_2.uuid.hex]}
    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.post(url, data=data, format="json")

    # then:
    # - The response contains a single condition of sale
    # - The database contains a single condition of sale
    # - The condition of sale is between:
    #   - The new ownership of Owner 2 and the old ownership of Owner 1
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert len(response.json().get("conditions_of_sale", [])) == 1, response.json()
    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 1
    assert conditions_of_sale[0].new_ownership == new_ownership
    assert conditions_of_sale[0].old_ownership == old_ownership


@pytest.mark.django_db
def test__api__condition_of_sale__create__household_of_two__both_have_new(api_client: HitasAPIClient):
    # given:
    # - Two owners:
    #   - Owner 1 has an ownership to an old apartment and a new apartment
    #   - Owner 2 has a single ownership to a new apartment
    owner_1: Owner = OwnerFactory.create()
    owner_2: Owner = OwnerFactory.create()
    old_apartment: Apartment = ApartmentFactory.create()
    new_apartment_1: Apartment = ApartmentFactory.create(first_purchase_date=None)
    new_apartment_2: Apartment = ApartmentFactory.create(first_purchase_date=None)
    old_ownership: Ownership = OwnershipFactory.create(owner=owner_1, apartment=old_apartment)
    new_ownership_1: Ownership = OwnershipFactory.create(owner=owner_1, apartment=new_apartment_1)
    new_ownership_2: Ownership = OwnershipFactory.create(owner=owner_2, apartment=new_apartment_2)

    # when:
    # - New conditions of sale are created for these two owners as a household
    data = {"household": [owner_1.uuid.hex, owner_2.uuid.hex]}
    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.post(url, data=data, format="json")

    # then:
    # - The response contains three conditions of sale
    # - The database contains three conditions of sale
    # - The conditions of sale are between:
    #   - The new ownership of Owner 1 and the old ownership of Owner 1
    #   - The new ownership of Owner 1 and the new ownership of Owner 2
    #   - The new ownership of Owner 2 and the old ownership of Owner 1
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert len(response.json().get("conditions_of_sale", [])) == 3, response.json()
    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 3
    assert conditions_of_sale[0].new_ownership == new_ownership_1
    assert conditions_of_sale[0].old_ownership == old_ownership
    assert conditions_of_sale[1].new_ownership == new_ownership_1
    assert conditions_of_sale[1].old_ownership == new_ownership_2
    assert conditions_of_sale[2].new_ownership == new_ownership_2
    assert conditions_of_sale[2].old_ownership == old_ownership


@pytest.mark.django_db
def test__api__condition_of_sale__create__household_of_two__one_has_multiple_new(api_client: HitasAPIClient):
    # given:
    # - Two owners:
    #   - Owner 1 has a single ownership to an old apartment
    #   - Owner 2 has two ownerships to two new apartments
    owner_1: Owner = OwnerFactory.create()
    owner_2: Owner = OwnerFactory.create()
    old_apartment: Apartment = ApartmentFactory.create()
    new_apartment_1: Apartment = ApartmentFactory.create(first_purchase_date=None)
    new_apartment_2: Apartment = ApartmentFactory.create(first_purchase_date=None)
    old_ownership: Ownership = OwnershipFactory.create(owner=owner_1, apartment=old_apartment)
    new_ownership_1: Ownership = OwnershipFactory.create(owner=owner_2, apartment=new_apartment_1)
    new_ownership_2: Ownership = OwnershipFactory.create(owner=owner_2, apartment=new_apartment_2)

    # when:
    # - New conditions of sale are created for these two owners as a household
    data = {"household": [owner_1.uuid.hex, owner_2.uuid.hex]}
    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.post(url, data=data, format="json")

    # then:
    # - The response contains three conditions of sale
    # - The database contains three conditions of sale
    # - The conditions of sale are between:
    #   - The new ownership of Owner 1 and the old ownership of Owner 1
    #   - The new ownership of Owner 1 and the new ownership of Owner 2
    #   - The new ownership of Owner 2 and the old ownership of Owner 1
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert "conditions_of_sale" in response.json(), response.json()
    assert len(response.json().get("conditions_of_sale", [])) == 3, response.json()
    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 3
    assert conditions_of_sale[0].new_ownership == new_ownership_1
    assert conditions_of_sale[0].old_ownership == old_ownership
    assert conditions_of_sale[1].new_ownership == new_ownership_1
    assert conditions_of_sale[1].old_ownership == new_ownership_2
    assert conditions_of_sale[2].new_ownership == new_ownership_2
    assert conditions_of_sale[2].old_ownership == old_ownership


@pytest.mark.django_db
def test__api__condition_of_sale__create__household_of_two__neither_have_new(api_client: HitasAPIClient):
    # given:
    # - Two owners:
    #   - Owner 1 has a single ownership to an old apartment
    #   - Owner 2 has a single ownership to an old apartment
    owner_1: Owner = OwnerFactory.create()
    owner_2: Owner = OwnerFactory.create()
    old_apartment_1: Apartment = ApartmentFactory.create()
    old_apartment_2: Apartment = ApartmentFactory.create()
    OwnershipFactory.create(owner=owner_1, apartment=old_apartment_1)
    OwnershipFactory.create(owner=owner_2, apartment=old_apartment_2)

    # when:
    # - New conditions of sale are created for these two owners as a household
    data = {"household": [owner_1.uuid.hex, owner_2.uuid.hex]}
    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.post(url, data=data, format="json")

    # then:
    # - The response contains no conditions of sale
    # - The database contains no conditions of sale
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert len(response.json().get("conditions_of_sale", [])) == 0, response.json()
    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 0


@pytest.mark.django_db
def test__api__condition_of_sale__create__two_households(api_client: HitasAPIClient):
    # given:
    # - Three owners:
    #   - Owner 1 has a single ownership to an old apartment
    #   - Owner 2 has a single ownership to a new apartment
    #   - Owner 3 has a single ownership to a new apartment
    owner_1: Owner = OwnerFactory.create()
    owner_2: Owner = OwnerFactory.create()
    owner_3: Owner = OwnerFactory.create()
    old_apartment: Apartment = ApartmentFactory.create()
    new_apartment_1: Apartment = ApartmentFactory.create(first_purchase_date=None)
    new_apartment_2: Apartment = ApartmentFactory.create(first_purchase_date=None)
    old_ownership: Ownership = OwnershipFactory.create(owner=owner_1, apartment=old_apartment)
    new_ownership_1: Ownership = OwnershipFactory.create(owner=owner_2, apartment=new_apartment_1)
    new_ownership_2: Ownership = OwnershipFactory.create(owner=owner_3, apartment=new_apartment_2)

    # when:
    # - New conditions of sale are created for Owner 1 and Owner 2 as a household
    data_1 = {"household": [owner_1.uuid.hex, owner_2.uuid.hex]}
    url_1 = reverse("hitas:conditions-of-sale-list")
    response_1 = api_client.post(url_1, data=data_1, format="json")

    # then:
    # - The response contains a single condition of sale
    # - The database contains a single condition of sale
    # - The condition of sale is between:
    #   - The new ownership of Owner 2 and the old ownership of Owner 1
    assert response_1.status_code == status.HTTP_201_CREATED, response_1.json()
    assert len(response_1.json().get("conditions_of_sale", [])) == 1, response_1.json()
    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 1
    assert conditions_of_sale[0].new_ownership == new_ownership_1
    assert conditions_of_sale[0].old_ownership == old_ownership

    # when:
    # - New conditions of sale are created for Owner 1 and Owner 3 as a household
    data_2 = {"household": [owner_1.uuid.hex, owner_3.uuid.hex]}
    url_2 = reverse("hitas:conditions-of-sale-list")
    response_2 = api_client.post(url_2, data=data_2, format="json")

    # then:
    # - The response contains two conditions of sale
    # - The database contains two conditions of sale
    # - The conditions of sale are between:
    #   - The new ownership of Owner 2 and the old ownership of Owner 1  (this was created previously)
    #   - The new ownership of Owner 3 and the old ownership of Owner 1  (this is new)
    assert response_2.status_code == status.HTTP_201_CREATED, response_2.json()
    assert len(response_2.json().get("conditions_of_sale", [])) == 2, response_2.json()
    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 2
    assert conditions_of_sale[0].new_ownership == new_ownership_1
    assert conditions_of_sale[0].old_ownership == old_ownership
    assert conditions_of_sale[1].new_ownership == new_ownership_2
    assert conditions_of_sale[1].old_ownership == old_ownership


@pytest.mark.parametrize(
    **parametrize_helper(
        {
            "Some other string": InvalidInput(
                invalid_data={"household": ["foo"]},
                fields=[{"field": "household.0", "message": "Not a valid UUID hex."}],
            ),
            "Empty String.": InvalidInput(
                invalid_data={"household": [""]},
                fields=[{"field": "household.0", "message": "Not a valid UUID hex."}],
            ),
            "Some other type": InvalidInput(
                invalid_data={"household": [1]},
                fields=[{"field": "household.0", "message": "Not a valid UUID hex."}],
            ),
            "Not a list": InvalidInput(
                invalid_data={"household": "foo"},
                fields=[{"field": "household", "message": 'Expected a list of items but got type "str".'}],
            ),
            "Null value in list": InvalidInput(
                invalid_data={"household": [None]},
                fields=[{"field": "household.0", "message": "This field is mandatory and cannot be null."}],
            ),
            "Null value": InvalidInput(
                invalid_data={"household": None},
                fields=[{"field": "household", "message": "This field is mandatory and cannot be null."}],
            ),
            "Owner not found": InvalidInput(
                invalid_data={"household": ["abb80d36d9ac4e2d969674e3ea573c9b"]},
                fields=[{"field": "household", "message": "Owners not found: 'abb80d36d9ac4e2d969674e3ea573c9b'."}],
            ),
            "Owners not found": InvalidInput(
                invalid_data={"household": ["abb80d36d9ac4e2d969674e3ea573c9b", "d35c2173d2c4481a82155cd80f2bc3c6"]},
                fields=[
                    {
                        "field": "household",
                        "message": (
                            "Owners not found: 'abb80d36d9ac4e2d969674e3ea573c9b', 'd35c2173d2c4481a82155cd80f2bc3c6'."
                        ),
                    }
                ],
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
    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.post(url, data=invalid_data, format="json", openapi_validate_request=False)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": fields,
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__condition_of_sale__create__not_if_flag_set(api_client: HitasAPIClient):
    # given:
    # - An owner with ownerships to one new and one old apartment
    # - Owner set to bypass conditions of sale (e.g. Helsinki city)
    owner: Owner = OwnerFactory.create(bypass_conditions_of_sale=True)
    new_apartment: Apartment = ApartmentFactory.create(first_purchase_date=None)
    old_apartment: Apartment = ApartmentFactory.create()
    OwnershipFactory.create(owner=owner, apartment=new_apartment)
    OwnershipFactory.create(owner=owner, apartment=old_apartment)

    # when:
    # - New conditions of sale are created for this owner as a household
    data = {"household": [owner.uuid.hex]}
    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.post(url, data=data, format="json")

    # then:
    # - The response contains no conditions of sale
    # - The database contains no conditions of sale
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert len(response.json().get("conditions_of_sale", [])) == 0, response.json()
    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 0


# Update tests


class ConditionOfSaleUpdateData(TypedDict):
    grace_period: str


class ConditionOfSaleUpdateArgs(NamedTuple):
    data: ConditionOfSaleUpdateData


@pytest.mark.parametrize(
    **parametrize_helper(
        {
            "Change grace period to three months": ConditionOfSaleUpdateArgs(
                data=ConditionOfSaleUpdateData(
                    grace_period=GracePeriod.THREE_MONTHS.value,
                ),
            ),
            "Change grace period to six months": ConditionOfSaleUpdateArgs(
                data=ConditionOfSaleUpdateData(
                    grace_period=GracePeriod.SIX_MONTHS.value,
                ),
            ),
        },
    ),
)
@pytest.mark.django_db
def test__api__condition_of_sale__update(api_client: HitasAPIClient, data: ConditionOfSaleUpdateData):
    condition_of_sale: ConditionOfSale = ConditionOfSaleFactory.create(grace_period=GracePeriod.NOT_GIVEN)

    url = reverse(
        "hitas:conditions-of-sale-detail",
        kwargs={
            "uuid": condition_of_sale.uuid.hex,
        },
    )
    response = api_client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["grace_period"] == str(data["grace_period"])
    condition_of_sale.refresh_from_db()
    assert condition_of_sale.grace_period.value == str(data["grace_period"])


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
    condition_of_sale: ConditionOfSale = ConditionOfSaleFactory.create(grace_period=GracePeriod.NOT_GIVEN)

    url = reverse(
        "hitas:conditions-of-sale-detail",
        kwargs={
            "uuid": condition_of_sale.uuid.hex,
        },
    )
    response = api_client.put(url, data=invalid_data, format="json", openapi_validate_request=False)
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

    condition_of_sale: ConditionOfSale = ConditionOfSaleFactory.create()

    url = reverse(
        "hitas:conditions-of-sale-detail",
        kwargs={
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
