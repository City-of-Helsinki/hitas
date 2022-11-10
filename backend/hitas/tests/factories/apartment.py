import random
from datetime import date, datetime, timezone

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDecimal
from rest_framework.utils import json
from rest_framework.utils.encoders import JSONEncoder

from hitas.calculations.max_price import roundup
from hitas.models import (
    Apartment,
    ApartmentConstructionPriceImprovement,
    ApartmentMarketPriceImprovement,
    ApartmentMaximumPriceCalculation,
)
from hitas.models.apartment import ApartmentState, DepreciationPercentage
from hitas.tests.factories._base import AbstractImprovementFactory


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
    completion_date = fuzzy.FuzzyDate(date(2010, 1, 1))
    apartment_number = fuzzy.FuzzyInteger(1, 99)
    floor = factory.Faker("numerify", text="%")
    stair = factory.Faker("bothify", text="?")  # Random letter
    first_purchase_date = fuzzy.FuzzyDate(date(2010, 1, 1))
    latest_purchase_date = fuzzy.FuzzyDate(date(2010, 1, 1))
    debt_free_purchase_price = fuzzy.FuzzyInteger(100000, 200000)
    purchase_price = fuzzy.FuzzyInteger(100000, 200000)
    primary_loan_amount = fuzzy.FuzzyInteger(100000, 200000)
    additional_work_during_construction = fuzzy.FuzzyInteger(10000, 20000)
    loans_during_construction = fuzzy.FuzzyInteger(100000, 200000)
    interest_during_construction = fuzzy.FuzzyInteger(10000, 20000)
    debt_free_purchase_price_during_construction = fuzzy.FuzzyInteger(100000, 200000)
    notes = factory.Faker("text")


class ApartmentMarketPriceImprovementFactory(AbstractImprovementFactory):
    class Meta:
        model = ApartmentMarketPriceImprovement

    apartment = factory.SubFactory("hitas.tests.factories.ApartmentFactory")


class ApartmentConstructionPriceImprovementFactory(AbstractImprovementFactory):
    class Meta:
        model = ApartmentConstructionPriceImprovement

    apartment = factory.SubFactory("hitas.tests.factories.ApartmentFactory")
    depreciation_percentage = fuzzy.FuzzyChoice(state[0] for state in DepreciationPercentage.choices())


