import factory
from factory.django import DjangoModelFactory
from faker import Faker
from faker.providers import BaseProvider

from hitas.models import Owner, Ownership
from hitas.models.utils import _business_id_checksum

faker = Faker(locale="fi_FI")


class IdentifierProvider(BaseProvider):
    def identifier(self):
        # 10% of identifiers generated are business ids
        if self.random_digit() == 0:
            return self.business_id()
        else:
            return faker.ssn()

    def business_id(self):
        # Continuously generate until we generate a valid one
        while True:
            seqnum = str(self.random_number(digits=7, fix_len=True))
            checksum = _business_id_checksum(seqnum)
            match checksum:  # noqa: E999
                case 0:
                    return seqnum + "-0"
                case 1:
                    # Not a valid checksum, try again
                    continue
                case _:
                    return seqnum + "-" + str(11 - checksum)


faker.add_provider(IdentifierProvider)


class OwnerFactory(DjangoModelFactory):
    class Meta:
        model = Owner

    name = factory.Faker("name")
    identifier = faker.identifier()
    email = factory.Faker("email")
    bypass_conditions_of_sale = False
    non_disclosure = False


class OwnershipFactory(DjangoModelFactory):
    class Meta:
        model = Ownership

    owner = factory.SubFactory("hitas.tests.factories.OwnerFactory")
    sale = factory.SubFactory(
        "hitas.tests.factories.ApartmentSaleFactory",
        ownerships=factory.LazyAttribute(lambda _: []),  # prevents another ownership from being created
    )
    percentage = 100
