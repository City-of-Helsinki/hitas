import datetime

import factory
from dateutil.relativedelta import relativedelta
from factory import fuzzy
from factory.django import DjangoModelFactory
from faker import Faker

from hitas.models import (
    ConstructionPriceIndex,
    ConstructionPriceIndexPre2005,
    MarketPriceIndex,
    MarketPriceIndexPre2005,
    MaxPriceIndex,
    SurfaceAreaPriceCeiling,
)

faker = Faker(locale="fi_FI")


class AbstractIndexFactory(DjangoModelFactory):
    class Meta:
        abstract = True

    month = factory.Sequence(lambda n: datetime.date(2000, 1, 1) + relativedelta(months=n))
    value = fuzzy.FuzzyDecimal(low=0)


class MaxPriceIndexFactory(AbstractIndexFactory):
    class Meta:
        model = MaxPriceIndex


class MarketPriceIndexFactory(AbstractIndexFactory):
    class Meta:
        model = MarketPriceIndex


class MarketPriceIndexPre2005Factory(AbstractIndexFactory):
    class Meta:
        model = MarketPriceIndexPre2005


class ConstructionPriceIndexFactory(AbstractIndexFactory):
    class Meta:
        model = ConstructionPriceIndex


class ConstructionPriceIndexPre2005Factory(AbstractIndexFactory):
    class Meta:
        model = ConstructionPriceIndexPre2005


class SurfaceAreaPriceCeilingFactory(AbstractIndexFactory):
    class Meta:
        model = SurfaceAreaPriceCeiling
