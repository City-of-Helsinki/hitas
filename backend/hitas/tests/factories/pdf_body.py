import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from faker import Faker

from hitas.models import PDFBody
from hitas.models.pdf_body import PDFBodyName

fake = Faker("fi_FI")


class PDFBodyFactory(DjangoModelFactory):
    class Meta:
        model = PDFBody
        django_get_or_create = ("name",)

    name = fuzzy.FuzzyChoice(state[0] for state in PDFBodyName.choices())
    texts = factory.List(fake.text() for _ in range(3))
