import pytest
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status

from hitas.models import Building, HousingCompany, RealEstate
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import BuildingFactory, HousingCompanyFactory, RealEstateFactory

# List tests


@pytest.mark.django_db
def test__api__real_estate__list__empty(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()

    url = reverse("hitas:real-estate-list", kwargs={"housing_company_uuid": hc.uuid.hex})
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
def test__api__real_estate__list(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    re1: RealEstate = RealEstateFactory.create(housing_company=hc)
    re2: RealEstate = RealEstateFactory.create(housing_company=hc)
    bu1: Building = BuildingFactory.create(real_estate=re1)
    bu2: Building = BuildingFactory.create(real_estate=re1)
    BuildingFactory.create()  # Another Housing Company etc.

    url = reverse("hitas:real-estate-list", kwargs={"housing_company_uuid": hc.uuid.hex})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "id": re1.uuid.hex,
            "address": {
                "city": "Helsinki",
                "postal_code": re1.postal_code.value,
                "street_address": re1.street_address,
            },
            "property_identifier": re1.property_identifier,
            "buildings": [
                {
                    "id": bu1.uuid.hex,
                    "address": {
                        "city": "Helsinki",
                        "postal_code": bu1.postal_code.value,
                        "street_address": bu1.street_address,
                    },
                    "building_identifier": bu1.building_identifier,
                },
                {
                    "id": bu2.uuid.hex,
                    "address": {
                        "city": "Helsinki",
                        "postal_code": bu2.postal_code.value,
                        "street_address": bu2.street_address,
                    },
                    "building_identifier": bu2.building_identifier,
                },
            ],
        },
        {
            "id": re2.uuid.hex,
            "address": {
                "city": "Helsinki",
                "postal_code": re2.postal_code.value,
                "street_address": re2.street_address,
            },
            "property_identifier": re2.property_identifier,
            "buildings": [],
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
def test__api__real_estate__list__invalid_housing_company(api_client: HitasAPIClient):
    RealEstateFactory.create()

    url = reverse("hitas:real-estate-list", kwargs={"housing_company_uuid": "foo"})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


# Retrieve tests


@pytest.mark.django_db
def test__api__real_estate__retrieve(api_client: HitasAPIClient):
    hc1: HousingCompany = HousingCompanyFactory.create()
    hc1_re1: RealEstate = RealEstateFactory.create(housing_company=hc1)
    hc1_re1_bu1: Building = BuildingFactory.create(real_estate=hc1_re1)
    hc1_re1_bu2: Building = BuildingFactory.create(real_estate=hc1_re1)

    # Second RealEstate in the same HousingCompany
    BuildingFactory.create(real_estate__housing_company=hc1)

    # Second HousingCompany with a building
    BuildingFactory.create()

    url = reverse("hitas:real-estate-detail", kwargs={"housing_company_uuid": hc1.uuid.hex, "uuid": hc1_re1.uuid.hex})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": hc1_re1.uuid.hex,
        "address": {
            "city": "Helsinki",
            "postal_code": hc1_re1.postal_code.value,
            "street_address": hc1_re1.street_address,
        },
        "property_identifier": hc1_re1.property_identifier,
        "buildings": [
            {
                "id": hc1_re1_bu1.uuid.hex,
                "address": {
                    "city": "Helsinki",
                    "postal_code": hc1_re1_bu1.postal_code.value,
                    "street_address": hc1_re1_bu1.street_address,
                },
                "building_identifier": hc1_re1_bu1.building_identifier,
            },
            {
                "id": hc1_re1_bu2.uuid.hex,
                "address": {
                    "city": "Helsinki",
                    "postal_code": hc1_re1_bu2.postal_code.value,
                    "street_address": hc1_re1_bu2.street_address,
                },
                "building_identifier": hc1_re1_bu2.building_identifier,
            },
        ],
    }


@pytest.mark.django_db
def test__api__real_estate__retrieve__invalid_real_estate(api_client: HitasAPIClient):
    re: RealEstate = RealEstateFactory.create()

    url = reverse(
        "hitas:real-estate-detail", kwargs={"housing_company_uuid": re.housing_company.uuid.hex, "uuid": "foo"}
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


# Create tests


@pytest.mark.django_db
def test__api__real_estate__create(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    data = {
        "address": {
            "postal_code": hc.postal_code.value,
            "street_address": "test-street-address-1",
        },
        "property_identifier": "1-1234-321-56",
    }

    url = reverse("hitas:real-estate-list", kwargs={"housing_company_uuid": hc.uuid.hex})
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()

    re = RealEstate.objects.first()
    url = reverse("hitas:real-estate-detail", kwargs={"housing_company_uuid": hc.uuid.hex, "uuid": re.uuid.hex})
    get_response = api_client.get(url)
    assert response.json() == get_response.json()


@pytest.mark.django_db
def test__api__real_estate__create__invalid_property_identifier(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    data = {
        "address": {
            "postal_code": hc.postal_code.value,
            "street_address": "test-street-address-1",
        },
        "property_identifier": "1-1234-321-56-a",
    }

    url = reverse("hitas:real-estate-list", kwargs={"housing_company_uuid": hc.uuid.hex})
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()


# Update tests


@pytest.mark.django_db
def test__api__real_estate__update(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    re: RealEstate = RealEstateFactory.create(housing_company=hc)
    data = {
        "address": {
            "postal_code": hc.postal_code.value,
            "street_address": "test-street-address-1",
        },
        "property_identifier": "1111-1111-1111-1111",
    }

    url = reverse("hitas:real-estate-detail", kwargs={"housing_company_uuid": hc.uuid.hex, "uuid": re.uuid.hex})
    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": re.uuid.hex,
        "address": {
            "city": "Helsinki",
            "postal_code": data["address"]["postal_code"],
            "street_address": data["address"]["street_address"],
        },
        "property_identifier": data["property_identifier"],
        "buildings": [],
    }

    get_response = api_client.get(url)
    assert response.json() == get_response.json()


# Delete tests


@pytest.mark.django_db
def test__api__real_estate__delete(api_client: HitasAPIClient):
    re: RealEstate = RealEstateFactory.create()

    url = reverse(
        "hitas:real-estate-detail", kwargs={"housing_company_uuid": re.housing_company.uuid.hex, "uuid": re.uuid.hex}
    )
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()

    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


# Filter tests


@pytest.mark.parametrize(
    "selected_filter",
    [
        {"property_identifier": "1-1234-321-56"},
        {"property_identifier": "1-1234-"},
        {"property_identifier": "321-56"},
        {"street_address": "test-street"},
        {"postal_code": "99999"},
    ],
)
@pytest.mark.django_db
def test__api__real_estate__filter(api_client: HitasAPIClient, selected_filter):
    re: RealEstate = RealEstateFactory.create(property_identifier="1-1234-321-56")
    RealEstateFactory.create(street_address="test-street", housing_company=re.housing_company)
    RealEstateFactory.create(postal_code__value="99999", housing_company=re.housing_company)

    url = (
        reverse("hitas:real-estate-list", kwargs={"housing_company_uuid": re.housing_company.uuid.hex})
        + "?"
        + urlencode(selected_filter)
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == 1, response.json()
