import pytest
from django.urls import reverse
from rest_framework import status

from hitas.models import PDFBody
from hitas.models.pdf_body import PDFBodyName
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import PDFBodyFactory

# List tests


@pytest.mark.django_db
def test__api__pdf_body__list__empty(api_client: HitasAPIClient):
    url = reverse("hitas:pdf-body-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == []


@pytest.mark.django_db
def test__api__pdf_body__list(api_client: HitasAPIClient):
    body_1: PDFBody = PDFBodyFactory.create(name=PDFBodyName.CONFIRMED_MAX_PRICE_CALCULATION)
    body_2: PDFBody = PDFBodyFactory.create(name=PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION)
    url = reverse("hitas:pdf-body-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "name": body_1.name.value,
            "texts": body_1.texts,
        },
        {
            "name": body_2.name.value,
            "texts": body_2.texts,
        },
    ]


# Create tests


@pytest.mark.django_db
def test__api__pdf_body__create__unconfirmed_max_price(api_client: HitasAPIClient):
    data = {
        "name": PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION.value,
        "texts": ["text 1", "text 2", "text 3"],
    }

    url = reverse("hitas:pdf-body-list")
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert response.json() == {
        "name": data["name"],
        "texts": data["texts"],
    }


@pytest.mark.django_db
def test__api__pdf_body__create__confirmed_max_price(api_client: HitasAPIClient):
    data = {
        "name": PDFBodyName.CONFIRMED_MAX_PRICE_CALCULATION.value,
        "texts": ["text 1"],
    }

    url = reverse("hitas:pdf-body-list")
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert response.json() == {
        "name": data["name"],
        "texts": data["texts"],
    }


@pytest.mark.django_db
def test__api__pdf_body__create__regulation_letter__stays_regulated(api_client: HitasAPIClient):
    data = {
        "name": PDFBodyName.STAYS_REGULATED.value,
        "texts": ["text 1", "text 2", "text 3"],
    }

    url = reverse("hitas:pdf-body-list")
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert response.json() == {
        "name": data["name"],
        "texts": data["texts"],
    }


@pytest.mark.django_db
def test__api__pdf_body__create__regulation_letter__released_from_regulation(api_client: HitasAPIClient):
    data = {
        "name": PDFBodyName.RELEASED_FROM_REGULATION.value,
        "texts": ["text 1"],
    }

    url = reverse("hitas:pdf-body-list")
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert response.json() == {
        "name": data["name"],
        "texts": data["texts"],
    }


@pytest.mark.django_db
def test__api__pdf_body__create__exists(api_client: HitasAPIClient):
    PDFBodyFactory.create(name=PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION)

    data = {
        "name": PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION.value,
        "texts": ["text 1", "text 2", "text 3"],
    }

    url = reverse("hitas:pdf-body-list")
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "name",
                "message": "PDF body with this name already exists.",
            },
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__pdf_body__create__invalid_name(api_client: HitasAPIClient):
    data = {
        "name": "foo",
        "texts": ["text 1", "text 2", "text 3"],
    }

    url = reverse("hitas:pdf-body-list")
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "name",
                "message": '"foo" is not a valid choice.',
            },
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.parametrize(
    ["name", "error"],
    [
        [
            PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION,
            "Unconfirmed max price calculation must have exactly 3 body texts.",
        ],
        [
            PDFBodyName.CONFIRMED_MAX_PRICE_CALCULATION,
            "Confirmed max price calculation must have exactly 1 body text.",
        ],
        [
            PDFBodyName.STAYS_REGULATED,
            "Regulation continuation letter must have exactly 3 body texts.",
        ],
        [
            PDFBodyName.RELEASED_FROM_REGULATION,
            "Regulation release letter must have exactly 1 body text.",
        ],
    ],
)
@pytest.mark.django_db
def test__api__pdf_body__create__invalid_text_size(api_client: HitasAPIClient, name: PDFBodyName, error: str):
    data = {
        "name": name.value,
        "texts": ["foo"] * 10,
    }

    url = reverse("hitas:pdf-body-list")
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "texts",
                "message": error,
            },
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


# Retrieve tests


@pytest.mark.django_db
def test__api__pdf_body__retrieve(api_client: HitasAPIClient):
    body: PDFBody = PDFBodyFactory.create(name=PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION)
    url = reverse("hitas:pdf-body-detail", kwargs={"name": body.name.value})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "name": body.name.value,
        "texts": body.texts,
    }


@pytest.mark.django_db
def test__api__pdf_body__retrieve__not_found(api_client: HitasAPIClient):
    PDFBodyFactory.create(name=PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION)
    url = reverse("hitas:pdf-body-detail", kwargs={"name": PDFBodyName.CONFIRMED_MAX_PRICE_CALCULATION.value})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "pdf_body_not_found",
        "message": "PDF body not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__pdf_body__retrieve__invalid_name(api_client: HitasAPIClient):
    PDFBodyFactory.create(name=PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION)
    url = reverse("hitas:pdf-body-detail", kwargs={"name": "foo"})
    response = api_client.get(url)

    # Even though the name is invalid, we still return 404, not 400
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "pdf_body_not_found",
        "message": "PDF body not found",
        "reason": "Not Found",
        "status": 404,
    }


# Update tests


@pytest.mark.django_db
def test__api__pdf_body__update(api_client: HitasAPIClient):
    body: PDFBody = PDFBodyFactory.create(name=PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION, texts=["foo", "bar"])

    data = {
        "name": PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION.value,
        "texts": ["text 1", "text 2", "text 3"],
    }
    url = reverse("hitas:pdf-body-detail", kwargs={"name": body.name.value})
    response = api_client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == data


@pytest.mark.parametrize(
    ["name", "error"],
    [
        [
            PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION,
            "Unconfirmed max price calculation must have exactly 3 body texts.",
        ],
        [
            PDFBodyName.CONFIRMED_MAX_PRICE_CALCULATION,
            "Confirmed max price calculation must have exactly 1 body text.",
        ],
    ],
)
@pytest.mark.django_db
def test__api__pdf_body__update__invalid_text_size(api_client: HitasAPIClient, name: PDFBodyName, error: str):
    body: PDFBody = PDFBodyFactory.create(name=name)
    data = {
        "name": name.value,
        "texts": ["foo"] * 10,
    }

    url = reverse("hitas:pdf-body-detail", kwargs={"name": body.name.value})
    response = api_client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "texts",
                "message": error,
            },
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


# Delete tests


@pytest.mark.django_db
def test__api__pdf_body__delete(api_client: HitasAPIClient):
    body: PDFBody = PDFBodyFactory.create(name=PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION)
    url = reverse("hitas:pdf-body-detail", kwargs={"name": body.name.value})
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()
    assert PDFBody.objects.filter(name=PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION).exists() is False
