import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from faker import Faker

from hitas.models import HitasPostalCode

faker = Faker(locale="fi_FI")


class HitasPostalCodeFactory(DjangoModelFactory):
    class Meta:
        model = HitasPostalCode
        django_get_or_create = ("value",)

    # # Helsinki area postal code e.g. 00100
    value = factory.Sequence(lambda n: faker.bothify(f"0{n%100:02}#0"))
    city = "Helsinki"
    cost_area = fuzzy.FuzzyInteger(1, 4)
