import factory
from factory import fuzzy
from factory.django import DjangoModelFactory

from users.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    is_staff = False
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.LazyAttribute(lambda u: f"{u.first_name.lower()}_{ u.last_name.lower()}")
    email = factory.LazyAttribute(lambda u: f"{u.first_name.lower()}.{ u.last_name.lower()}@example.com")
    phone = factory.Faker("phone_number")
    title = fuzzy.FuzzyChoice(state for state in ("asuntosihteeri", "suunnittelija"))
