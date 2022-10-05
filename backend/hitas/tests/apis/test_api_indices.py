import datetime
from itertools import product

import pytest
from django.urls import reverse
from rest_framework import status

from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories.indices import (
    ConstructionPriceIndexFactory,
    ConstructionPriceIndexPre2005Factory,
    MarketPriceIndexFactory,
    MarketPriceIndexPre2005Factory,
    MaxPriceIndexFactory,
)

_code_parameters = (
    "url_basename,model,factory",
    [
        ("max-price-index", None, MaxPriceIndexFactory),
        ("market-price-index", None, MarketPriceIndexFactory),
        ("market-price-index-pre-2005", None, MarketPriceIndexPre2005Factory),
        ("construction-price-index", None, ConstructionPriceIndexFactory),
        ("construction-price-index-pre-2005", None, ConstructionPriceIndexPre2005Factory),
    ],
)

indices = [
    "max-price-index",
    "market-price-index",
    "market-price-index-pre-2005",
    "construction-price-index",
    "construction-price-index-pre-2005",
]

factories = [
    MaxPriceIndexFactory,
    MarketPriceIndexFactory,
    MarketPriceIndexPre2005Factory,
    ConstructionPriceIndexFactory,
    ConstructionPriceIndexPre2005Factory,
]

# List tests


@pytest.mark.parametrize("index", indices)
@pytest.mark.django_db
def test__api__indices__list__empty(api_client: HitasAPIClient, index):
    response = api_client.get(reverse(f"hitas:{index}-list"))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "contents": [],
        "page": {
            "size": 0,
            "current_page": 1,
            "total_items": 0,
            "total_pages": 1,
            "links": {
                "next": None,
                "previous": None,
            },
        },
    }


@pytest.mark.parametrize("index,factory", zip(indices, factories))
@pytest.mark.django_db
def test__api__indices__list(api_client: HitasAPIClient, index, factory):
    factory.create(month=datetime.date(2022, 1, 1), value=127.48)
    factory.create(month=datetime.date(1999, 12, 1), value=256)

    response = api_client.get(reverse(f"hitas:{index:}-list"))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "contents": [
            {"month": "1999-12", "value": 256},
            {"month": "2022-01", "value": 127.48},
        ],
        "page": {
            "size": 2,
            "current_page": 1,
            "total_items": 2,
            "total_pages": 1,
            "links": {
                "next": None,
                "previous": None,
            },
        },
    }


# Create


@pytest.mark.parametrize("index", indices)
@pytest.mark.django_db
def test__api__indices__create(api_client: HitasAPIClient, index):
    response = api_client.post(reverse(f"hitas:{index}-list"), data={}, openapi_validate=False)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED, response.json()
    assert response.json() == {
        "error": "method_not_allowed",
        "message": "Method not allowed",
        "reason": "Method Not Allowed",
        "status": 405,
    }


# Read


@pytest.mark.parametrize("index,factory", zip(indices, factories))
@pytest.mark.django_db
def test__api__indices__retrieve(api_client: HitasAPIClient, index, factory):
    factory.create(month=datetime.date(2022, 1, 1), value=127.48)

    response = api_client.get(reverse(f"hitas:{index}-detail", kwargs={"month": "2022-01"}))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "month": "2022-01",
        "value": 127.48,
    }


@pytest.mark.parametrize("index", indices)
@pytest.mark.django_db
def test__api__indices__retrieve__unexisting_valid_month(api_client: HitasAPIClient, index):
    response = api_client.get(reverse(f"hitas:{index}-detail", kwargs={"month": "2022-01"}))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "month": "2022-01",
        "value": None,
    }


@pytest.mark.parametrize("index,month", product(indices, ["foo", "", "0-1", "2022-1", "2022-13", "2022-00"]))
@pytest.mark.django_db
def test__api__indices__retrieve__invalid_month(api_client: HitasAPIClient, index, month):
    response = api_client.get(reverse(f"hitas:{index}-detail", kwargs={"month": "foo"}), openapi_validate_request=False)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "month",
                "message": "Field has to be a valid month in format 'yyyy-mm'.",
            }
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


# Update


@pytest.mark.parametrize(
    "index_and_factory,create,value", product(zip(indices, factories), [True, False], [None, 1, 1.12])
)
@pytest.mark.django_db
def test__api__indices__update(api_client: HitasAPIClient, index_and_factory, create, value):
    index, factory = index_and_factory[0], index_and_factory[1]

    if create:
        factory.create(month=datetime.date(2022, 1, 1), value=127.48)

    response = api_client.put(
        reverse(f"hitas:{index}-detail", kwargs={"month": "2022-01"}), data={"value": value}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "month": "2022-01",
        "value": value,
    }

    # Fetch and recheck
    response = api_client.get(reverse(f"hitas:{index}-detail", kwargs={"month": "2022-01"}))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "month": "2022-01",
        "value": value,
    }


@pytest.mark.parametrize("index,factory", zip(indices, factories))
@pytest.mark.django_db
def test__api__indices__update__too_many_decimal_points(api_client: HitasAPIClient, index, factory):
    factory.create(month=datetime.date(2022, 1, 1), value=127.48)

    response = api_client.put(
        reverse(f"hitas:{index}-detail", kwargs={"month": "2022-01"}), data={"value": 987.654}, format="json"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "value",
                "message": "Ensure that there are no more than 2 decimal places.",
            }
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


# Delete


@pytest.mark.parametrize("index", indices)
@pytest.mark.django_db
def test__api__indices__delete(api_client: HitasAPIClient, index):
    response = api_client.delete(reverse(f"hitas:{index}-detail", kwargs={"month": "2022-01"}), openapi_validate=False)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert response.json() == {
        "error": "method_not_allowed",
        "message": "Method not allowed",
        "reason": "Method Not Allowed",
        "status": 405,
    }
