import pytest
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status

from hitas.models import ApartmentType, BuildingType, Developer, FinancingMethod
from hitas.tests import factories
from hitas.tests.apis.helpers import HitasAPIClient

_code_parameters = (
    "url_basename,model,factory",
    [
        ("financing-method", FinancingMethod, factories.OldHitasFinancingMethodFactory),
        ("building-type", BuildingType, factories.BuildingTypeFactory),
        ("developer", Developer, factories.DeveloperFactory),
        ("apartment-type", ApartmentType, factories.ApartmentTypeFactory),
    ],
)

# List tests


@pytest.mark.parametrize(*_code_parameters)
@pytest.mark.django_db
def test__api__codes__list__empty(api_client: HitasAPIClient, url_basename, model, factory):
    response = api_client.get(reverse(f"hitas:{url_basename}-list"))
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


@pytest.mark.parametrize(*_code_parameters)
@pytest.mark.django_db
def test__api__code__list(api_client: HitasAPIClient, url_basename, model, factory):
    code1 = factory.create(value="1", order=2)
    code2 = factory.create(value="2", order=1)

    url = reverse(f"hitas:{url_basename}-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "id": code2.uuid.hex,
            "value": code2.value,
            "description": code2.description,
            "code": code2.legacy_code_number,
        },
        {
            "id": code1.uuid.hex,
            "value": code1.value,
            "description": code1.description,
            "code": code1.legacy_code_number,
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


# Retrieve tests


@pytest.mark.parametrize(*_code_parameters)
@pytest.mark.django_db
def test__api__code__retrieve(api_client: HitasAPIClient, url_basename, model, factory):
    code = factory.create()

    url = reverse(f"hitas:{url_basename}-detail", kwargs={"uuid": code.uuid.hex})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": code.uuid.hex,
        "value": code.value,
        "description": code.description,
        "code": code.legacy_code_number,
    }


@pytest.mark.parametrize(*_code_parameters)
@pytest.mark.django_db
def test__api__code__retrieve__invalid_id(api_client: HitasAPIClient, url_basename, model, factory):
    factory.create()

    url = reverse(f"hitas:{url_basename}-detail", kwargs={"uuid": "foo"})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert {
        "error": f'{url_basename.replace("-", "_")}_not_found',
        "message": f'{url_basename.capitalize().replace("-", " ")} not found',
        "reason": "Not Found",
        "status": 404,
    } == response.json()


# Create tests


@pytest.mark.parametrize(*_code_parameters)
@pytest.mark.django_db
def test__api__code__create(api_client: HitasAPIClient, url_basename, model, factory):
    data = {
        "value": "Code Value",
        "description": "Code description",
        "code": "123",
    }

    url = reverse(f"hitas:{url_basename}-list")
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()

    url = reverse(f"hitas:{url_basename}-detail", kwargs={"uuid": model.objects.first().uuid.hex})
    get_response = api_client.get(url)
    assert response.json() == get_response.json()


@pytest.mark.parametrize(*_code_parameters)
@pytest.mark.parametrize(
    "invalid_data",
    [
        {"code": None},
        {"description": None},
    ],
)
@pytest.mark.django_db
def test__api__code__create__invalid_data(api_client: HitasAPIClient, url_basename, model, factory, invalid_data):
    data = {
        "value": "Code Value",
        "description": "Code description",
        "code": "123",
    }
    data.update(invalid_data)

    url = reverse(f"hitas:{url_basename}-list")
    response = api_client.post(url, data=data, format="json", openapi_validate_request=False)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()


# Update tests


@pytest.mark.parametrize(*_code_parameters)
@pytest.mark.django_db
def test__api__code__update(api_client: HitasAPIClient, url_basename, model, factory):
    code = factory.create()
    data = {
        "value": "Code Value",
        "description": "Code description",
        "code": "123",
    }

    url = reverse(f"hitas:{url_basename}-detail", kwargs={"uuid": code.uuid.hex})
    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": code.uuid.hex,
        "value": data["value"],
        "description": data["description"],
        "code": data["code"],
    }

    get_response = api_client.get(url)
    assert response.json() == get_response.json()


# Delete tests


@pytest.mark.parametrize(*_code_parameters)
@pytest.mark.django_db
def test__api__code__delete(api_client: HitasAPIClient, url_basename, model, factory):
    code = factory.create()

    url = reverse(f"hitas:{url_basename}-detail", kwargs={"uuid": code.uuid.hex})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()

    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


# Filter tests


@pytest.mark.parametrize(*_code_parameters)
@pytest.mark.parametrize(
    "selected_filter,result_count",
    [
        [{"value": "TestN"}, 1],
        [{"value": "testn"}, 1],
    ],
)
@pytest.mark.django_db
def test__api__code__filter(api_client: HitasAPIClient, url_basename, model, factory, selected_filter, result_count):
    factory.create(legacy_code_number="111", value="TestName")
    factory.create(legacy_code_number="113", value="123")

    url = reverse(f"hitas:{url_basename}-list") + "?" + urlencode(selected_filter)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == result_count, response.json()
