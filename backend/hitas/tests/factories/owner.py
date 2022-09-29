import factory
from factory.django import DjangoModelFactory
from faker import Faker

from hitas.models import Owner, Ownership

fake = Faker(locale="fi_FI")


class OwnerFactory(DjangoModelFactory):
    class Meta:
        model = Owner

    name = factory.Faker("name")
    identifier = factory.Faker("ssn")
    email = factory.Faker("email")


class OwnershipFactory(DjangoModelFactory):
    class Meta:
        model = Ownership

    apartment = factory.SubFactory("hitas.tests.factories.ApartmentFactory")
    owner = factory.SubFactory("hitas.tests.factories.OwnerFactory")
    percentage = 100
    start_date = None
    end_date = None
