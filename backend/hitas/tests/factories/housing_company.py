from datetime import date

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory

from hitas.models import (
    Building,
    HousingCompany,
    HousingCompanyConstructionPriceImprovement,
    HousingCompanyMarketPriceImprovement,
    RealEstate,
)
from hitas.models.housing_company import HitasType, RegulationStatus
from hitas.tests.factories._base import AbstractImprovementFactory


class HousingCompanyFactory(DjangoModelFactory):
    class Meta:
        model = HousingCompany

    display_name = factory.Sequence(lambda n: f"Test Housing company {n:03}")
    official_name = factory.LazyAttribute(lambda self: f"As Oy {self.display_name}")
    hitas_type = fuzzy.FuzzyChoice(state[0] for state in HitasType.choices())
    exclude_from_statistics = False
    regulation_status = RegulationStatus.REGULATED
    business_id = factory.Faker("company_business_id")
    street_address = factory.Faker("street_address")
    postal_code = factory.SubFactory("hitas.tests.factories.HitasPostalCodeFactory")
    building_type = factory.SubFactory("hitas.tests.factories.BuildingTypeFactory")
    property_manager = factory.SubFactory("hitas.tests.factories.PropertyManagerFactory")
    developer = factory.SubFactory("hitas.tests.factories.DeveloperFactory")
    acquisition_price = fuzzy.FuzzyDecimal(10000000, 99999999, precision=2)
    primary_loan = fuzzy.FuzzyDecimal(10000000, 99999999, precision=2)
    sales_price_catalogue_confirmation_date = fuzzy.FuzzyDate(date(2010, 1, 1))
    legacy_release_date = None
    notes = factory.Faker("text")


class RealEstateFactory(DjangoModelFactory):
    class Meta:
        model = RealEstate

    housing_company = factory.SubFactory("hitas.tests.factories.HousingCompanyFactory")
    property_identifier = factory.Faker("bothify", text="####-####-####-####")


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
    no_deductions = False


class HousingCompanyConstructionPriceImprovementFactory(AbstractImprovementFactory):
    class Meta:
        model = HousingCompanyConstructionPriceImprovement

    housing_company = factory.SubFactory("hitas.tests.factories.HousingCompanyFactory")
