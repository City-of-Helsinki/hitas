from datetime import datetime
from zoneinfo import ZoneInfo

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from faker import Faker

from hitas.models import ApartmentType, BuildingType, Developer

faker = Faker(locale="fi_FI")


class AbstractCodeFactory(DjangoModelFactory):
    class Meta:
        abstract = True

    value = None
    description = factory.Faker("sentence")
    in_use = True
    order = None
    legacy_code_number = factory.Sequence(lambda n: f"{n%1000:03}")
    legacy_start_date = fuzzy.FuzzyDateTime(datetime(2010, 1, 1, tzinfo=ZoneInfo("Europe/Helsinki")))
    legacy_end_date = None


class BuildingTypeFactory(AbstractCodeFactory):
    class Meta:
        model = BuildingType
        django_get_or_create = ("value",)

    value = fuzzy.FuzzyChoice(
        [
            "tuntematon",
            "kerrostalo",
            "rivitalo",
            "paritalo",
            "pienkerrostalo",
            "luhtitalo",
            "omakotitalo",
            "rivitalo/kerrostalo",
            "kerrostalo/rivitalo",
            "pientalo",
            "erillistalo",
            "rivitalo/erillistalo",
        ]
    )


class DeveloperFactory(AbstractCodeFactory):
    class Meta:
        model = Developer
        django_get_or_create = ("value",)

    value = factory.LazyAttribute(lambda _: f"As Oy {faker.last_name()}")


class ApartmentTypeFactory(AbstractCodeFactory):
    class Meta:
        model = ApartmentType
        django_get_or_create = ("value",)

    value = fuzzy.FuzzyChoice(
        [
            "tuntematon",
            "h",
            "Alkovi+tupak+s",
            "h+k+s",
            "h+kk+s",
            "mh+tupak+s",
            "h+k+khh+s+piha",
            "h+k+työtila",
        ]
    )
