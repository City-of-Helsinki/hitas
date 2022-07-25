from datetime import datetime

import factory
import pytz
from factory import fuzzy
from factory.django import DjangoModelFactory
from faker import Faker

from hitas.models import ApartmentType, BuildingType, Developer, FinancingMethod, PostalCode

fake = Faker(locale="fi_FI")


class AbstractCodeFactory(DjangoModelFactory):
    class Meta:
        django_get_or_create = ("value",)
        abstract = True

    value = None
    description = fake.sentence()
    in_use = True
    order = None
    legacy_code_number = factory.Sequence(lambda n: f"{n%1000:03}")
    legacy_start_date = fuzzy.FuzzyDateTime(datetime(2010, 1, 1, tzinfo=pytz.timezone("Europe/Helsinki")))
    legacy_end_date = None


class PostalCodeFactory(AbstractCodeFactory):
    class Meta:
        model = PostalCode
        django_get_or_create = ("value",)

    # # Helsinki area postal code e.g. 00100
    value = factory.Sequence(lambda n: fake.bothify(f"0{n%100:02}#0"))
    description = fake.city()


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


class FinancingMethodFactory(AbstractCodeFactory):
    class Meta:
        model = FinancingMethod
        django_get_or_create = ("value",)

    value = fuzzy.FuzzyChoice(
        [
            "tuntematon",
            "vapaarahoitteinen, Hitas I",
            "vapaarahoitteinen, Hitas II",
            "HK valtion laina, Hitas I",
            "HK valtion laina, Hitas II",
            "RA valtion laina, Hitas I",
            "RA valtion laina, Hitas I",
            "HK valtion laina, Hitas I",
            "HK valtion laina, Hitas II",
            "RA valtion laina, Hitas I",
            "RA valtion laina, Hitas II",
            "Korkotuki, Hitas I",
            "Korkotuki, Hitas II",
            "Lyhyt korkotukilaina, ns. osaomistus Hitas I",
            "Pitkä korkotukilaina osaomistus Hitas I",
            "Omaksi lunastettava vuokra-asunto, Hitas I",
            "Uusi Hitas I (vapaarahoitteinen)",
            "Uusi Hitas II (vapaarahoitteinen)",
            "Uusi Hitas I (vanhat säännöt)",
            "Uusi Hitas II (vanhat säännöt)",
            "Vuokratalo Hitas II",
            "Vuokratalo Hitas I",
        ]
    )


class DeveloperFactory(AbstractCodeFactory):
    class Meta:
        model = Developer
        django_get_or_create = ("value",)

    value = factory.LazyAttribute(lambda self: f"As Oy {fake.last_name()}")


class ApartmentTypeFactory(AbstractCodeFactory):
    class Meta:
        model = ApartmentType
        django_get_or_create = ("value",)

    value = fuzzy.FuzzyChoice(
        [
            "tuntematon",
            "1h",
            "2h",
            "Alkovi+tupak+s",
            "2h+kk+s",
            "2h+k+s",
            "3h+kk+s",
            "2h+kk+s",
            "2mh+tupak+s",
            "Alkovi+tupak+s",
            "2mh+tupak+s",
        ]
    )
