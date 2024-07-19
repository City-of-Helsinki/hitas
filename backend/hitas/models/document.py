import os
from uuid import uuid4

from crum import get_current_request
from django.db import models
from django.urls import reverse
from django.utils.deconstruct import deconstructible
from safedelete import SOFT_DELETE_CASCADE

from hitas.models._base import ExternalSafeDeleteHitasModel


@deconstructible
class DocumentFilenameGenerator:
    def __init__(self, directory=""):
        self.upload_to_directory = directory

    def __call__(self, instance, filename):
        _, extension = os.path.splitext(filename)
        generated_filename = f"{uuid4()}{extension}"
        parent_id = str(instance.get_parent().pk)
        return os.path.join(self.upload_to_directory, parent_id, generated_filename)

    def __eq__(self, other):
        return isinstance(other, DocumentFilenameGenerator) and self.upload_to_directory == other.upload_to_directory


class BaseDocument(ExternalSafeDeleteHitasModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    display_name = models.CharField(max_length=1024)
    original_filename = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class HousingCompanyDocument(BaseDocument):
    file = models.FileField(upload_to=DocumentFilenameGenerator("housingcompany_documents"))
    housing_company = models.ForeignKey("HousingCompany", on_delete=models.CASCADE, related_name="documents")

    def get_parent(self):
        return self.housing_company

    def get_file_link(self):
        request = get_current_request()
        return request.build_absolute_uri(
            reverse(
                "hitas:document-redirect",
                kwargs={
                    "housing_company_uuid": self.housing_company.uuid.hex,
                    "uuid": self.uuid.hex,
                },
            )
        )


class AparmentDocument(BaseDocument):
    file = models.FileField(upload_to=DocumentFilenameGenerator("apartment_documents"))
    apartment = models.ForeignKey("Apartment", on_delete=models.CASCADE, related_name="documents")

    def get_parent(self):
        return self.apartment

    def get_file_link(self):
        request = get_current_request()
        return request.build_absolute_uri(
            reverse(
                "hitas:document-redirect",
                kwargs={
                    "housing_company_uuid": self.apartment.housing_company.uuid.hex,
                    "apartment_uuid": self.apartment.uuid.hex,
                    "uuid": self.uuid.hex,
                },
            )
        )
