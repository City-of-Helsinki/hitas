import pytest
from django.urls import reverse
from rest_framework import status

from hitas.models.email_template import EmailTemplate, EmailTemplateName
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import EmailTemplateFactory

# List tests


@pytest.mark.django_db
def test__api__email_template__list__empty(api_client: HitasAPIClient):
    url = reverse("hitas:email-template-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == []


@pytest.mark.django_db
def test__api__email_template__list__single(api_client: HitasAPIClient):
    template = EmailTemplateFactory.create()

    url = reverse("hitas:email-template-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "name": template.name.value,
            "text": template.text,
        },
    ]


@pytest.mark.django_db
def test__api__email_template__list__multiple(api_client: HitasAPIClient):
    template_1: EmailTemplate = EmailTemplateFactory.create(name=EmailTemplateName.CONFIRMED_MAX_PRICE_CALCULATION)
    template_2: EmailTemplate = EmailTemplateFactory.create(name=EmailTemplateName.UNCONFIRMED_MAX_PRICE_CALCULATION)

    url = reverse("hitas:email-template-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "name": template_1.name.value,
            "text": template_1.text,
        },
        {
            "name": template_2.name.value,
            "text": template_2.text,
        },
    ]


# Create tests


@pytest.mark.django_db
def test__api__email_template__create(api_client: HitasAPIClient):
    data = {
        "name": EmailTemplateName.CONFIRMED_MAX_PRICE_CALCULATION.value,
        "text": "foo",
    }
    url = reverse("hitas:email-template-list")
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert list(response.json()) == ["name", "text"]
    assert response.json()["name"] == EmailTemplateName.CONFIRMED_MAX_PRICE_CALCULATION.value
    assert response.json()["text"] == "foo"


@pytest.mark.django_db
def test__api__email_template__create__exists(api_client: HitasAPIClient):
    EmailTemplateFactory.create(name=EmailTemplateName.CONFIRMED_MAX_PRICE_CALCULATION)
    data = {
        "name": EmailTemplateName.CONFIRMED_MAX_PRICE_CALCULATION.value,
        "text": "foo",
    }
    url = reverse("hitas:email-template-list")
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "name",
                "message": "Email template with this name already exists.",
            },
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__email_template__create__invalid_name(api_client: HitasAPIClient):
    data = {
        "name": "foo",
        "text": "bar",
    }
    url = reverse("hitas:email-template-list")
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


# Retrieve tests


@pytest.mark.django_db
def test__api__email_template__retrieve(api_client: HitasAPIClient):
    template: EmailTemplate = EmailTemplateFactory.create()

    url = reverse("hitas:email-template-detail", kwargs={"name": template.name.value})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert list(response.json()) == ["name", "text"]
    assert response.json()["name"] == template.name.value
    assert response.json()["text"] == template.text


@pytest.mark.django_db
def test__api__email_template__retrieve__not_found(api_client: HitasAPIClient):
    EmailTemplateFactory.create(name=EmailTemplateName.CONFIRMED_MAX_PRICE_CALCULATION)

    url = reverse(
        "hitas:email-template-detail",
        kwargs={
            "name": EmailTemplateName.UNCONFIRMED_MAX_PRICE_CALCULATION.value,
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
    template: EmailTemplate = EmailTemplateFactory.create(text="foo")

    data = {
        "name": template.name.value,
        "text": "bar",
    }

    url = reverse("hitas:email-template-detail", kwargs={"name": template.name.value})
    response = api_client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert list(response.json()) == ["name", "text"]
    assert response.json()["name"] == template.name.value
    assert response.json()["text"] == "bar"


# Delete tests


@pytest.mark.django_db
def test__api__email_template__delete(api_client: HitasAPIClient):
    template: EmailTemplate = EmailTemplateFactory.create(text="foo")

    url = reverse("hitas:email-template-detail", kwargs={"name": template.name.value})
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()
    assert EmailTemplate.objects.filter(name=template.name).exists() is False
