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
                    sales=[],
                ),
                is_new=True,
            ),
            "Completed in the future": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2024, 1, 1),
                    sales=[],
                ),
                is_new=True,
            ),
            "Completed in the past, no sales": IsNewParams(
                config=ApartmentConfig(
                    completion_date=datetime.date(2022, 1, 1),
                    sales=[],
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
        },
    ),
)
@pytest.mark.django_db
def test__properties__apartment__is_new(config: ApartmentConfig, is_new: bool, freezer):
    freezer.move_to("2023-01-01 00:00:00+00:00")

    apartment: Apartment = ApartmentFactory.create(completion_date=config.completion_date, sales=[])
    for sale in config.sales:
        ApartmentSaleFactory.create(apartment=apartment, purchase_date=sale.purchase_date)

    assert apartment.is_new == is_new


@pytest.mark.django_db
def test__properties__apartment__latest_purchase_date__no_sales():
    apartment: Apartment = ApartmentFactory.create(sales=[])
    assert apartment.latest_purchase_date is None


@pytest.mark.django_db
def test__properties__apartment__latest_purchase_date__single_sale():
    apartment: Apartment = ApartmentFactory.create(sales=[])
    ApartmentSaleFactory.create(apartment=apartment)
    assert apartment.latest_purchase_date is None  # Should not be set with only one sale


@pytest.mark.django_db
def test__properties__apartment__latest_purchase_date__multiple_sales():
    apartment: Apartment = ApartmentFactory.create(sales=[])
    ApartmentSaleFactory.create(apartment=apartment)
    ApartmentSaleFactory.create(apartment=apartment)
    assert apartment.latest_purchase_date is not None


class ApartmentAcquisitionPriceConfig(NamedTuple):
    primary_price: Optional[int]
    catalog_price: Optional[int]
    acquisition_price: Optional[int]


@pytest.mark.parametrize(
    **parametrize_helper(
        {
            "No catalog or first sale": ApartmentAcquisitionPriceConfig(
                primary_price=None,
                catalog_price=None,
                acquisition_price=None,
            ),
            "Catalog price but no first sale": ApartmentAcquisitionPriceConfig(
                primary_price=1000,
                catalog_price=None,
                acquisition_price=1000,
            ),
            "First sale but no catalog price": ApartmentAcquisitionPriceConfig(
                primary_price=None,
                catalog_price=1000,
                acquisition_price=1000,
            ),
            "First sale and catalog price": ApartmentAcquisitionPriceConfig(
                primary_price=2000,
                catalog_price=1000,
                acquisition_price=2000,
            ),
        },
    ),
)
@pytest.mark.django_db
def test__properties__apartment__acquisition_price(primary_price, catalog_price, acquisition_price):
    apartment: Apartment = ApartmentFactory.create(
        catalog_purchase_price=None,
        catalog_primary_loan_amount=None,
        sales=[],
    )

    if primary_price is not None:
        ApartmentSaleFactory.create(
            apartment=apartment,
            purchase_price=primary_price,
            apartment_share_of_housing_company_loans=0,
        )

    if catalog_price is not None:
        apartment.catalog_purchase_price = catalog_price
        apartment.catalog_primary_loan_amount = 0
        apartment.save()

    assert apartment.first_sale_acquisition_price == acquisition_price
