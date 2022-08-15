from datetime import date

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from faker import Faker

from hitas.models import Owner, Person

fake = Faker(locale="fi_FI")


class PersonFactory(DjangoModelFactory):
    class Meta:
        model = Person

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    social_security_number = factory.Faker("ssn")
    email = factory.Faker("email")
    street_address = factory.Faker("street_address")
    postal_code = factory.SubFactory("hitas.tests.factories.PostalCodeFactory")


class OwnerFactory(DjangoModelFactory):
    class Meta:
        model = Owner

    apartment = factory.SubFactory("hitas.tests.factories.ApartmentFactory")
    person = factory.SubFactory("hitas.tests.factories.PersonFactory")
    ownership_percentage = 100
    ownership_start_date = fuzzy.FuzzyDate(date(2010, 1, 1))
    ownership_end_date = None
