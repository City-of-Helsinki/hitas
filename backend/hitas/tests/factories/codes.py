from datetime import datetime

import factory
import pytz
from factory import fuzzy
from factory.django import DjangoModelFactory
from faker import Faker

from hitas.models import ApartmentType, BuildingType, Developer, FinancingMethod

faker = Faker(locale="fi_FI")


class AbstractCodeFactory(DjangoModelFactory):
    class Meta:
        django_get_or_create = ("value",)
        abstract = True

    value = None
    description = factory.Faker("sentence")
    in_use = True
    order = None
    legacy_code_number = factory.Sequence(lambda n: f"{n%1000:03}")
    legacy_start_date = fuzzy.FuzzyDateTime(datetime(2010, 1, 1, tzinfo=pytz.timezone("Europe/Helsinki")))
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


class OldHitasFinancingMethodFactory(AbstractCodeFactory):
    class Meta:
        model = FinancingMethod

    value = fuzzy.FuzzyChoice(
        [
            "Tuntematon",
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
            "Uusi Hitas I (vanhat säännöt)",
            "Uusi Hitas II (vanhat säännöt)",
            "Vuokratalo Hitas II",
            "Vuokratalo Hitas I",
        ]
    )
    include_in_statistics = factory.Faker("boolean")
    old_hitas_ruleset = True
    half_hitas = False


class NewHitasFinancingMethodFactory(AbstractCodeFactory):
    class Meta:
        model = FinancingMethod

    value = fuzzy.FuzzyChoice(
        [
            "Tuntematon",
            "Uusi Hitas I (vapaarahoitteinen)",
            "Uusi Hitas II (vapaarahoitteinen)",
        ]
    )
    include_in_statistics = True
    old_hitas_ruleset = False
    half_hitas = False


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
