import pytest
from django.urls import reverse
from rest_framework import status

from hitas.models.email_template import EmailTemplate, EmailTemplateType
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import EmailTemplateFactory

# List tests


@pytest.mark.django_db
def test__api__email_template__list__empty(api_client: HitasAPIClient):
    url = reverse("hitas:email-template-list", kwargs={"type": EmailTemplateType.CONFIRMED_MAX_PRICE_CALCULATION.value})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == []


@pytest.mark.django_db
def test__api__email_template__list__different_type(api_client: HitasAPIClient):
    EmailTemplateFactory.create(type=EmailTemplateType.UNCONFIRMED_MAX_PRICE_CALCULATION)

    url = reverse("hitas:email-template-list", kwargs={"type": EmailTemplateType.CONFIRMED_MAX_PRICE_CALCULATION.value})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == []


@pytest.mark.django_db
def test__api__email_template__list__invalid_type(api_client: HitasAPIClient):
    url = reverse("hitas:email-template-list", kwargs={"type": "foo"})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "type",
                "message": "Invalid template type.",
            },
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__email_template__list__single(api_client: HitasAPIClient):
    template = EmailTemplateFactory.create(type=EmailTemplateType.CONFIRMED_MAX_PRICE_CALCULATION)

    url = reverse("hitas:email-template-list", kwargs={"type": EmailTemplateType.CONFIRMED_MAX_PRICE_CALCULATION.value})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "name": template.name,
            "type": template.type.value,
            "text": template.text,
        },
    ]


@pytest.mark.django_db
def test__api__email_template__list__multiple(api_client: HitasAPIClient):
    template_1: EmailTemplate = EmailTemplateFactory.create(type=EmailTemplateType.CONFIRMED_MAX_PRICE_CALCULATION)
    template_2: EmailTemplate = EmailTemplateFactory.create(type=EmailTemplateType.CONFIRMED_MAX_PRICE_CALCULATION)

    url = reverse("hitas:email-template-list", kwargs={"type": EmailTemplateType.CONFIRMED_MAX_PRICE_CALCULATION.value})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "name": template_1.name,
            "type": template_1.type.value,
            "text": template_1.text,
        },
        {
            "name": template_2.name,
            "type": template_2.type.value,
            "text": template_2.text,
        },
    ]


# Create tests


@pytest.mark.django_db
def test__api__email_template__create(api_client: HitasAPIClient):
    data = {
        "name": "foo",
        "text": "bar",
    }
    url = reverse("hitas:email-template-list", kwargs={"type": EmailTemplateType.CONFIRMED_MAX_PRICE_CALCULATION.value})
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert list(response.json()) == ["name", "type", "text"]
    assert response.json()["name"] == "foo"
    assert response.json()["type"] == EmailTemplateType.CONFIRMED_MAX_PRICE_CALCULATION.value
    assert response.json()["text"] == "bar"


@pytest.mark.django_db
def test__api__email_template__create__exists(api_client: HitasAPIClient):
    EmailTemplateFactory.create(name="foo", type=EmailTemplateType.CONFIRMED_MAX_PRICE_CALCULATION)
    data = {
        "name": "foo",
        "text": "foo",
    }
    url = reverse("hitas:email-template-list", kwargs={"type": EmailTemplateType.CONFIRMED_MAX_PRICE_CALCULATION.value})
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "non_field_errors",
                "message": "Email template with this type and name already exists.",
            },
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__email_template__create__exists__different_type(api_client: HitasAPIClient):
    EmailTemplateFactory.create(name="foo", type=EmailTemplateType.UNCONFIRMED_MAX_PRICE_CALCULATION)
    data = {
        "name": "foo",
        "text": "bar",
    }
    url = reverse("hitas:email-template-list", kwargs={"type": EmailTemplateType.CONFIRMED_MAX_PRICE_CALCULATION.value})
    response = api_client.post(url, data=data, format="json")

    # Can create a template with the same name if the type is different
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert list(response.json()) == ["name", "type", "text"]
    assert response.json()["name"] == "foo"
    assert response.json()["type"] == EmailTemplateType.CONFIRMED_MAX_PRICE_CALCULATION.value
    assert response.json()["text"] == "bar"


@pytest.mark.django_db
def test__api__email_template__create__invalid_type(api_client: HitasAPIClient):
    data = {
        "name": "foo",
        "text": "foo",
    }
    url = reverse("hitas:email-template-list", kwargs={"type": "foo"})
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "type",
                "message": "Invalid template type.",
            },
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


# Retrieve tests


@pytest.mark.django_db
def test__api__email_template__retrieve(api_client: HitasAPIClient):
    template: EmailTemplate = EmailTemplateFactory.create()

    url = reverse("hitas:email-template-detail", kwargs={"type": template.type.value, "name": template.name})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert list(response.json()) == ["name", "type", "text"]
    assert response.json()["name"] == template.name
    assert response.json()["type"] == template.type.value
    assert response.json()["text"] == template.text


@pytest.mark.django_db
def test__api__email_template__retrieve__not_found(api_client: HitasAPIClient):
    EmailTemplateFactory.create(type=EmailTemplateType.CONFIRMED_MAX_PRICE_CALCULATION, name="foo")

    url = reverse(
        "hitas:email-template-detail",
        kwargs={
            "type": EmailTemplateType.UNCONFIRMED_MAX_PRICE_CALCULATION.value,
            "name": "bar",
        },
    )
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "email_template_not_found",
        "message": "Email template not found",
        "reason": "Not Found",
        "status": 404,
    }


# Update tests


@pytest.mark.django_db
def test__api__email_template__update(api_client: HitasAPIClient):
    template: EmailTemplate = EmailTemplateFactory.create(name="one", text="foo")

    data = {
        "name": "two",
        "text": "bar",
    }

    url = reverse("hitas:email-template-detail", kwargs={"type": template.type.value, "name": template.name})
    response = api_client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert list(response.json()) == ["name", "type", "text"]
    assert response.json()["name"] == "two"
    assert response.json()["type"] == template.type.value
    assert response.json()["text"] == "bar"


# Delete tests


@pytest.mark.django_db
def test__api__email_template__delete(api_client: HitasAPIClient):
    template: EmailTemplate = EmailTemplateFactory.create(name="foo")

    url = reverse("hitas:email-template-detail", kwargs={"type": template.type.value, "name": template.name})
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()
    assert EmailTemplate.objects.filter(type=template.type, name=template.name).exists() is False
