import datetime
import uuid

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from hitas.tests.factories.indices import (
    ConstructionPriceIndex2005Equal100Factory,
    MarketPriceIndex2005Equal100Factory,
    SurfaceAreaPriceCeilingFactory,
)


def assert_created(created: str):
    created = parse_datetime(created)
    # created timestamp is created 0-10 seconds in the past so effectively "now"
    assert 0 < (timezone.now() - created).total_seconds() < 10


def assert_id(id: str) -> uuid.UUID:
    return uuid.UUID(hex=id)


def create_necessary_indices(completion_month: datetime.date, calculation_month: datetime.date):
    assert completion_month.day == 1
    assert calculation_month.day == 1

    # Create necessary apartment's completion date indices
    ConstructionPriceIndex2005Equal100Factory.create(month=completion_month, value=129.29)
    MarketPriceIndex2005Equal100Factory.create(month=completion_month, value=167.9)

    # Create necessary calculation date indices
    ConstructionPriceIndex2005Equal100Factory.create(month=calculation_month, value=146.4)
    MarketPriceIndex2005Equal100Factory.create(month=calculation_month, value=189.1)
    SurfaceAreaPriceCeilingFactory.create(month=calculation_month, value=4869)
