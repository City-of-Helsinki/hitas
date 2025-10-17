import datetime
from datetime import date
from typing import Optional

import pytest
from django.urls import reverse
from rest_framework import status

from hitas.models import (
    Apartment,
    HousingCompany,
)
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import (
    ApartmentFactory,
    HousingCompanyFactory,
)


@pytest.mark.django_db
def test__api__batch_complete_apartments__improper_range(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": 2,
        "apartment_number_end": 1,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "non_field_errors",
                "message": "Starting apartment number must be less than or equal to the ending apartment number.",
            },
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__batch_complete_apartments__no_apartments(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": 1,
        "apartment_number_end": 100,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 0,
    }


@pytest.mark.django_db
def test__api__batch_complete_apartments__single__in_range(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="1",
        completion_date=None,
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": 1,
        "apartment_number_end": 1,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 1,
    }

    apartment.refresh_from_db()
    assert apartment.completion_date == date(2020, 1, 1)


@pytest.mark.django_db
def test__api__batch_complete_apartments__single__not_in_range(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="1",
        completion_date=None,
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": 2,
        "apartment_number_end": 100,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 0,
    }

    apartment.refresh_from_db()
    assert apartment.completion_date is None


@pytest.mark.django_db
def test__api__batch_complete_apartments__single__all(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="1",
        completion_date=None,
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": None,
        "apartment_number_end": None,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 1,
    }

    apartment.refresh_from_db()
    assert apartment.completion_date == date(2020, 1, 1)


@pytest.mark.django_db
def test__api__batch_complete_apartments__single__set_not_completed(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="1",
        completion_date=datetime.date(2020, 1, 1),
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": None,
        "apartment_number_start": 1,
        "apartment_number_end": 1,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 1,
    }

    apartment.refresh_from_db()
    assert apartment.completion_date is None


@pytest.mark.django_db
def test__api__batch_complete_apartments__multiple__in_range(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment_1: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="1",
        completion_date=None,
    )
    apartment_2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="2",
        completion_date=None,
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": 1,
        "apartment_number_end": 2,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 2,
    }

    apartment_1.refresh_from_db()
    assert apartment_1.completion_date == date(2020, 1, 1)

    apartment_2.refresh_from_db()
    assert apartment_2.completion_date == date(2020, 1, 1)


@pytest.mark.django_db
def test__api__batch_complete_apartments__multiple__some_in_range(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment_1: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="1",
        completion_date=None,
    )
    apartment_2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="2",
        completion_date=None,
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": 1,
        "apartment_number_end": 1,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 1,
    }

    apartment_1.refresh_from_db()
    assert apartment_1.completion_date == date(2020, 1, 1)

    apartment_2.refresh_from_db()
    assert apartment_2.completion_date is None


@pytest.mark.django_db
def test__api__batch_complete_apartments__multiple__different_stair(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment_1: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="1",
        completion_date=None,
    )
    apartment_2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="B",
        apartment_number="1",
        completion_date=None,
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": 1,
        "apartment_number_end": 1,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()

    # Both apartments are completed, even though they are in different stairs
    # This was agreed as the current accepted behaviour, as the most common use cases
    # for this feature are covered by just selecting an apartment number range.
    assert response.json() == {
        "completed_apartment_count": 2,
    }

    apartment_1.refresh_from_db()
    assert apartment_1.completion_date == date(2020, 1, 1)

    apartment_2.refresh_from_db()
    assert apartment_2.completion_date == date(2020, 1, 1)


@pytest.mark.django_db
def test__api__batch_complete_apartments__multiple__all(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment_1: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="1",
        completion_date=None,
    )
    apartment_2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="2",
        completion_date=None,
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": None,
        "apartment_number_end": None,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 2,
    }

    apartment_1.refresh_from_db()
    assert apartment_1.completion_date == date(2020, 1, 1)

    apartment_2.refresh_from_db()
    assert apartment_2.completion_date == date(2020, 1, 1)


@pytest.mark.django_db
def test__api__batch_complete_apartments__multiple__one_already_completed(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment_1: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="1",
        completion_date=None,
    )
    apartment_2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="2",
        completion_date=date(2022, 1, 1),
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": 1,
        "apartment_number_end": 2,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 2,
    }

    apartment_1.refresh_from_db()
    assert apartment_1.completion_date == date(2020, 1, 1)

    # Completion date is changed even if set
    apartment_2.refresh_from_db()
    assert apartment_2.completion_date == date(2020, 1, 1)


@pytest.mark.parametrize(
    ["apartment_number_start", "apartment_number_end"],
    [
        (1, None),
        (None, 2),
    ],
)
@pytest.mark.django_db
def test__api__batch_complete_apartments__multiple__open_range(
    api_client: HitasAPIClient,
    apartment_number_start: Optional[int],
    apartment_number_end: Optional[int],
):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment_1: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="1",
        completion_date=None,
    )
    apartment_2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="2",
        completion_date=None,
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": apartment_number_start,
        "apartment_number_end": apartment_number_end,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 2,
    }

    apartment_1.refresh_from_db()
    assert apartment_1.completion_date == date(2020, 1, 1)

    apartment_2.refresh_from_db()
    assert apartment_2.completion_date == date(2020, 1, 1)


@pytest.mark.django_db
def test__api__batch_complete_apartments__multiple__with_letters(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment_1a: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="1a",
        completion_date=None,
    )
    apartment_1b: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="1b",
        completion_date=None,
    )
    apartment_2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="2",
        completion_date=None,
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": 1,
        "apartment_number_end": 2,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 3,
    }

    apartment_1a.refresh_from_db()
    assert apartment_1a.completion_date == date(2020, 1, 1)

    apartment_1b.refresh_from_db()
    assert apartment_1b.completion_date == date(2020, 1, 1)

    apartment_2.refresh_from_db()
    assert apartment_2.completion_date == date(2020, 1, 1)


@pytest.mark.django_db
def test__api__batch_complete_apartments__multiple__with_letters__out_of_range(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment_1: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="1",
        completion_date=None,
    )
    apartment_2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="2",
        completion_date=None,
    )
    apartment_10: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="10",
        completion_date=None,
    )
    apartment_11a: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="11a",
        completion_date=None,
    )
    apartment_11b: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number="11b",
        completion_date=None,
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": 1,
        "apartment_number_end": 2,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 2,
    }

    apartment_1.refresh_from_db()
    assert apartment_1.completion_date == date(2020, 1, 1)

    apartment_2.refresh_from_db()
    assert apartment_2.completion_date == date(2020, 1, 1)

    apartment_10.refresh_from_db()
    assert apartment_10.completion_date is None

    apartment_11a.refresh_from_db()
    assert apartment_11a.completion_date is None

    apartment_11b.refresh_from_db()
    assert apartment_11b.completion_date is None
