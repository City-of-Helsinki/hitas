import random
from datetime import date
from decimal import Decimal

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from faker import Faker

from hitas.models import HousingCompany
from hitas.models.housing_company import Building, HousingCompanyState, RealEstate

fake = Faker(locale="fi_FI")


class HousingCompanyFactory(DjangoModelFactory):
    display_name = fake.last_name()
    official_name = factory.LazyAttribute(lambda self: f"As Oy {self.display_name}")
    state = HousingCompanyState.NOT_READY
    business_id = fake.company_business_id()
    street_address = fake.street_address()
    postal_code = factory.SubFactory("hitas.tests.factories.PostalCodeFactory")
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
    legacy_id = factory.Sequence(lambda n: f"{n:03}")
    notes = fake.text()
    last_modified_datetime = fuzzy.FuzzyDate(date(2010, 1, 1))
    last_modified_by = factory.SubFactory("hitas.tests.factories.UserFactory")

    class Meta:
        model = HousingCompany


class RealEstateFactory(DjangoModelFactory):
    housing_company = factory.SubFactory("hitas.tests.factories.HousingCompanyFactory")
    property_identifier = fake.bothify(fake.random_element(["####-####-####-####"]))
    street_address = fake.street_address()
    postal_code = factory.SubFactory("hitas.tests.factories.PostalCodeFactory")

    class Meta:
        model = RealEstate


class BuildingFactory(DjangoModelFactory):
    class Meta:
        model = Building

    real_estate = factory.SubFactory("hitas.tests.factories.RealEstateFactory")
    completion_date = fuzzy.FuzzyDate(date(2010, 1, 1))
    building_identifier = fake.bothify(fake.random_element(["1########?"]))
    street_address = fake.street_address()
    postal_code = factory.SubFactory("hitas.tests.factories.PostalCodeFactory")
