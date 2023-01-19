import factory
from factory import fuzzy
from factory.django import DjangoModelFactory

from hitas.models import ConditionOfSale
from hitas.models.condition_of_sale import GracePeriod


class ConditionOfSaleFactory(DjangoModelFactory):
    class Meta:
        model = ConditionOfSale

    new_ownership = factory.SubFactory("hitas.tests.factories.OwnershipFactory")
    old_ownership = factory.SubFactory("hitas.tests.factories.OwnershipFactory")
    grace_period = fuzzy.FuzzyChoice(state[0] for state in GracePeriod.choices())
