from typing import NamedTuple

import pytest

from hitas.models import Owner, Ownership
from hitas.models.housing_company import RegulationStatus
from hitas.services.owner import obfuscate_owners_without_regulated_apartments
from hitas.tests.apis.helpers import parametrize_helper
from hitas.tests.factories import OwnerFactory, OwnershipFactory


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
    )
    OwnershipFactory.create(
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
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
    )
    ownership_2: Ownership = OwnershipFactory.create(
        sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )
    OwnershipFactory.create(
        owner=ownership_1.owner,
        sale__apartment__building__real_estate__housing_company=ownership_2.apartment.housing_company,
    )

    owners = obfuscate_owners_without_regulated_apartments()

    assert len(owners) == 0
