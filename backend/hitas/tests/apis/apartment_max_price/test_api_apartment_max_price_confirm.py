import datetime
import uuid

import pytest
from django.urls import reverse
from rest_framework import status

from hitas.models import Apartment, ApartmentMaxPriceCalculation, HousingCompany
from hitas.tests.apis.apartment_max_price.utils import assert_created, create_necessary_indices
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import ApartmentFactory, HousingCompanyFactory, OwnershipFactory
from hitas.tests.factories.apartment import ApartmentMaxPriceCalculationFactory


@pytest.mark.django_db
def test__api__apartment_max_price__confirm(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2019, 11, 27),
    )
    OwnershipFactory.create(apartment=a, percentage=100)

    create_necessary_indices(
        completion_month=datetime.date(2019, 11, 1),
        calculation_month=datetime.date(2022, 7, 1),
    )

    # Create few unconfirmed calculations that gets removed after confirmation
    unconfirmed_mpc: ApartmentMaxPriceCalculation = ApartmentMaxPriceCalculationFactory.create(
        confirmed_at=None, apartment=a
    )
    unconfirmed_mpc2: ApartmentMaxPriceCalculation = ApartmentMaxPriceCalculationFactory.create(
        confirmed_at=None, apartment=a
    )
    unconfirmed_mpc_other_apartment: ApartmentMaxPriceCalculation = ApartmentMaxPriceCalculationFactory.create(
        confirmed_at=None,
        apartment=ApartmentFactory.create(
            building__real_estate__housing_company=a.housing_company,
        ),
    )
    unconfirmed_mpc_other_hc: ApartmentMaxPriceCalculation = ApartmentMaxPriceCalculationFactory.create(
        confirmed_at=None
    )

    # Create one confirmed calculation so that it's possible to verify the apartment's max price gets updated with the
    # latest calculation
    confirmed_mpc: ApartmentMaxPriceCalculation = ApartmentMaxPriceCalculationFactory.create(apartment=a)

    data = {
        "calculation_date": "2022-07-05",
        "apartment_share_of_housing_company_loans": 2500,
    }

    # Create max price calculation
    create_response = api_client.post(
        reverse("hitas:maximum-price-list", args=[a.housing_company.uuid.hex, a.uuid.hex]), data=data, format="json"
    )
    assert create_response.status_code == status.HTTP_200_OK, create_response.json()
    create_json = create_response.json()
    mpc_id = create_json.get("id")

    # Verify the `confirmed_at` is not yet set
    assert create_json.pop("confirmed_at") is None

    # Confirm the created max price calculation
    retrieve_response = api_client.put(
        reverse("hitas:maximum-price-detail", args=[a.housing_company.uuid.hex, a.uuid.hex, mpc_id]),
        data={"confirm": True},
        format="json",
    )
    assert retrieve_response.status_code == status.HTTP_200_OK, retrieve_response.json()
    retrieve_json = retrieve_response.json()

    # Verify `confirmed_at` has been updated
    assert_created(retrieve_json.pop("confirmed_at"))

    # Verify the response matches to previous response
    assert create_json == retrieve_json

    # Fetch apartment
    apartment_detail = api_client.get(reverse("hitas:apartment-detail", args=[a.housing_company.uuid.hex, a.uuid.hex]))
    assert apartment_detail.status_code == status.HTTP_200_OK, apartment_detail.json()
    apartment_json = apartment_detail.json()

    # Verify the apartment has now a confirmed max price
    confirmed_price = apartment_json["prices"]["max_prices"]["confirmed"]
    assert_created(confirmed_price.pop("confirmed_at"))
    assert confirmed_price == {
        "id": mpc_id,
        "created_at": retrieve_json["created_at"],
        "calculation_date": retrieve_json["calculation_date"],
        "max_price": retrieve_json["max_price"],
        "valid": {"is_valid": False, "valid_until": retrieve_json["valid_until"]},
    }

    # Verify unconfirmed calculations were deleted
    assert ApartmentMaxPriceCalculation.objects.filter(id=unconfirmed_mpc.id).first() is None
    assert ApartmentMaxPriceCalculation.objects.filter(id=unconfirmed_mpc2.id).first() is None

    # Verify confirmed calculations were *not* deleted
    ApartmentMaxPriceCalculation.objects.get(id=confirmed_mpc.id)

    # Verify unconfirmed calculations for other housing companies or apartments were *not* deleted
    ApartmentMaxPriceCalculation.objects.get(id=unconfirmed_mpc_other_apartment.id)
    ApartmentMaxPriceCalculation.objects.get(id=unconfirmed_mpc_other_hc.id)


@pytest.mark.django_db
def test__api__apartment_max_price__confirm__false(api_client: HitasAPIClient):
    mpc: ApartmentMaxPriceCalculation = ApartmentMaxPriceCalculationFactory.create(confirmed_at=None)

    # Create max price calculation
    create_response = api_client.put(
        reverse(
            "hitas:maximum-price-detail",
            args=[mpc.apartment.housing_company.uuid.hex, mpc.apartment.uuid.hex, mpc.uuid.hex],
        ),
        data={"confirm": False},
        format="json",
    )
    assert create_response.status_code == status.HTTP_204_NO_CONTENT

    # Verify the calculation was removed
    assert ApartmentMaxPriceCalculation.objects.filter(id=mpc.id).first() is None


