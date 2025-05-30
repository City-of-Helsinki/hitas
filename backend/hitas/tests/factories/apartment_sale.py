from datetime import date
from typing import Any, Iterable, Optional

import factory
from django.conf import settings
from factory import fuzzy
from factory.django import DjangoModelFactory

from hitas.models import ApartmentSale, Ownership
from hitas.tests.factories.owner import OwnershipFactory


class ApartmentSaleFactory(DjangoModelFactory):
    class Meta:
        model = ApartmentSale
        skip_postgeneration_save = True

    apartment = factory.SubFactory(
        "hitas.tests.factories.ApartmentFactory",
        sales=factory.LazyAttribute(lambda _: []),  # prevents another sale from being created
    )
    notification_date = fuzzy.FuzzyDate(date(2010, 1, 1))
    purchase_date = factory.LazyAttribute(
        lambda self: (self.apartment.completion_date or fuzzy.FuzzyDate(date(2010, 1, 1)).fuzz())
    )
    purchase_price = fuzzy.FuzzyDecimal(100_000, 200_000)
    apartment_share_of_housing_company_loans = fuzzy.FuzzyDecimal(10000, 20000)
    exclude_from_statistics = False

    @factory.post_generation
    def ownerships(self, create: bool, extracted: Optional[Iterable[Ownership]], **kwargs: Any) -> None:
        if not create:
            return

        if extracted is None:
            kwargs.setdefault("sale", self)
            extracted = [OwnershipFactory.create(**kwargs)]

        for ownership in extracted:
            self.ownerships.add(ownership)

    @factory.post_generation
    def set_updated_acquisition_price(self, create, extracted, **kwargs):
        if getattr(settings, "TESTS_SHOULD_SET_UPDATED_ACQUISITION_PRICE", False):
            self.apartment.updated_acquisition_price = self.apartment.first_sale_acquisition_price
            self.apartment.save()
