from typing import NamedTuple, TypedDict

import pytest
from django.urls import reverse
from rest_framework import status

from hitas.models.condition_of_sale import ConditionOfSale, GracePeriod
from hitas.tests.apis.helpers import HitasAPIClient, InvalidInput, parametrize_helper
from hitas.tests.factories import (
    ConditionOfSaleFactory,
)


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
