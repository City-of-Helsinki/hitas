from datetime import date

import pytest
from django.urls import reverse
from rest_framework import status

from hitas import exceptions
from hitas.models import Building, HousingCompany
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import BuildingFactory, HousingCompanyFactory


@pytest.mark.django_db
def test__api__housing_company__list__empty(api_client: HitasAPIClient):
    response = api_client.get(reverse("hitas:housing-company-list"))
    assert response.status_code == status.HTTP_200_OK
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
def test__api__housing_company__list(api_client: HitasAPIClient):
    hc1: HousingCompany = HousingCompanyFactory.create()
    hc2: HousingCompany = HousingCompanyFactory.create()
    BuildingFactory.create(real_estate__housing_company=hc1, completion_date=date(2020, 1, 1))
    bu2: Building = BuildingFactory.create(real_estate__housing_company=hc1, completion_date=date(2000, 1, 1))

    response = api_client.get(reverse("hitas:housing-company-list"))
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["contents"] == [
        {
            "id": hc1.uuid.hex,
            "name": hc1.display_name,
            "state": hc1.state.name.lower(),
            "address": {
                "street": hc1.street_address,
                "postal_code": hc1.postal_code.value,
                "city": "Helsinki",
            },
            "area": {"name": hc1.postal_code.description, "cost_area": hc1.area},
            "date": str(bu2.completion_date),
        },
        {
            "id": hc2.uuid.hex,
            "name": hc2.display_name,
            "state": hc2.state.name.lower(),
            "address": {
                "street": hc2.street_address,
                "postal_code": hc2.postal_code.value,
                "city": "Helsinki",
            },
            "area": {"name": hc2.postal_code.description, "cost_area": hc2.area},
            "date": None,
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
def test__api__housing_company__list__paging(api_client: HitasAPIClient):
    HousingCompanyFactory.create_batch(size=45)

    response = api_client.get(reverse("hitas:housing-company-list"))
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["page"] == {
        "size": 10,
        "current_page": 1,
        "total_items": 45,
        "total_pages": 5,
        "links": {
            "next": "http://testserver/api/v1/housing-companies?page=2",
            "previous": None,
        },
    }

    # Make the second page request
    response = api_client.get(reverse("hitas:housing-company-list"), {"page": 2})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["page"] == {
        "size": 10,
        "current_page": 2,
        "total_items": 45,
        "total_pages": 5,
        "links": {
            "next": "http://testserver/api/v1/housing-companies?page=3",
            "previous": "http://testserver/api/v1/housing-companies",
        },
    }

    # Make the last page request
    response = api_client.get(reverse("hitas:housing-company-list"), {"page": 5})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["page"] == {
        "size": 5,
        "current_page": 5,
        "total_items": 45,
        "total_pages": 5,
        "links": {
            "next": None,
            "previous": "http://testserver/api/v1/housing-companies?page=4",
        },
    }


@pytest.mark.parametrize("page_number", ["a", "#", " ", ""])
@pytest.mark.django_db
def test__api__housing_company__list__paging__invalid(api_client: HitasAPIClient, page_number):
    response = api_client.get(reverse("hitas:housing-company-list"), {"page": page_number})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == exceptions.InvalidPage().data


@pytest.mark.django_db
def test__api__housing_company__list__paging__too_high(api_client: HitasAPIClient):
    response = api_client.get(reverse("hitas:housing-company-list"), {"page": 2})
    assert response.status_code == status.HTTP_200_OK
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
