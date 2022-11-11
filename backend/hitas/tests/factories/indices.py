import datetime

import factory
from dateutil.relativedelta import relativedelta
from factory import fuzzy
from factory.django import DjangoModelFactory
from faker import Faker

from hitas.models import (
    ConstructionPriceIndex,
    ConstructionPriceIndex2005Equal100,
    MarketPriceIndex,
    MarketPriceIndex2005Equal100,
    MaximumPriceIndex,
    SurfaceAreaPriceCeiling,
)

faker = Faker(locale="fi_FI")


class AbstractIndexFactory(DjangoModelFactory):
    class Meta:
        abstract = True

    month = factory.Sequence(lambda n: datetime.date(2000, 1, 1) + relativedelta(months=n))
    value = fuzzy.FuzzyDecimal(low=0, high=1000)


class MaximumPriceIndexFactory(AbstractIndexFactory):
    class Meta:
        model = MaximumPriceIndex


class MarketPriceIndexFactory(AbstractIndexFactory):
    class Meta:
        model = MarketPriceIndex


class MarketPriceIndex2005Equal100Factory(AbstractIndexFactory):
    class Meta:
        model = MarketPriceIndex2005Equal100


class ConstructionPriceIndexFactory(AbstractIndexFactory):
    class Meta:
        model = ConstructionPriceIndex


class ConstructionPriceIndex2005Equal100Factory(AbstractIndexFactory):
    class Meta:
        model = ConstructionPriceIndex2005Equal100


class SurfaceAreaPriceCeilingFactory(AbstractIndexFactory):
    class Meta:
        model = SurfaceAreaPriceCeiling
