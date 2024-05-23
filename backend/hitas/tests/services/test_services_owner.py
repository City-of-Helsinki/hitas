from typing import NamedTuple

import pytest
from django.urls import reverse
from rest_framework import status

from hitas.models import Owner, Ownership
from hitas.models.apartment import Apartment
from hitas.models.housing_company import HitasType, RegulationStatus
from hitas.services.housing_company import get_number_of_unsold_apartments
from hitas.services.owner import obfuscate_owners_without_regulated_apartments
from hitas.tests.apis.helpers import HitasAPIClient, parametrize_helper
from hitas.tests.factories import OwnerFactory, OwnershipFactory
from hitas.tests.factories.apartment import ApartmentFactory


@pytest.mark.django_db
def test_obfuscate_owners_without_regulated_apartments__empty():
    owners = obfuscate_owners_without_regulated_apartments()
    assert owners == []


@pytest.mark.django_db
def test_obfuscate_owners_without_regulated_apartments__no_ownerships__single():
    owner_1: Owner = OwnerFactory.create()

    owners = obfuscate_owners_without_regulated_apartments()

    assert len(owners) == 1

    assert owners[0]["name"] == owner_1.name
    assert owners[0]["identifier"] == owner_1.identifier
    assert owners[0]["email"] == owner_1.email

    owner_1.refresh_from_db()
    assert owner_1.name == ""
    assert owner_1.identifier is None
    assert owner_1.valid_identifier is False
    assert owner_1.email is None
    assert owner_1.bypass_conditions_of_sale is True


@pytest.mark.django_db
def test_obfuscate_owners_without_regulated_apartments__no_ownerships__multiple():
    owner_1: Owner = OwnerFactory.create()
    owner_2: Owner = OwnerFactory.create()

    owners = obfuscate_owners_without_regulated_apartments()

    assert len(owners) == 2

    assert owners[0]["name"] == owner_1.name
    assert owners[0]["identifier"] == owner_1.identifier
    assert owners[0]["email"] == owner_1.email

    assert owners[1]["name"] == owner_2.name
    assert owners[1]["identifier"] == owner_2.identifier
    assert owners[1]["email"] == owner_2.email

    owner_1.refresh_from_db()
    assert owner_1.name == ""
    assert owner_1.identifier is None
    assert owner_1.valid_identifier is False
    assert owner_1.email is None
    assert owner_1.bypass_conditions_of_sale is True

    owner_2.refresh_from_db()
    assert owner_2.name == ""
    assert owner_2.identifier is None
    assert owner_2.valid_identifier is False
    assert owner_2.email is None
    assert owner_2.bypass_conditions_of_sale is True


class ObfuscationTestInfo(NamedTuple):
    regulation_status: RegulationStatus
    obfuscated: bool


@pytest.mark.parametrize(
    **parametrize_helper(
        {
            "NOT_READY": ObfuscationTestInfo(
                regulation_status=RegulationStatus.REGULATED,
                obfuscated=False,
            ),
            "RELEASED_BY_HITAS": ObfuscationTestInfo(
                regulation_status=RegulationStatus.RELEASED_BY_HITAS,
                obfuscated=True,
            ),
            "RELEASED_BY_PLOT_DEPARTMENT": ObfuscationTestInfo(
                regulation_status=RegulationStatus.RELEASED_BY_PLOT_DEPARTMENT,
                obfuscated=True,
            ),
        }
    ),
)
@pytest.mark.django_db
def test_obfuscate_owners_without_regulated_apartments__housing_company_regulation_status(
    regulation_status, obfuscated
):
    ownership: Ownership = OwnershipFactory.create(
        sale__apartment__building__real_estate__housing_company__regulation_status=regulation_status,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )

    owners = obfuscate_owners_without_regulated_apartments()

    if obfuscated:
        assert len(owners) == 1

        assert owners[0]["name"] == ownership.owner.name
        assert owners[0]["identifier"] == ownership.owner.identifier
        assert owners[0]["email"] == ownership.owner.email

    else:
        assert len(owners) == 0


@pytest.mark.django_db
def test_obfuscate_owners_without_regulated_apartments__one_owns_regulated():
    ownership: Ownership = OwnershipFactory.create(
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.RELEASED_BY_HITAS,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    OwnershipFactory.create(
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )

    owners = obfuscate_owners_without_regulated_apartments()

    assert len(owners) == 1

    assert owners[0]["name"] == ownership.owner.name
    assert owners[0]["identifier"] == ownership.owner.identifier
    assert owners[0]["email"] == ownership.owner.email


@pytest.mark.django_db
def test_obfuscate_owners_without_regulated_apartments__one_owns_one_regulated_and_one_released():
    ownership_1: Ownership = OwnershipFactory.create(
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.RELEASED_BY_HITAS,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    ownership_2: Ownership = OwnershipFactory.create(
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    OwnershipFactory.create(
        owner=ownership_1.owner,
        sale__apartment__building__real_estate__housing_company=ownership_2.apartment.housing_company,
        sale__apartment__building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )

    owners = obfuscate_owners_without_regulated_apartments()

    assert len(owners) == 0


@pytest.mark.django_db
def test_obfuscate_owners_without_regulated_apartments__half_hitas_sales_after_regulation_released(
    api_client: HitasAPIClient,
):
    # Unsold apartment in a released half hitas housing company
    apartment: Apartment = ApartmentFactory.create(
        sales=[],
        building__real_estate__housing_company__regulation_status=RegulationStatus.RELEASED_BY_HITAS,
        building__real_estate__housing_company__hitas_type=HitasType.HALF_HITAS,
    )

    unsold_apartments_count = get_number_of_unsold_apartments(apartment.housing_company)
    assert unsold_apartments_count == 1

    # Create a sale for the apartment through the API so that it passes through validation
    owner: Owner = OwnerFactory.create()
    data = {
        "ownerships": [
            {
                "owner": {
                    "id": owner.uuid.hex,
                },
                "percentage": 100.0,
            },
        ],
        "notification_date": "2022-01-01",
        "purchase_date": "2022-01-01",
        "purchase_price": 100_000,
        "apartment_share_of_housing_company_loans": 50_000,
        "exclude_from_statistics": True,
    }
    url = reverse(
        "hitas:apartment-sale-list",
        kwargs={
            "housing_company_uuid": apartment.housing_company.uuid.hex,
            "apartment_uuid": apartment.uuid.hex,
        },
    )
    response = api_client.post(url, data=data, format="json")
    response_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED, response_data

    unsold_apartments_count = get_number_of_unsold_apartments(apartment.housing_company)
    assert unsold_apartments_count == 0

    # See that owner is obfuscated in the next regulation round
    owners = obfuscate_owners_without_regulated_apartments()
    assert len(owners) == 1
