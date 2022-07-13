import factory
from factory.django import DjangoModelFactory
from faker import Faker

from hitas.models import PropertyManager

fake = Faker(locale="fi_FI")


class PropertyManagerFactory(DjangoModelFactory):
    class Meta:
        model = PropertyManager

    name = fake.name()
    email = fake.email()
    street_address = fake.street_address()
    postal_code = factory.SubFactory("hitas.tests.factories.PostalCodeFactory")