@pytest.mark.django_db
def test__api__apartment_max_price__confirm__already_confirmed(api_client: HitasAPIClient):
    mpc: ApartmentMaxPriceCalculation = ApartmentMaxPriceCalculationFactory.create()

    # Create max price calculation
    create_response = api_client.put(
        reverse(
            "hitas:maximum-price-detail",
            args=[mpc.apartment.housing_company.uuid.hex, mpc.apartment.uuid.hex, mpc.uuid.hex],
        ),
        data={"confirm": True},
        format="json",
    )
    assert create_response.status_code == status.HTTP_409_CONFLICT, create_response.json()
    assert create_response.json() == {
        "error": "already_confirmed",
        "message": "Maximum price calculation has already been confirmed.",
        "reason": "Conflict",
        "status": 409,
    }


@pytest.mark.django_db
def test__api__apartment_max_price__confirm__incorrect_housing_company_uuid(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2019, 11, 27),
    )
    other_hc: HousingCompany = HousingCompanyFactory.create()
    mpc: ApartmentMaxPriceCalculation = ApartmentMaxPriceCalculationFactory.create(confirmed_at=None, apartment=a)

    # Create max price calculation
    create_response = api_client.put(
        reverse("hitas:maximum-price-detail", args=[other_hc.uuid.hex, a.uuid.hex, mpc.uuid.hex]),
        data={"confirm": True},
        format="json",
    )
    assert create_response.status_code == status.HTTP_404_NOT_FOUND, create_response.json()
    assert create_response.json() == {
        "error": "apartment_not_found",
        "message": "Apartment not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__apartment_max_price__confirm__nonexistent_housing_company_uuid(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2019, 11, 27),
    )
    mpc: ApartmentMaxPriceCalculation = ApartmentMaxPriceCalculationFactory.create(confirmed_at=None, apartment=a)

    # Create max price calculation
    create_response = api_client.put(
        reverse("hitas:maximum-price-detail", args=[uuid.uuid4().hex, a.uuid.hex, mpc.uuid.hex]),
        data={"confirm": True},
        format="json",
    )
    assert create_response.status_code == status.HTTP_404_NOT_FOUND, create_response.json()
    assert create_response.json() == {
        "error": "housing_company_not_found",
        "message": "Housing company not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__apartment_max_price__confirm__incorrect_apartment_id(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2019, 11, 27),
    )
    mpc: ApartmentMaxPriceCalculation = ApartmentMaxPriceCalculationFactory.create(confirmed_at=None, apartment=a)
    a2: Apartment = ApartmentFactory.create(building__real_estate__housing_company=a.housing_company)

    # Create max price calculation
    create_response = api_client.put(
        reverse("hitas:maximum-price-detail", args=[a.housing_company.uuid.hex, a2.uuid.hex, mpc.uuid.hex]),
        data={"confirm": True},
        format="json",
    )
    assert create_response.status_code == status.HTTP_404_NOT_FOUND, create_response.json()
    assert create_response.json() == {
        "error": "apartment_maximum_price_calculation_not_found",
        "message": "Apartment maximum price calculation not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__apartment_max_price__confirm__nonexistent_apartment_id(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2019, 11, 27),
    )
    mpc: ApartmentMaxPriceCalculation = ApartmentMaxPriceCalculationFactory.create(confirmed_at=None, apartment=a)

    # Create max price calculation
    create_response = api_client.put(
        reverse("hitas:maximum-price-detail", args=[a.housing_company.uuid.hex, uuid.uuid4().hex, mpc.uuid.hex]),
        data={"confirm": True},
        format="json",
    )
    assert create_response.status_code == status.HTTP_404_NOT_FOUND, create_response.json()
    assert create_response.json() == {
        "error": "apartment_not_found",
        "message": "Apartment not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__apartment_max_price__confirm__nonexistent_calculation_id(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2019, 11, 27),
    )
    ApartmentMaxPriceCalculationFactory.create(confirmed_at=None, apartment=a)

    # Create max price calculation
    create_response = api_client.put(
        reverse("hitas:maximum-price-detail", args=[a.housing_company.uuid.hex, a.uuid.hex, uuid.uuid4().hex]),
        data={"confirm": True},
        format="json",
    )
    assert create_response.status_code == status.HTTP_404_NOT_FOUND, create_response.json()
    assert create_response.json() == {
        "error": "apartment_maximum_price_calculation_not_found",
        "message": "Apartment maximum price calculation not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__apartment_max_price__confirm__invalid_id(api_client: HitasAPIClient):
    a: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2019, 11, 27),
    )
    ApartmentMaxPriceCalculationFactory.create(confirmed_at=None, apartment=a)
    mpc2: ApartmentMaxPriceCalculation = ApartmentMaxPriceCalculationFactory.create(confirmed_at=None)

    # Create max price calculation
    create_response = api_client.put(
        reverse("hitas:maximum-price-detail", args=[a.housing_company.uuid.hex, a.uuid.hex, mpc2.uuid.hex]),
        data={"confirm": True},
        format="json",
    )
    assert create_response.status_code == status.HTTP_404_NOT_FOUND, create_response.json()
    assert create_response.json() == {
        "error": "apartment_maximum_price_calculation_not_found",
        "message": "Apartment maximum price calculation not found",
        "reason": "Not Found",
        "status": 404,
    }
