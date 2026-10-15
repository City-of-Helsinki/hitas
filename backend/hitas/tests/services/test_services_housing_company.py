import datetime
from decimal import Decimal

import pytest

from hitas.models import Apartment, ApartmentSale
from hitas.models.housing_company import HitasType, RegulationStatus
from hitas.services.housing_company import get_completed_housing_companies
from hitas.tests.factories import ApartmentFactory, ApartmentSaleFactory


@pytest.fixture
def unsold_apartment(db) -> Apartment:
    return ApartmentFactory.create(
        sales=[],
        completion_date=datetime.date(2025, 12, 12),
        surface_area=Decimal("50"),
        catalog_purchase_price=Decimal("149082"),
        catalog_primary_loan_amount=Decimal("109095"),
        updated_acquisition_price=None,
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        building__real_estate__housing_company__exclude_from_statistics=False,
    )


@pytest.mark.django_db
def test_get_completed_housing_companies__cancelled_sale_uses_catalog_price(unsold_apartment: Apartment):
    sale = ApartmentSaleFactory.create(
        apartment=unsold_apartment,
        purchase_date=datetime.date(2026, 1, 1),
        purchase_price=Decimal("140000"),
        apartment_share_of_housing_company_loans=Decimal("100000"),
        ownerships=[],
    )
    sale.delete()

    # A cancelled sale remains in the database, but is not an active first sale.
    assert not unsold_apartment.sales.exists()
    assert ApartmentSale.deleted_objects.filter(pk=sale.pk).exists()

    housing_companies = get_completed_housing_companies(
        completion_month=datetime.date(2026, 8, 1),
        include_excluded_from_statistics=False,
        include_rental_hitas=False,
        select_half_hitas=False,
    )

    assert len(housing_companies) == 1
    assert housing_companies[0].pk == unsold_apartment.housing_company.pk
    assert housing_companies[0].realized_acquisition_price == Decimal("258177")


@pytest.mark.django_db
def test_get_completed_housing_companies__unsold_updated_price_is_counted_once(unsold_apartment: Apartment):
    # Use an override different from the catalogue price to verify precedence.
    unsold_apartment.updated_acquisition_price = Decimal("260000")
    unsold_apartment.save(update_fields=["updated_acquisition_price"])
    assert not unsold_apartment.sales.exists()

    housing_companies = get_completed_housing_companies(
        completion_month=datetime.date(2026, 8, 1),
        include_excluded_from_statistics=False,
        include_rental_hitas=False,
        select_half_hitas=False,
    )

    assert len(housing_companies) == 1
    assert housing_companies[0].pk == unsold_apartment.housing_company.pk
    assert housing_companies[0].realized_acquisition_price == Decimal("260000")
