from datetime import date
from typing import Any, Iterable, Optional

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory

from hitas.models import ApartmentSale, Ownership
from hitas.tests.factories.owner import OwnershipFactory


class ApartmentSaleFactory(DjangoModelFactory):
    class Meta:
        model = ApartmentSale

    apartment = factory.SubFactory(
        "hitas.tests.factories.ApartmentFactory",
        sales=factory.LazyAttribute(lambda _: []),  # prevents another sale from being created
    )
    notification_date = fuzzy.FuzzyDate(date(2010, 1, 1))
    purchase_date = fuzzy.FuzzyDate(date(2010, 1, 1))
    purchase_price = fuzzy.FuzzyDecimal(100_000, 200_000)
    apartment_share_of_housing_company_loans = fuzzy.FuzzyDecimal(100_000, 200_000)
    exclude_in_statistics = False

    @factory.post_generation
    def ownerships(self, create: bool, extracted: Optional[Iterable[Ownership]], **kwargs: Any) -> None:
        if not create:
            return

        if extracted is None:
            extracted = [OwnershipFactory.create(apartment=self.apartment, apartment__sales=self, **kwargs)]

        for ownership in extracted:
            self.ownerships.add(ownership)
