import datetime
from typing import Iterable, NamedTuple, Optional

import pytest

from hitas.models import Apartment, ApartmentSale, ConditionOfSale
from hitas.tests.apis.helpers import parametrize_helper
from hitas.tests.factories import ApartmentFactory, ApartmentSaleFactory


class SaleConfig(NamedTuple):
    purchase_date: Optional[datetime.date] = None


class ApartmentConfig(NamedTuple):
    completion_date: Optional[datetime.date] = None
    sales: Iterable[SaleConfig] = ()
    conditions_of_sale_new: bool = False
    conditions_of_sale_old: bool = False


class IsNewParams(NamedTuple):
    config: ApartmentConfig
    is_new: bool


@pytest.mark.parametrize(
    **parametrize_helper(
        {
            "Not completed": IsNewParams(
                config=ApartmentConfig(
                    completion_date=None,
                ),
                is_new=True,
            ),
            "Completed in the future": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2024, 1, 1),
                ),
                is_new=True,
            ),
            "Completed in the past, no sales": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2022, 1, 1),
                ),
                is_new=True,
            ),
            "Completed in the past, sales in the future": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2022, 1, 1),
                    sales=[
                        SaleConfig(
                            purchase_date=datetime.date(2024, 1, 1),
                        ),
                    ],
                ),
                is_new=True,
            ),
            "Completed in the past, sales in the past": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2022, 1, 1),
                    sales=[
                        SaleConfig(
                            purchase_date=datetime.date(2022, 1, 1),
                        ),
                    ],
                ),
                is_new=False,
            ),
            "Completed in the past, sales in the past and future": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2022, 1, 1),
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
            "Completed, sales in the past, has conditions of sale where new": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2022, 1, 1),
                    sales=[
                        SaleConfig(
                            purchase_date=datetime.date(2022, 1, 1),
                        ),
                    ],
                    conditions_of_sale_new=True,
                ),
                is_new=True,
            ),
            "Completed, sales in the past, has conditions of sale where old": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2022, 1, 1),
                    sales=[
                        SaleConfig(
                            purchase_date=datetime.date(2022, 1, 1),
                        ),
                    ],
                    conditions_of_sale_old=True,
                ),
                is_new=False,
            ),
        },
    ),
)
@pytest.mark.django_db
def test__properties__apartment__is_new(config: ApartmentConfig, is_new: bool, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    apartment: Apartment = ApartmentFactory.create(completion_date=config.completion_date, sales=[])
    for sale_config in config.sales:
        ApartmentSaleFactory.create(apartment=apartment, purchase_date=sale_config.purchase_date)

    if config.conditions_of_sale_new:
        sale: ApartmentSale = ApartmentSaleFactory.create()
        ConditionOfSale.objects.create(
            new_ownership=apartment.first_sale().ownerships.first(),
            old_ownership=sale.ownerships.first(),
        )

    if config.conditions_of_sale_old:
        sale: ApartmentSale = ApartmentSaleFactory.create()
        ConditionOfSale.objects.create(
            new_ownership=sale.ownerships.first(),
            old_ownership=apartment.first_sale().ownerships.first(),
        )

    assert apartment.is_new == is_new


@pytest.mark.django_db
def test__properties__apartment__purchase_dates__no_sales():
    apartment: Apartment = ApartmentFactory.create(sales=[])
    assert apartment.latest_purchase_date is None


@pytest.mark.django_db
def test__properties__apartment__purchase_dates__single_sale():
    apartment: Apartment = ApartmentFactory.create(sales=[])
    sale: ApartmentSale = ApartmentSaleFactory.create(apartment=apartment)
    assert apartment.first_purchase_date == sale.purchase_date
    assert apartment.latest_purchase_date is None  # Should not be set with only one sale


@pytest.mark.django_db
def test__properties__apartment__purchase_dates__multiple_sales():
    apartment: Apartment = ApartmentFactory.create(sales=[])
    sale_1: ApartmentSale = ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=datetime.date(2022, 1, 1),
    )
    sale_2: ApartmentSale = ApartmentSaleFactory.create(
        apartment=apartment,
        purchase_date=datetime.date(2022, 2, 1),
    )
    assert apartment.first_purchase_date == sale_1.purchase_date
    assert apartment.latest_purchase_date == sale_2.purchase_date
