from datetime import date

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory


class AbstractImprovementFactory(DjangoModelFactory):
    class Meta:
        abstract = True

    name = factory.Faker("sentence")
    completion_date = fuzzy.FuzzyDate(date(2010, 1, 1))
    value = fuzzy.FuzzyDecimal(low=1, high=100000)
