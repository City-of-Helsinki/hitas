import factory
from factory import fuzzy
from factory.django import DjangoModelFactory

from hitas.models import EmailTemplate
from hitas.models.email_template import EmailTemplateType


class EmailTemplateFactory(DjangoModelFactory):
    class Meta:
        model = EmailTemplate
        django_get_or_create = ("name", "type")

    name = factory.Faker("word")
    type = fuzzy.FuzzyChoice(state[0] for state in EmailTemplateType.choices())
    text = factory.Faker("text")
