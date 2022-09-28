import random
from datetime import date
from decimal import Decimal

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory

from hitas.models import (
    Building,
    HousingCompany,
    HousingCompanyConstructionPriceImprovement,
    HousingCompanyMarketPriceImprovement,
    HousingCompanyState,
    RealEstate,
)
from hitas.tests.factories._base import AbstractImprovementFactory


class HousingCompanyFactory(DjangoModelFactory):
    class Meta:
        model = HousingCompany

    id = factory.Sequence(lambda n: n)
    display_name = factory.Sequence(lambda n: f"Test Housing company {n:03}")
    official_name = factory.LazyAttribute(lambda self: f"As Oy {self.display_name}")
    state = fuzzy.FuzzyChoice(state[0] for state in HousingCompanyState.choices())
    business_id = factory.Faker("company_business_id")
    street_address = factory.Faker("street_address")
    postal_code = factory.SubFactory("hitas.tests.factories.HitasPostalCodeFactory")
    building_type = factory.SubFactory("hitas.tests.factories.BuildingTypeFactory")
    financing_method = factory.SubFactory("hitas.tests.factories.FinancingMethodFactory")
    property_manager = factory.SubFactory("hitas.tests.factories.PropertyManagerFactory")
    developer = factory.SubFactory("hitas.tests.factories.DeveloperFactory")
    acquisition_price = fuzzy.FuzzyDecimal(10000000, 99999999, precision=2)
    # Randomise realized price a bit, if housing company is ready, else set it to None
    realized_acquisition_price = factory.LazyAttribute(
        lambda self: self.state == HousingCompanyState.NOT_READY
        and None
        or round(self.acquisition_price * Decimal(random.uniform(0.5, 1.5)), 2)
    )
    primary_loan = fuzzy.FuzzyDecimal(10000000, 99999999, precision=2)
    sales_price_catalogue_confirmation_date = fuzzy.FuzzyDate(date(2010, 1, 1))
    notification_date = fuzzy.FuzzyDate(date(2010, 1, 1))
    notes = factory.Faker("text")
    last_modified_datetime = fuzzy.FuzzyDate(date(2010, 1, 1))
    last_modified_by = factory.SubFactory("hitas.tests.factories.UserFactory")


class RealEstateFactory(DjangoModelFactory):
    class Meta:
        model = RealEstate

    housing_company = factory.SubFactory("hitas.tests.factories.HousingCompanyFactory")
    property_identifier = factory.Faker("bothify", text="####-####-####-####")
    street_address = factory.Faker("street_address")


class BuildingFactory(DjangoModelFactory):
    class Meta:
        model = Building

    real_estate = factory.SubFactory("hitas.tests.factories.RealEstateFactory")
    building_identifier = factory.Faker("bothify", text="1########?")
    street_address = factory.Faker("street_address")


class HousingCompanyMarketPriceImprovementFactory(AbstractImprovementFactory):
    class Meta:
        model = HousingCompanyMarketPriceImprovement

    housing_company = factory.SubFactory("hitas.tests.factories.HousingCompanyFactory")


class HousingCompanyConstructionPriceImprovementFactory(AbstractImprovementFactory):
    class Meta:
        model = HousingCompanyConstructionPriceImprovement

    housing_company = factory.SubFactory("hitas.tests.factories.HousingCompanyFactory")
