import datetime
from typing import Optional

import pytest

from hitas.models import Apartment, HousingCompany
from hitas.tests.apis.helpers import count_queries
from hitas.tests.factories import ApartmentFactory, BuildingFactory, HousingCompanyFactory
from hitas.utils import max_date_if_all_not_null


@pytest.mark.django_db
def test__max_date_if_all_not_null__all_completed():
    housing_company: HousingCompany = HousingCompanyFactory.create()
    ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        completion_date=datetime.date(2020, 1, 1),
    )
    apartment_2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        completion_date=datetime.date(2020, 3, 1),
    )
    ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        completion_date=datetime.date(2020, 2, 1),
    )

    with count_queries(1):
        housing_company: Optional[HousingCompany] = (
            HousingCompany.objects.filter(uuid=housing_company.uuid)
            .annotate(
                _completion_date=max_date_if_all_not_null("real_estates__buildings__apartments__completion_date"),
            )
            .first()
        )

    assert housing_company.completion_date == apartment_2.completion_date


@pytest.mark.django_db
def test__max_date_if_all_not_null__one_not_completed():
    housing_company: HousingCompany = HousingCompanyFactory.create()
    ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        completion_date=datetime.date(2020, 1, 1),
    )
    ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        completion_date=datetime.date(2020, 3, 1),
    )
    ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        completion_date=None,
    )

    with count_queries(1):
        housing_company: Optional[HousingCompany] = (
            HousingCompany.objects.filter(uuid=housing_company.uuid)
            .annotate(
                _completion_date=max_date_if_all_not_null("real_estates__buildings__apartments__completion_date"),
            )
            .first()
        )

    assert housing_company.completion_date is None


@pytest.mark.django_db
def test__max_date_if_all_not_null__one_building_empty():
    housing_company: HousingCompany = HousingCompanyFactory.create()
    ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        completion_date=datetime.date(2020, 1, 1),
    )
    apartment_2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        completion_date=datetime.date(2020, 3, 1),
    )
    BuildingFactory.create(
        real_estate__housing_company=housing_company,
    )

    with count_queries(1):
        housing_company: Optional[HousingCompany] = (
            HousingCompany.objects.filter(uuid=housing_company.uuid)
            .annotate(
                _completion_date=max_date_if_all_not_null("real_estates__buildings__apartments__completion_date"),
            )
            .first()
        )

    assert housing_company.completion_date == apartment_2.completion_date


@pytest.mark.django_db
def test__max_date_if_all_not_null__one_apartment_deleted__not_completed():
    housing_company: HousingCompany = HousingCompanyFactory.create()
    ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        completion_date=datetime.date(2020, 1, 1),
    )
    apartment_2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        completion_date=datetime.date(2020, 3, 1),
    )
    apartment_3: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        completion_date=None,
    )
    apartment_3.delete()

    with count_queries(1):
        housing_company: Optional[HousingCompany] = (
            HousingCompany.objects.filter(uuid=housing_company.uuid)
            .annotate(
                _completion_date=max_date_if_all_not_null("real_estates__buildings__apartments__completion_date"),
            )
            .first()
        )

    assert housing_company.completion_date == apartment_2.completion_date


@pytest.mark.django_db
def test__max_date_if_all_not_null__one_apartment_deleted__deleted_completed_last():
    housing_company: HousingCompany = HousingCompanyFactory.create()
    ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        completion_date=datetime.date(2020, 1, 1),
    )
    apartment_2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        completion_date=datetime.date(2020, 3, 1),
    )
    apartment_3: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        completion_date=datetime.date(2020, 4, 1),
    )
    apartment_3.delete()

    with count_queries(1):
        housing_company: Optional[HousingCompany] = (
            HousingCompany.objects.filter(uuid=housing_company.uuid)
            .annotate(
                _completion_date=max_date_if_all_not_null("real_estates__buildings__apartments__completion_date"),
            )
            .first()
        )

    assert housing_company.completion_date == apartment_2.completion_date
