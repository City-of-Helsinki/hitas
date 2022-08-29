import factory
from factory.django import DjangoModelFactory
from faker import Faker

from hitas.models import Ownership, Person

fake = Faker(locale="fi_FI")


class PersonFactory(DjangoModelFactory):
    class Meta:
        model = Person

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    social_security_number = factory.Faker("ssn")
    email = factory.Faker("email")


class OwnershipFactory(DjangoModelFactory):
    class Meta:
        model = Ownership

    apartment = factory.SubFactory("hitas.tests.factories.ApartmentFactory")
    owner = factory.SubFactory("hitas.tests.factories.PersonFactory")
    percentage = 100
    start_date = None
    end_date = None
