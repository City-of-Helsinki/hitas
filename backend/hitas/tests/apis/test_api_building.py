import uuid

import pytest
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status

from hitas.models import Apartment, Building, HousingCompany, RealEstate
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import (
    ApartmentFactory,
    BuildingFactory,
    HousingCompanyFactory,
    OwnershipFactory,
    RealEstateFactory,
)

# List tests


@pytest.mark.django_db
def test__api__building__list__empty(api_client: HitasAPIClient):
    re: RealEstate = RealEstateFactory.create()

    url = reverse(
        "hitas:building-list",
        kwargs={"housing_company_uuid": re.housing_company.uuid.hex, "real_estate_uuid": re.uuid.hex},
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
def test__api__building__list(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    re1: RealEstate = RealEstateFactory.create(housing_company=hc)
    re2: RealEstate = RealEstateFactory.create(housing_company=hc)
    bu1: Building = BuildingFactory.create(real_estate=re1)
    bu2: Building = BuildingFactory.create(real_estate=re1)
    BuildingFactory.create(real_estate=re2)

    url = reverse(
        "hitas:building-list",
        kwargs={"housing_company_uuid": hc.uuid.hex, "real_estate_uuid": re1.uuid.hex},
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "id": bu1.uuid.hex,
            "address": {
                "city": "Helsinki",
                "postal_code": bu1.real_estate.housing_company.postal_code.value,
                "street_address": bu1.street_address,
            },
            "building_identifier": bu1.building_identifier,
        },
        {
            "id": bu2.uuid.hex,
            "address": {
                "city": "Helsinki",
                "postal_code": bu2.real_estate.housing_company.postal_code.value,
                "street_address": bu2.street_address,
            },
            "building_identifier": bu2.building_identifier,
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
def test__api__building__list__invalid_real_estate(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    BuildingFactory.create(real_estate__housing_company=hc)

    url = reverse(
        "hitas:building-list",
        kwargs={"housing_company_uuid": hc.uuid.hex, "real_estate_uuid": "bar"},
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


# Retrieve tests


@pytest.mark.django_db
def test__api__building__retrieve(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    re: RealEstate = RealEstateFactory.create(housing_company=hc)
    bu1: Building = BuildingFactory.create(real_estate=re)

    url = reverse(
        "hitas:building-detail",
        kwargs={"housing_company_uuid": hc.uuid.hex, "real_estate_uuid": re.uuid.hex, "uuid": bu1.uuid.hex},
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": bu1.uuid.hex,
        "address": {
            "city": "Helsinki",
            "postal_code": bu1.real_estate.housing_company.postal_code.value,
            "street_address": bu1.street_address,
        },
        "building_identifier": bu1.building_identifier,
    }


@pytest.mark.django_db
def test__api__building__retrieve__invalid_housing_company_id(api_client: HitasAPIClient):
    hc1: HousingCompany = HousingCompanyFactory.create()
    re: RealEstate = RealEstateFactory.create(housing_company=hc1)
    bu1: Building = BuildingFactory.create(real_estate=re)

    url = reverse(
        "hitas:building-detail",
        kwargs={"housing_company_uuid": uuid.uuid4().hex, "real_estate_uuid": re.uuid.hex, "uuid": bu1.uuid.hex},
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "housing_company_not_found",
        "message": "Housing company not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__building__retrieve__invalid_real_estate_id(api_client: HitasAPIClient):
    hc1: HousingCompany = HousingCompanyFactory.create()
    hc2: HousingCompany = HousingCompanyFactory.create()
    re1: RealEstate = RealEstateFactory.create(housing_company=hc1)
    re2: RealEstate = RealEstateFactory.create(housing_company=hc2)
    bu1: Building = BuildingFactory.create(real_estate=re1)

    url = reverse(
        "hitas:building-detail",
        kwargs={"housing_company_uuid": hc1.uuid.hex, "real_estate_uuid": re2.uuid.hex, "uuid": bu1.uuid.hex},
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "real_estate_not_found",
        "message": "Real estate not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__building__retrieve__invalid_building_id(api_client: HitasAPIClient):
    hc1: HousingCompany = HousingCompanyFactory.create()
    hc2: HousingCompany = HousingCompanyFactory.create()
    re1: RealEstate = RealEstateFactory.create(housing_company=hc1)
    re2: RealEstate = RealEstateFactory.create(housing_company=hc2)
    Building = BuildingFactory.create(real_estate=re1)
    bu2: Building = BuildingFactory.create(real_estate=re2)

    url = reverse(
        "hitas:building-detail",
        kwargs={"housing_company_uuid": hc1.uuid.hex, "real_estate_uuid": re1.uuid.hex, "uuid": bu2.uuid.hex},
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "building_not_found",
        "message": "Building not found",
        "reason": "Not Found",
        "status": 404,
    }


# Create tests


@pytest.mark.parametrize("building_identifier", ["100012345A", "1-1234-321-56 A 111"])
@pytest.mark.django_db
def test__api__building__create(api_client: HitasAPIClient, building_identifier):
    hc: HousingCompany = HousingCompanyFactory.create()
    re: RealEstate = RealEstateFactory.create(housing_company=hc)

    data = {
        "address": {
            "street_address": "test-street-address-1",
        },
    }

    url = reverse(
        "hitas:building-list",
        kwargs={"housing_company_uuid": hc.uuid.hex, "real_estate_uuid": re.uuid.hex},
    )
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()

    bu = Building.objects.first()
    url = reverse(
        "hitas:building-detail",
        kwargs={"housing_company_uuid": hc.uuid.hex, "real_estate_uuid": re.uuid.hex, "uuid": bu.uuid.hex},
    )
    get_response = api_client.get(url)
    assert response.json() == get_response.json()


@pytest.mark.django_db
def test__api__building__create__no_building_identifier(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    re: RealEstate = RealEstateFactory.create(housing_company=hc)
    data = {
        "address": {
            "postal_code": re.housing_company.postal_code.value,
            "street_address": "test-street-address-1",
        },
    }

    url = reverse(
        "hitas:building-list",
        kwargs={"housing_company_uuid": hc.uuid.hex, "real_estate_uuid": re.uuid.hex},
    )
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()

    bu = Building.objects.first()
    assert bu.building_identifier is None
    url = reverse(
        "hitas:building-detail",
        kwargs={"housing_company_uuid": hc.uuid.hex, "real_estate_uuid": re.uuid.hex, "uuid": bu.uuid.hex},
    )
    get_response = api_client.get(url)
    assert response.json() == get_response.json()


@pytest.mark.parametrize("building_identifier", ["foo", None])
@pytest.mark.django_db
def test__api__building__create__invalid_building_identifier(api_client: HitasAPIClient, building_identifier):
    re: RealEstate = RealEstateFactory.create()
    data = {
        "address": {
            "postal_code": re.postal_code.value,
            "street_address": "test-street-address-1",
        },
        "building_identifier": building_identifier,
    }

    url = reverse(
        "hitas:building-list",
        kwargs={"housing_company_uuid": re.housing_company.uuid.hex, "real_estate_uuid": re.uuid.hex},
    )
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()


@pytest.mark.django_db
def test__api__building__create__invalid_real_estate(api_client: HitasAPIClient):
    re: RealEstate = RealEstateFactory.create()
    data = {
        "address": {
            "postal_code": re.postal_code.value,
            "street_address": "test-street-address-1",
        },
        "building_identifier": "100012345A",
    }

    url = reverse(
        "hitas:building-list",
        kwargs={"housing_company_uuid": re.housing_company.uuid.hex, "real_estate_uuid": "foo"},
    )
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


# Update tests


@pytest.mark.django_db
def test__api__building__update(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    re: RealEstate = RealEstateFactory.create(housing_company=hc)
    bu: Building = BuildingFactory.create(real_estate=re)

    data = {
        "address": {
            "postal_code": re.postal_code.value,
            "street_address": "test-street-address-1",
        },
        "building_identifier": "100012345A",
    }

    url = reverse(
        "hitas:building-detail",
        kwargs={"housing_company_uuid": hc.uuid.hex, "real_estate_uuid": re.uuid.hex, "uuid": bu.uuid.hex},
    )
    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": bu.uuid.hex,
        "address": {
            "city": "Helsinki",
            "postal_code": data["address"]["postal_code"],
            "street_address": data["address"]["street_address"],
        },
        "building_identifier": data["building_identifier"],
    }

    get_response = api_client.get(url)
    assert response.json() == get_response.json()


# Delete tests


@pytest.mark.django_db
def test__api__building__delete(api_client: HitasAPIClient):
    bu: Building = BuildingFactory.create()

    url = reverse(
        "hitas:building-detail",
        kwargs={
            "housing_company_uuid": bu.real_estate.housing_company.uuid.hex,
            "real_estate_uuid": bu.real_estate.uuid.hex,
            "uuid": bu.uuid.hex,
        },
    )
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()

    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


@pytest.mark.django_db
def test__api__building__delete__with_references(api_client: HitasAPIClient):
    bu: Building = BuildingFactory.create()
    a: Apartment = ApartmentFactory.create(building=bu)
    OwnershipFactory.create(apartment=a)

    url = reverse(
        "hitas:building-detail",
        kwargs={
            "housing_company_uuid": bu.real_estate.housing_company.uuid.hex,
            "real_estate_uuid": bu.real_estate.uuid.hex,
            "uuid": bu.uuid.hex,
        },
    )
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()

    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


# Filter tests


@pytest.mark.parametrize(
    "selected_filter",
    [
        {"building_identifier": "100012345"},
        {"building_identifier": "1000"},
        {"building_identifier": "12345"},
        {"street_address": "test-street"},
    ],
)
@pytest.mark.django_db
def test__api__building__filter(api_client: HitasAPIClient, selected_filter):
    bu: Building = BuildingFactory.create()
    BuildingFactory.create(building_identifier="100012345A", real_estate=bu.real_estate)
    BuildingFactory.create(street_address="test-street", real_estate=bu.real_estate)

    url = (
        reverse(
            "hitas:building-list",
            kwargs={
                "housing_company_uuid": bu.real_estate.housing_company.uuid.hex,
                "real_estate_uuid": bu.real_estate.uuid.hex,
            },
        )
        + "?"
        + urlencode(selected_filter)
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == 1, response.json()
