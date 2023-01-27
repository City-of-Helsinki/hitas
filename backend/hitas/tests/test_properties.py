import datetime
from typing import Iterable, NamedTuple, Optional

import pytest

from hitas.models import Apartment
from hitas.tests.apis.helpers import parametrize_helper
from hitas.tests.factories import ApartmentFactory, ApartmentSaleFactory


class SaleConfig(NamedTuple):
    purchase_date: Optional[datetime.date] = None


class ApartmentConfig(NamedTuple):
    completion_date: Optional[datetime.date] = None
    first_purchase_date: Optional[datetime.date] = None
    sales: Iterable[SaleConfig] = ()


class IsNewParams(NamedTuple):
    config: ApartmentConfig
    is_new: bool


@pytest.mark.parametrize(
    **parametrize_helper(
        {
            "Not completed": IsNewParams(
                config=ApartmentConfig(
                    completion_date=None,
                    first_purchase_date=None,
                    sales=[],
                ),
                is_new=True,
            ),
            "Completed in the future": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2024, 1, 1),
                    first_purchase_date=None,
                    sales=[],
                ),
                is_new=True,
            ),
            "Completed in the past, no first purchase date, no sales": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2022, 1, 1),
                    first_purchase_date=None,
                    sales=[],
                ),
                is_new=True,
            ),
            "Completed in the past, no first purchase date, sales in the future": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2022, 1, 1),
                    first_purchase_date=None,
                    sales=[
                        SaleConfig(
                            purchase_date=datetime.date(2024, 1, 1),
                        ),
                    ],
                ),
                is_new=True,
            ),
            "Completed in the past, no first purchase date, sales in the past": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2022, 1, 1),
                    first_purchase_date=None,
                    sales=[
                        SaleConfig(
                            purchase_date=datetime.date(2022, 1, 1),
                        ),
                    ],
                ),
                is_new=False,
            ),
            "Completed in the past, no first purchase date, sales in the past and future": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2022, 1, 1),
                    first_purchase_date=None,
                    sales=[
                        SaleConfig(
                            purchase_date=datetime.date(2022, 1, 1),
                        ),
                        SaleConfig(
                            purchase_date=datetime.date(2024, 1, 1),
                        ),
                    ],
                ),
                is_new=False,
            ),
            "Completed in the past, first purchase date in the future, no sales": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2022, 1, 1),
                    first_purchase_date=datetime.date(2024, 1, 1),
                    sales=[],
                ),
                is_new=True,
            ),
            "Completed in the past, first purchase date in the future, sales in the future": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2022, 1, 1),
                    first_purchase_date=datetime.date(2024, 1, 1),
                    sales=[
                        SaleConfig(
                            purchase_date=datetime.date(2024, 1, 1),
                        ),
                    ],
                ),
                is_new=True,
            ),
            "Completed in the past, first purchase date in the future, sales in the past": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2022, 1, 1),
                    first_purchase_date=datetime.date(2024, 1, 1),
                    sales=[
                        SaleConfig(
                            purchase_date=datetime.date(2022, 1, 1),
                        ),
                    ],
                ),
                is_new=False,
            ),
            "Completed in the past, first purchase date in the future, sales in the past and future": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2022, 1, 1),
                    first_purchase_date=datetime.date(2024, 1, 1),
                    sales=[
                        SaleConfig(
                            purchase_date=datetime.date(2022, 1, 1),
                        ),
                        SaleConfig(
                            purchase_date=datetime.date(2024, 1, 1),
                        ),
                    ],
                ),
                is_new=False,
            ),
            "Completed in the past, first purchase date in the past, no sales": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2022, 1, 1),
                    first_purchase_date=datetime.date(2022, 1, 1),
                    sales=[],
                ),
                is_new=False,
            ),
            "Completed in the past, first purchase date in the past, sales in the future": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2022, 1, 1),
                    first_purchase_date=datetime.date(2022, 1, 1),
                    sales=[
                        SaleConfig(
                            purchase_date=datetime.date(2024, 1, 1),
                        ),
                    ],
                ),
                is_new=False,
            ),
            "Completed in the past, first purchase date in the past, sales in the past": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2022, 1, 1),
                    first_purchase_date=datetime.date(2022, 1, 1),
                    sales=[
                        SaleConfig(
                            purchase_date=datetime.date(2022, 1, 1),
                        ),
                    ],
                ),
                is_new=False,
            ),
            "Completed in the past, first purchase date in the past, sales in the past and future": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2022, 1, 1),
                    first_purchase_date=datetime.date(2022, 1, 1),
                    sales=[
                        SaleConfig(
                            purchase_date=datetime.date(2022, 1, 1),
                        ),
                        SaleConfig(
                            purchase_date=datetime.date(2024, 1, 1),
                        ),
                    ],
                ),
                is_new=False,
            ),
        },
    ),
)
@pytest.mark.django_db
def test__properties__apartment__is_new(config: ApartmentConfig, is_new: bool, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    apartment: Apartment = ApartmentFactory.create(
        completion_date=config.completion_date,
        first_purchase_date=config.first_purchase_date,
    )
    for sale in config.sales:
        ApartmentSaleFactory.create(apartment=apartment, purchase_date=sale.purchase_date)

    assert apartment.is_new == is_new
