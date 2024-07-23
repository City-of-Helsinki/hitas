import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status

from hitas.models import (
    AparmentDocument,
    HousingCompanyDocument,
)
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import (
    ApartmentFactory,
    HousingCompanyFactory,
)


@pytest.mark.django_db
def test__api__apartment__document__list(api_client: HitasAPIClient):
    apartment = ApartmentFactory()
    AparmentDocument.objects.create(apartment=apartment, display_name="Test document", original_filename="test.pdf")
    response = api_client.get(
        reverse("hitas:document-list", args=[apartment.housing_company.uuid.hex, apartment.uuid.hex])
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    document_list = data["contents"]
    assert len(document_list) == 1
    assert document_list[0]["display_name"] == "Test document"
    assert document_list[0]["file_link"] is not None


@pytest.mark.django_db
def test__api__housingcompany__document__list(api_client: HitasAPIClient):
    housing_company = HousingCompanyFactory()
    HousingCompanyDocument.objects.create(
        housing_company=housing_company, display_name="Test document", original_filename="test.pdf"
    )
    response = api_client.get(reverse("hitas:document-list", args=[housing_company.uuid.hex]))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    document_list = data["contents"]
    assert len(document_list) == 1
    assert document_list[0]["display_name"] == "Test document"
    assert document_list[0]["file_link"] is not None


@pytest.mark.django_db
def test__api__apartment__document__create(api_client: HitasAPIClient):
    apartment = ApartmentFactory()
    response = api_client.post(
        reverse("hitas:document-list", args=[apartment.housing_company.uuid.hex, apartment.uuid.hex]),
        data={
            "display_name": "Test document",
            "file_content": SimpleUploadedFile("testfile.txt", b"test file content", content_type="text/plain"),
        },
        format="multipart",
    )
    assert response.status_code == status.HTTP_201_CREATED
    document = AparmentDocument.objects.get(apartment=apartment)
    assert document.display_name == "Test document"
    assert document.original_filename == "testfile.txt"
    assert document.file.read() == b"test file content"


@pytest.mark.django_db
def test__api__housingcompany__document__create(api_client: HitasAPIClient):
    housing_company = HousingCompanyFactory()
    response = api_client.post(
        reverse("hitas:document-list", args=[housing_company.uuid.hex]),
        data={
            "display_name": "Test document",
            "file_content": SimpleUploadedFile("testfile.txt", b"test file content", content_type="text/plain"),
        },
        format="multipart",
    )
    assert response.status_code == status.HTTP_201_CREATED
    document = HousingCompanyDocument.objects.get(housing_company=housing_company)
    assert document.display_name == "Test document"
    assert document.original_filename == "testfile.txt"
    assert document.file.read() == b"test file content"


@pytest.mark.django_db
def test__api__apartment__document__update__display_name(api_client: HitasAPIClient):
    apartment = ApartmentFactory()
    document = AparmentDocument.objects.create(
        apartment=apartment, display_name="Test document", original_filename="testfile.txt"
    )
    response = api_client.put(
        reverse(
            "hitas:document-detail", args=[apartment.housing_company.uuid.hex, apartment.uuid.hex, document.uuid.hex]
        ),
        data={"display_name": "Updated document"},
    )
    assert response.status_code == status.HTTP_200_OK
    document.refresh_from_db()
    assert document.display_name == "Updated document"


@pytest.mark.django_db
def test__api__housingcompany__document__update__display_name(api_client: HitasAPIClient):
    housing_company = HousingCompanyFactory()
    document = HousingCompanyDocument.objects.create(
        housing_company=housing_company, display_name="Test document", original_filename="testfile.txt"
    )
    response = api_client.put(
        reverse("hitas:document-detail", args=[housing_company.uuid.hex, document.uuid.hex]),
        data={"display_name": "Updated document"},
    )
    assert response.status_code == status.HTTP_200_OK
    document.refresh_from_db()
    assert document.display_name == "Updated document"


@pytest.mark.django_db
def test__api__apartment__document__update__file(api_client: HitasAPIClient):
    apartment = ApartmentFactory()
    document = AparmentDocument.objects.create(
        apartment=apartment, display_name="Test document", original_filename="testfile.txt"
    )
    response = api_client.put(
        reverse(
            "hitas:document-detail", args=[apartment.housing_company.uuid.hex, apartment.uuid.hex, document.uuid.hex]
        ),
        data={
            "display_name": "Test document",
            "file_content": SimpleUploadedFile("testfile.txt", b"test file content 1", content_type="text/plain"),
        },
    )
    assert response.status_code == status.HTTP_200_OK
    document.refresh_from_db()
    assert document.file.read() == b"test file content 1"
    old_filename = document.file.name
    response = api_client.put(
        reverse(
            "hitas:document-detail", args=[apartment.housing_company.uuid.hex, apartment.uuid.hex, document.uuid.hex]
        ),
        data={
            "display_name": "Test document",
            "file_content": SimpleUploadedFile("testfile.txt", b"test file content 2", content_type="text/plain"),
        },
    )
    assert response.status_code == status.HTTP_200_OK
    document.refresh_from_db()
    assert document.file.read() == b"test file content 2"
    assert not document.file.storage.exists(old_filename), "Old file should be deleted from storage"


@pytest.mark.django_db
def test__api__housingcompany__document__update__file(api_client: HitasAPIClient):
    housing_company = HousingCompanyFactory()
    document = HousingCompanyDocument.objects.create(
        housing_company=housing_company, display_name="Test document", original_filename="testfile.txt"
    )
    response = api_client.put(
        reverse("hitas:document-detail", args=[housing_company.uuid.hex, document.uuid.hex]),
        data={
            "display_name": "Test document",
            "file_content": SimpleUploadedFile("testfile.txt", b"test file content 1", content_type="text/plain"),
        },
    )
    assert response.status_code == status.HTTP_200_OK
    document.refresh_from_db()
    assert document.file.read() == b"test file content 1"
    old_filename = document.file.name
    response = api_client.put(
        reverse("hitas:document-detail", args=[housing_company.uuid.hex, document.uuid.hex]),
        data={
            "display_name": "Test document",
            "file_content": SimpleUploadedFile("testfile.txt", b"test file content 2", content_type="text/plain"),
        },
    )
    assert response.status_code == status.HTTP_200_OK
    document.refresh_from_db()
    assert document.file.read() == b"test file content 2"
    assert not document.file.storage.exists(old_filename), "Old file should be deleted from storage"


@pytest.mark.django_db
def test__api__apartment__document__redirect(api_client: HitasAPIClient):
    apartment = ApartmentFactory()
    response = api_client.post(
        reverse("hitas:document-list", args=[apartment.housing_company.uuid.hex, apartment.uuid.hex]),
        data={
            "display_name": "Test document",
            "file_content": SimpleUploadedFile("testfile.txt", b"test file content", content_type="text/plain"),
        },
        format="multipart",
    )
    assert response.status_code == status.HTTP_201_CREATED
    document = AparmentDocument.objects.get(apartment=apartment)
    response = api_client.get(
        reverse(
            "hitas:document-redirect", args=[apartment.housing_company.uuid.hex, apartment.uuid.hex, document.uuid.hex]
        )
    )
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test__api__housingcompany__document__redirect(api_client: HitasAPIClient):
    housing_company = HousingCompanyFactory()
    response = api_client.post(
        reverse("hitas:document-list", args=[housing_company.uuid.hex]),
        data={
            "display_name": "Test document",
            "file_content": SimpleUploadedFile("testfile.txt", b"test file content", content_type="text/plain"),
        },
        format="multipart",
    )
    assert response.status_code == status.HTTP_201_CREATED
    document = HousingCompanyDocument.objects.get(housing_company=housing_company)
    response = api_client.get(reverse("hitas:document-redirect", args=[housing_company.uuid.hex, document.uuid.hex]))
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test__api__apartment__document__delete(api_client: HitasAPIClient):
    apartment = ApartmentFactory()
    response = api_client.post(
        reverse("hitas:document-list", args=[apartment.housing_company.uuid.hex, apartment.uuid.hex]),
        data={
            "display_name": "Test document",
            "file_content": SimpleUploadedFile("testfile.txt", b"test file content", content_type="text/plain"),
        },
        format="multipart",
    )
    assert response.status_code == status.HTTP_201_CREATED
    document = AparmentDocument.objects.get(apartment=apartment)
    assert document.file.storage.exists(document.file.name)
    response = api_client.delete(
        reverse(
            "hitas:document-detail", args=[apartment.housing_company.uuid.hex, apartment.uuid.hex, document.uuid.hex]
        )
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = api_client.get(
        reverse(
            "hitas:document-detail", args=[apartment.housing_company.uuid.hex, apartment.uuid.hex, document.uuid.hex]
        )
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not document.file.storage.exists(document.file.name)


@pytest.mark.django_db
def test__api__housingcompany__document__delete(api_client: HitasAPIClient):
    housing_company = HousingCompanyFactory()
    response = api_client.post(
        reverse("hitas:document-list", args=[housing_company.uuid.hex]),
        data={
            "display_name": "Test document",
            "file_content": SimpleUploadedFile("testfile.txt", b"test file content", content_type="text/plain"),
        },
        format="multipart",
    )
    assert response.status_code == status.HTTP_201_CREATED
    document = HousingCompanyDocument.objects.get(housing_company=housing_company)
    assert document.file.storage.exists(document.file.name)
    response = api_client.delete(reverse("hitas:document-detail", args=[housing_company.uuid.hex, document.uuid.hex]))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = api_client.get(reverse("hitas:document-detail", args=[housing_company.uuid.hex, document.uuid.hex]))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not document.file.storage.exists(document.file.name)