def create_apartment_max_price_calculation(**kwargs) -> ApartmentMaximumPriceCalculation:
    mpc: ApartmentMaximumPriceCalculation = ApartmentMaximumPriceCalculationFactory.create(**kwargs)

    index = fuzzy.FuzzyChoice(["market_price_index", "construction_price_index", "surface_area_price_ceiling"]).fuzz()
    completion_date = fuzzy.FuzzyDate(date(2010, 1, 1)).fuzz()
    calculation_date = fuzzy.FuzzyDate(date(2020, 1, 1)).fuzz()

    mpc_json = {
        "id": mpc.uuid.hex,
        "created_at": mpc.created_at,
        "maximum_price": mpc.maximum_price,
        "calculation_date": mpc.calculation_date,
        "valid_until": mpc.valid_until,
        "index": index,
        "calculations": {
            "construction_price_index": {
                "maximum_price": random.randint(100_000, 300_000),
                "valid_until": mpc.valid_until,
                "maximum": index == "construction_price_index",
                "calculation_variables": {
                    "acquisition_price": random.randint(100_000, 300_000),
                    "additional_work_during_construction": random.randint(0, 50_000),
                    "basic_price": random.randint(100_000, 300_000),
                    "index_adjustment": random.randint(10_000, 50_000),
                    "apartment_improvements": None,
                    "housing_company_improvements": {
                        "items": [
                            {
                                "name": factory.Faker("sentence").evaluate(None, None, {"locale": None}),
                                "value": random.randint(100_000, 200_000),
                                "value_added": random.randint(100_00, 200_00),
                                "completion_date": fuzzy.FuzzyDate(date(2010, 1, 1)).fuzz().strftime("%Y-%m"),
                                "depreciation": None,
                                "value_for_housing_company": random.randint(20_000, 30_000),
                                "value_for_apartment": random.randint(100, 1000),
                            },
                        ],
                        "summary": {
                            "value": random.randint(100_000, 200_000),
                            "value_added": random.randint(100_00, 200_00),
                            "excess": {
                                "surface_area": mpc.apartment.surface_area,
                                "value_per_square_meter": 30,
                                "total": roundup(30 * mpc.apartment.surface_area, 0),
                            },
                            "depreciation": 0,
                            "value_for_housing_company": random.randint(20_000, 30_000),
                            "value_for_apartment": random.randint(100, 1000),
                        },
                    },
                    "debt_free_price": random.randint(100_000, 300_000),
                    "debt_free_price_m2": random.randint(1_000, 10_000),
                    "apartment_share_of_housing_company_loans": random.randint(0, 50_000),
                    "apartment_share_of_housing_company_loans_date": fuzzy.FuzzyDate(date(2010, 1, 1)).fuzz(),
                    "completion_date": completion_date,
                    "completion_date_index": FuzzyDecimal(100, 300).fuzz(),
                    "calculation_date": calculation_date,
                    "calculation_date_index": FuzzyDecimal(300, 600).fuzz(),
                },
            },
            "market_price_index": {
                "maximum_price": random.randint(100_000, 300_000),
                "valid_until": mpc.valid_until,
                "maximum": index == "market_price_index",
                "calculation_variables": {
                    "acquisition_price": random.randint(100_000, 300_000),
                    "additional_work_during_construction": random.randint(0, 50_000),
                    "basic_price": random.randint(100_000, 300_000),
                    "index_adjustment": random.randint(10_000, 50_000),
                    "apartment_improvements": None,
                    "housing_company_improvements": {
                        "items": [
                            {
                                "name": factory.Faker("sentence").evaluate(None, None, {"locale": None}),
                                "value": random.randint(100_000, 200_000),
                                "value_added": random.randint(100_00, 200_00),
                                "completion_date": fuzzy.FuzzyDate(date(2010, 1, 1)).fuzz().strftime("%Y-%m"),
                                "depreciation": None,
                                "value_for_housing_company": random.randint(20_000, 30_000),
                                "value_for_apartment": random.randint(100, 1000),
                            },
                        ],
                        "summary": {
                            "value": random.randint(100_000, 200_000),
                            "value_added": random.randint(100_00, 200_00),
                            "excess": {
                                "surface_area": mpc.apartment.surface_area,
                                "value_per_square_meter": 30,
                                "total": roundup(30 * mpc.apartment.surface_area, 0),
                            },
                            "depreciation": 0,
                            "value_for_housing_company": random.randint(20_000, 30_000),
                            "value_for_apartment": random.randint(100, 1000),
                        },
                    },
                    "debt_free_price": random.randint(100_000, 300_000),
                    "debt_free_price_m2": random.randint(1_000, 10_000),
                    "apartment_share_of_housing_company_loans": random.randint(0, 50_000),
                    "apartment_share_of_housing_company_loans_date": fuzzy.FuzzyDate(date(2010, 1, 1)).fuzz(),
                    "completion_date": completion_date,
                    "completion_date_index": FuzzyDecimal(100, 300).fuzz(),
                    "calculation_date": calculation_date,
                    "calculation_date_index": FuzzyDecimal(300, 600).fuzz(),
                },
            },
            "surface_area_price_ceiling": {
                "maximum_price": random.randint(100_000, 300_000),
                "valid_until": mpc.valid_until,
                "maximum": index == "surface_area_price_ceiling",
                "calculation_variables": {
                    "calculation_date": calculation_date,
                    "calculation_date_value": FuzzyDecimal(3000, 6000).fuzz(),
                    "surface_area": mpc.apartment.surface_area,
                },
            },
        },
        "apartment": {
            "address": {
                "apartment_number": mpc.apartment.apartment_number,
                "city": mpc.apartment.city,
                "floor": mpc.apartment.floor,
                "postal_code": mpc.apartment.postal_code.value,
                "stair": mpc.apartment.stair,
                "street_address": mpc.apartment.street_address,
            },
            "type": mpc.apartment.apartment_type.value,
            "ownerships": [],
            "rooms": mpc.apartment.rooms,
            "shares": {
                "start": mpc.apartment.share_number_start,
                "end": mpc.apartment.share_number_end,
                "total": 2383,
            },
            "surface_area": 30.0,
        },
        "housing_company": {
            "archive_id": mpc.apartment.housing_company.id,
            "official_name": mpc.apartment.housing_company.official_name,
            "property_manager": {
                "name": mpc.apartment.housing_company.property_manager.name,
                "street_address": mpc.apartment.housing_company.property_manager.street_address,
            },
        },
    }
    # Encode and decode to get rid of `Decimal`, `datetime.date`, etc.
    mpc.json = json.loads(JSONEncoder().encode(mpc_json))
    mpc.save()

    return mpc


class ApartmentMaximumPriceCalculationFactory(DjangoModelFactory):
    class Meta:
        model = ApartmentMaximumPriceCalculation

    apartment = factory.SubFactory("hitas.tests.factories.ApartmentFactory")
    created_at = fuzzy.FuzzyDateTime(datetime(2010, 1, 1, tzinfo=timezone.utc))
    confirmed_at = fuzzy.FuzzyDateTime(datetime(2010, 1, 1, tzinfo=timezone.utc))

    calculation_date = fuzzy.FuzzyDate(date(2010, 1, 1))
    valid_until = fuzzy.FuzzyDate(date(2010, 1, 1))

    maximum_price = fuzzy.FuzzyInteger(100000, 200000)
    json = {}
