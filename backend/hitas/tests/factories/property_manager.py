import factory
from factory.django import DjangoModelFactory

from hitas.models import PropertyManager


class PropertyManagerFactory(DjangoModelFactory):
    class Meta:
        model = PropertyManager

    name = factory.Faker("name")
    email = factory.Faker("email")
