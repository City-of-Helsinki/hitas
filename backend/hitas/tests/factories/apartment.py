from datetime import date

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory

from hitas.models import Apartment
from hitas.models.apartment import ApartmentState


class ApartmentFactory(DjangoModelFactory):
    class Meta:
        model = Apartment

    building = factory.SubFactory("hitas.tests.factories.BuildingFactory")
    state = fuzzy.FuzzyChoice(state[0] for state in ApartmentState.choices())
    apartment_type = factory.SubFactory("hitas.tests.factories.ApartmentTypeFactory")
    surface_area = fuzzy.FuzzyDecimal(10, 99, precision=2)
    share_number_start = factory.Sequence(lambda n: n * 50 + 1)
    share_number_end = factory.LazyAttribute(lambda self: (self.share_number_start + 50))
    street_address = factory.Faker("street_address")
    completion_date = fuzzy.FuzzyDate(date(2010, 1, 1))
    apartment_number = fuzzy.FuzzyInteger(1, 99)
    floor = factory.Faker("numerify", text="%")
    stair = factory.Faker("bothify", text="?")  # Random letter
    debt_free_purchase_price = fuzzy.FuzzyInteger(100000, 200000)
    purchase_price = fuzzy.FuzzyInteger(100000, 200000)
    primary_loan_amount = fuzzy.FuzzyInteger(100000, 200000)
    loans_during_construction = fuzzy.FuzzyInteger(100000, 200000)
    interest_during_construction = fuzzy.FuzzyInteger(10000, 20000)
    notes = factory.Faker("text")
