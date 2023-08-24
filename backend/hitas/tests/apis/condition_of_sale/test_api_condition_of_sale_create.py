import datetime
from typing import Any

import pytest
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from hitas.models.condition_of_sale import ConditionOfSale
from hitas.models.housing_company import HitasType, RegulationStatus
from hitas.models.owner import Owner
from hitas.models.ownership import Ownership
from hitas.tests.apis.helpers import HitasAPIClient, InvalidInput, parametrize_helper
from hitas.tests.factories import (
    ConditionOfSaleFactory,
    OwnerFactory,
    OwnershipFactory,
)


@pytest.mark.django_db
def test__api__condition_of_sale__create__single(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    # given:
    # - An owner with ownerships to one new and one old apartment
    owner: Owner = OwnerFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=None,
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    old_ownership: Ownership = OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )

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
def test__api__condition_of_sale__create__no_ownerships(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

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
def test__api__condition_of_sale__create__no_new_apartments(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    # given:
    # - An owner with no ownerships to new apartments
    owner: Owner = OwnerFactory.create()
    OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )

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
def test__api__condition_of_sale__create__some_already_exist(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    # given:
    # - An owner with ownerships to one new and two old apartment
    # - A condition of sale already exists between one new and old apartment, but not the other
    owner: Owner = OwnerFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=None,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    old_ownership_1: Ownership = OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    old_ownership_2: Ownership = OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
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
def test__api__condition_of_sale__create__all_already_exist(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    # given:
    # - An owner with ownerships to one new and two old apartment
    # - Conditions of sale already exists between the new and both old apartments
    owner: Owner = OwnerFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=None,
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    old_ownership_1: Ownership = OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    old_ownership_2: Ownership = OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
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
def test__api__condition_of_sale__create__has_sales__in_the_future(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    # given:
    # - An owner with ownerships to one new and two old apartment
    # - the new apartment has apartment sales in the future (apartment is still new)
    owner: Owner = OwnerFactory.create()
    new_ownership: Ownership = OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=timezone.now() + relativedelta(days=1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    old_ownership: Ownership = OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
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
def test__api__condition_of_sale__create__has_sales__in_the_past(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    # given:
    # - An owner with ownerships to one new and two old apartment
    # - the new apartment has apartment sales in the past (apartment is no longer new)
    owner: Owner = OwnerFactory.create()
    OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=timezone.now() - relativedelta(days=1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
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
def test__api__condition_of_sale__create__only_one_old_apartment(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    # given:
    # - An owner with ownerships to a single old apartment
    owner: Owner = OwnerFactory.create()
    OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
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
def test__api__condition_of_sale__create__only_one_new_apartment(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    # given:
    # - An owner with ownerships to a single new apartment
    owner: Owner = OwnerFactory.create()
    OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=None,
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
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
def test__api__condition_of_sale__create__household_of_two__one_has_new(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    # given:
    # - Two owners:
    #   - Owner 1 has a single ownership to an old apartment
    #   - Owner 2 has a single ownership to a new apartment
    owner_1: Owner = OwnerFactory.create()
    owner_2: Owner = OwnerFactory.create()
    old_ownership: Ownership = OwnershipFactory.create(
        owner=owner_1,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    new_ownership: Ownership = OwnershipFactory.create(
        owner=owner_2,
        sale__apartment__completion_date=None,
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )

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
def test__api__condition_of_sale__create__household_of_two__both_have_new(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    # given:
    # - Two owners:
    #   - Owner 1 has an ownership to an old apartment and a new apartment
    #   - Owner 2 has a single ownership to a new apartment
    owner_1: Owner = OwnerFactory.create()
    owner_2: Owner = OwnerFactory.create()
    old_ownership: Ownership = OwnershipFactory.create(
        owner=owner_1,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    new_ownership_1: Ownership = OwnershipFactory.create(
        owner=owner_1,
        sale__apartment__completion_date=None,
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    new_ownership_2: Ownership = OwnershipFactory.create(
        owner=owner_2,
        sale__apartment__completion_date=None,
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )

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
def test__api__condition_of_sale__create__household_of_two__one_has_multiple_new(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    # given:
    # - Two owners:
    #   - Owner 1 has a single ownership to an old apartment
    #   - Owner 2 has two ownerships to two new apartments
    owner_1: Owner = OwnerFactory.create()
    owner_2: Owner = OwnerFactory.create()
    old_ownership: Ownership = OwnershipFactory.create(
        owner=owner_1,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    new_ownership_1: Ownership = OwnershipFactory.create(
        owner=owner_2,
        sale__apartment__completion_date=None,
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    new_ownership_2: Ownership = OwnershipFactory.create(
        owner=owner_2,
        sale__apartment__completion_date=None,
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )

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
def test__api__condition_of_sale__create__household_of_two__neither_have_new(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    # given:
    # - Two owners:
    #   - Owner 1 has a single ownership to an old apartment
    #   - Owner 2 has a single ownership to an old apartment
    owner_1: Owner = OwnerFactory.create()
    owner_2: Owner = OwnerFactory.create()
    OwnershipFactory.create(
        owner=owner_1,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    OwnershipFactory.create(
        owner=owner_2,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )

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
def test__api__condition_of_sale__create__household_of_two__same_new_apartment(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    # given:
    # - Two owners:
    #   - Owner 1 has an ownership to an old apartment and a new apartment
    #   - Owner 2 has an ownership to the same new apartment
    owner_1: Owner = OwnerFactory.create()
    owner_2: Owner = OwnerFactory.create()
    owner_1_old_ownership: Ownership = OwnershipFactory.create(
        owner=owner_1,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        sale__purchase_date=datetime.date(2022, 1, 1),
    )
    owner_1_new_ownership: Ownership = OwnershipFactory.create(
        owner=owner_1,
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        sale__apartment__completion_date=None,
    )
    owner_2_new_ownership: Ownership = OwnershipFactory.create(
        owner=owner_2,
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        sale__apartment=owner_1_new_ownership.sale.apartment,
    )

    # when:
    # - New conditions of sale are created for these two owners as a household
    data = {"household": [owner_1.uuid.hex, owner_2.uuid.hex]}
    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.post(url, data=data, format="json")

    # then:
    # - The response contains two conditions of sale
    # - The database contains two condition of sale
    # - The conditions of sale are between:
    #   - The new ownership of Owner 1 and the old ownership of Owner 1
    #   - The new ownership of Owner 2 and the old ownership of Owner 1
    # - There is not an ownership between the two new ownerships to the same apartment
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert len(response.json().get("conditions_of_sale", [])) == 2, response.json()
    conditions_of_sale: list[ConditionOfSale] = list(ConditionOfSale.objects.all())
    assert len(conditions_of_sale) == 2
    assert conditions_of_sale[0].new_ownership == owner_1_new_ownership
    assert conditions_of_sale[0].old_ownership == owner_1_old_ownership
    assert conditions_of_sale[1].new_ownership == owner_2_new_ownership
    assert conditions_of_sale[1].old_ownership == owner_1_old_ownership


@pytest.mark.django_db
def test__api__condition_of_sale__create__two_households(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    # given:
    # - Three owners:
    #   - Owner 1 has a single ownership to an old apartment
    #   - Owner 2 has a single ownership to a new apartment
    #   - Owner 3 has a single ownership to a new apartment
    owner_1: Owner = OwnerFactory.create()
    owner_2: Owner = OwnerFactory.create()
    owner_3: Owner = OwnerFactory.create()
    old_ownership: Ownership = OwnershipFactory.create(
        owner=owner_1,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    new_ownership_1: Ownership = OwnershipFactory.create(
        owner=owner_2,
        sale__apartment__completion_date=None,
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    new_ownership_2: Ownership = OwnershipFactory.create(
        owner=owner_3,
        sale__apartment__completion_date=None,
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )

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
def test__api__condition_of_sale__create__not_if_flag_set(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    # given:
    # - An owner with ownerships to one new and one old apartment
    # - Owner set to bypass conditions of sale (e.g. Helsinki city)
    owner: Owner = OwnerFactory.create(bypass_conditions_of_sale=True)
    OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=None,
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
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
def test__api__condition_of_sale__create__apartment_new_due_to_condition_of_sale(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    # given:
    # - An owner with ownerships to two new apartments and one old apartment
    # - One new apartment is completed and the other is not
    # - There is already a condition of sale between the completed new apartment and the old apartment
    owner: Owner = OwnerFactory.create()
    new_ownership_1: Ownership = OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    new_ownership_2: Ownership = OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=None,
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    old_ownership: Ownership = OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    ConditionOfSaleFactory.create(new_ownership=new_ownership_1, old_ownership=old_ownership)

    # when:
    # - New conditions of sale are created for this owner as a household
    data = {"household": [owner.uuid.hex]}
    url = reverse("hitas:conditions-of-sale-list")
    response = api_client.post(url, data=data, format="json")

    # then:
    # - The response contains three conditions of sale
    # - The database contains three conditions of sale
    # - The conditions of sale are between old ownership and the two new ownerships
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
def test__api__condition_of_sale__create__not_if_not_regulated(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    # given:
    # - An owner with ownerships to one new and one old apartment
    # - The old apartment's housing company is not regulated
    owner: Owner = OwnerFactory.create()
    OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=None,
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.RELEASED_BY_HITAS,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
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
def test__api__condition_of_sale__create__not_to_half_hitas(api_client: HitasAPIClient, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    # given:
    # - An owner with ownerships to one new half-hitas apartment and one old non-half-hitas apartment
    owner: Owner = OwnerFactory.create()
    OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=None,
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.HALF_HITAS,
    )
    OwnershipFactory.create(
        owner=owner,
        sale__apartment__completion_date=datetime.date(2022, 1, 1),
        sale__purchase_date=datetime.date(2022, 1, 1),
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
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
