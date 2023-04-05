from datetime import date, datetime, timezone
from typing import Any, Collection, Optional

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDate, FuzzyDecimal

from hitas.calculations.max_prices.max_price import calculate_max_price, fetch_apartment
from hitas.models import (
    Apartment,
    ApartmentConstructionPriceImprovement,
    ApartmentMarketPriceImprovement,
    ApartmentMaximumPriceCalculation,
    ApartmentSale,
)
from hitas.models.apartment import ApartmentState, DepreciationPercentage
from hitas.models.housing_company import HitasType
from hitas.tests.factories._base import AbstractImprovementFactory
from hitas.tests.factories.apartment_sale import ApartmentSaleFactory
from hitas.tests.factories.indices import (
    ConstructionPriceIndex2005Equal100Factory,
    MarketPriceIndex2005Equal100Factory,
    SurfaceAreaPriceCeilingFactory,
)
from hitas.utils import monthify


class ApartmentFactory(DjangoModelFactory):
    class Meta:
        model = Apartment

    building = factory.SubFactory("hitas.tests.factories.BuildingFactory")
    state = fuzzy.FuzzyChoice(state[0] for state in ApartmentState.choices())
    apartment_type = factory.SubFactory("hitas.tests.factories.ApartmentTypeFactory")
    surface_area = fuzzy.FuzzyDecimal(10, 99, precision=2)
    rooms = fuzzy.FuzzyInteger(1, 9)
    share_number_start = factory.Sequence(lambda n: n * 50 + 1)
    share_number_end = factory.LazyAttribute(lambda self: (self.share_number_start + 50))
    street_address = factory.Faker("street_address")
    completion_date = fuzzy.FuzzyDate(date(2011, 1, 1))
    apartment_number = fuzzy.FuzzyInteger(1, 99)
    floor = factory.Faker("numerify", text="%")
    stair = factory.Faker("bothify", text="?")  # Random letter
    catalog_purchase_price = fuzzy.FuzzyDecimal(100000, 200000)
    catalog_primary_loan_amount = fuzzy.FuzzyDecimal(100000, 200000)
    additional_work_during_construction = fuzzy.FuzzyDecimal(10000, 20000)
    loans_during_construction = fuzzy.FuzzyDecimal(100000, 200000)
    interest_during_construction_6 = fuzzy.FuzzyDecimal(10000, 20000)
    interest_during_construction_14 = fuzzy.FuzzyDecimal(20000, 30000)
    debt_free_purchase_price_during_construction = fuzzy.FuzzyDecimal(100000, 200000)
    notes = factory.Faker("text")

    @factory.post_generation
    def sales(self, create: bool, extracted: Optional[Collection[ApartmentSale]], **kwargs: Any) -> None:
        if not create:
            return

        if extracted is None:
            kwargs.setdefault("apartment", self)
            extracted = [ApartmentSaleFactory.create(**kwargs)]

        for ownership in extracted:
            self.sales.add(ownership)


class ApartmentMarketPriceImprovementFactory(AbstractImprovementFactory):
    class Meta:
        model = ApartmentMarketPriceImprovement

    apartment = factory.SubFactory("hitas.tests.factories.ApartmentFactory")
    no_deductions = False


class ApartmentConstructionPriceImprovementFactory(AbstractImprovementFactory):
    class Meta:
        model = ApartmentConstructionPriceImprovement

    apartment = factory.SubFactory("hitas.tests.factories.ApartmentFactory")
    depreciation_percentage = fuzzy.FuzzyChoice(state[0] for state in DepreciationPercentage.choices())


def create_apartment_max_price_calculation(create_indices=True, **kwargs) -> ApartmentMaximumPriceCalculation:
    if "apartment__completion_date" not in kwargs:
        kwargs["apartment__completion_date"] = FuzzyDate(date(2011, 1, 1), date(2015, 1, 1)).fuzz()
    if "calculation_date" not in kwargs:
        kwargs["calculation_date"] = FuzzyDate(date(2015, 1, 1)).fuzz()

    if kwargs["calculation_date"] < date(2011, 1, 1):
        kwargs["apartment__building__real_estate__housing_company__hitas_type"] = HitasType.HITAS_I
    else:
        kwargs["apartment__building__real_estate__housing_company__hitas_type"] = HitasType.NEW_HITAS_I

    # Create indices for `calculate_max_price`
    if create_indices:
        for index_factory in [
            ConstructionPriceIndex2005Equal100Factory,
            MarketPriceIndex2005Equal100Factory,
            SurfaceAreaPriceCeilingFactory,
        ]:
            completion_date_index = index_factory.create(month=monthify(kwargs["apartment__completion_date"]))
            index_factory.create(
                month=monthify(kwargs["calculation_date"]),
                value=completion_date_index.value + FuzzyDecimal(1, 300).fuzz(),
            )

    # Create max price calculation
    mpc: ApartmentMaximumPriceCalculation = ApartmentMaximumPriceCalculationFactory.create(**kwargs)
    mpc.json = calculate_max_price(
        apartment=fetch_apartment(mpc.apartment.housing_company.uuid, mpc.apartment.uuid, mpc.calculation_date),
        apartment_share_of_housing_company_loans=fuzzy.FuzzyInteger(0, 5000).fuzz(),
        apartment_share_of_housing_company_loans_date=fuzzy.FuzzyDate(date(2020, 1, 1)).fuzz(),
        calculation_date=mpc.calculation_date,
    )
    mpc.save()
    # Refresh to make sure the JSON is encoded
    mpc.refresh_from_db()

    return mpc


class ApartmentMaximumPriceCalculationFactory(DjangoModelFactory):
    class Meta:
        model = ApartmentMaximumPriceCalculation

    apartment = factory.SubFactory("hitas.tests.factories.ApartmentFactory")
    created_at = fuzzy.FuzzyDateTime(datetime(2010, 1, 1, tzinfo=timezone.utc))
    confirmed_at = fuzzy.FuzzyDateTime(datetime(2010, 1, 1, tzinfo=timezone.utc))

    calculation_date = fuzzy.FuzzyDate(date(2010, 1, 1))
    valid_until = fuzzy.FuzzyDate(date(2010, 1, 1))

    maximum_price = fuzzy.FuzzyDecimal(100000, 200000)
    json = {}
