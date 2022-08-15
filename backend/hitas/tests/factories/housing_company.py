import random
from datetime import date
from decimal import Decimal

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory

from hitas.models import Apartment, Building, HousingCompany, HousingCompanyState, RealEstate
from hitas.models.apartment import ApartmentState


class HousingCompanyFactory(DjangoModelFactory):
    class Meta:
        model = HousingCompany

    display_name = factory.Faker("last_name")
    official_name = factory.LazyAttribute(lambda self: f"As Oy {self.display_name}")
    state = HousingCompanyState.NOT_READY
    business_id = factory.Faker("company_business_id")
    street_address = factory.Faker("street_address")
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
    notes = factory.Faker("text")
    last_modified_datetime = fuzzy.FuzzyDate(date(2010, 1, 1))
    last_modified_by = factory.SubFactory("hitas.tests.factories.UserFactory")


class RealEstateFactory(DjangoModelFactory):
    class Meta:
        model = RealEstate

    housing_company = factory.SubFactory("hitas.tests.factories.HousingCompanyFactory")
    property_identifier = factory.Faker("bothify", text="####-####-####-####")
    street_address = factory.Faker("street_address")
    postal_code = factory.SubFactory("hitas.tests.factories.PostalCodeFactory")


class BuildingFactory(DjangoModelFactory):
    class Meta:
        model = Building

    real_estate = factory.SubFactory("hitas.tests.factories.RealEstateFactory")
    completion_date = fuzzy.FuzzyDate(date(2010, 1, 1))
    building_identifier = factory.Faker("bothify", text="1########?")
    street_address = factory.Faker("street_address")
    postal_code = factory.SubFactory("hitas.tests.factories.PostalCodeFactory")


class ApartmentFactory(DjangoModelFactory):
    class Meta:
        model = Apartment

    building = factory.SubFactory("hitas.tests.factories.BuildingFactory")
    state = fuzzy.FuzzyChoice(state[0] for state in ApartmentState.choices())
    apartment_type = factory.SubFactory("hitas.tests.factories.ApartmentTypeFactory")
    surface_area = fuzzy.FuzzyDecimal(10, 99, precision=2)
    share_number_start = factory.Sequence(lambda n: n * 50)
    share_number_end = factory.LazyAttribute(lambda self: (self.share_number_start + 50))
    street_address = factory.Faker("street_address")
    postal_code = factory.SubFactory("hitas.tests.factories.PostalCodeFactory")
    apartment_number = fuzzy.FuzzyInteger(1, 99)
    floor = fuzzy.FuzzyInteger(1, 9)
    stair = factory.Faker("bothify", text="?")  # Random letter
    debt_free_purchase_price = fuzzy.FuzzyDecimal(100000, 200000, precision=2)
    purchase_price = fuzzy.FuzzyDecimal(100000, 200000, precision=2)
    acquisition_price = fuzzy.FuzzyDecimal(100000, 200000, precision=2)
    primary_loan_amount = fuzzy.FuzzyDecimal(100000, 200000, precision=2)
    loans_during_construction = fuzzy.FuzzyDecimal(100000, 200000, precision=2)
    interest_during_construction = fuzzy.FuzzyDecimal(10000, 20000, precision=2)
    notes = factory.Faker("text")
