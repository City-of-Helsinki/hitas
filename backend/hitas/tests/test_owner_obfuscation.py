import re

import pytest

from hitas.models import Owner
from hitas.tests.factories import OwnerFactory


@pytest.mark.django_db
def test_owner_obfuscation__model__obfuscate():
    OwnerFactory.create(
        name="Testi Testinen",
        identifier="123456-789A",
        email=None,
        non_disclosure=True,
    )

    owner = Owner.objects.first()

    assert owner.name == ""
    assert owner.identifier is None
    assert owner.email is None

    assert owner._unobfuscated_data == {"name": "Testi Testinen", "identifier": "123456-789A", "email": None}


@pytest.mark.django_db
def test_owner_obfuscation__model__dont_obfuscate():
    OwnerFactory.create(
        name="Testi Testinen",
        identifier="123456-789A",
        email=None,
        non_disclosure=False,
    )

    owner = Owner.objects.first()

    assert owner.name == "Testi Testinen"
    assert owner.identifier == "123456-789A"
    assert owner.email is None

    assert not hasattr(owner, "_unobfuscated_data")


@pytest.mark.django_db
def test_owner_obfuscation__values__obfuscate():
    OwnerFactory.create(
        name="Testi Testinen",
        identifier="123456-789A",
        email=None,
        non_disclosure=True,
    )

    owner = Owner.objects.values("name", "identifier", "email", "non_disclosure").first()

    assert owner["name"] == ""
    assert owner["identifier"] is None
    assert owner["email"] is None

    # No cache created when using values()
    assert not hasattr(owner, "_unobfuscated_data")


@pytest.mark.django_db
def test_owner_obfuscation__values__obfuscate__non_disclosure_missing():
    OwnerFactory.create(
        name="Testi Testinen",
        identifier="123456-789A",
        email=None,
        non_disclosure=True,
    )

    msg = (
        "Due to owner obfuscation, 'non_disclosure' field should always be included "
        "when fetching owners. Field not found in fields: ('name', 'identifier', 'email')"
    )

    with pytest.raises(RuntimeError, match=re.escape(msg)):
        Owner.objects.values("name", "identifier", "email").first()


@pytest.mark.django_db
def test_owner_obfuscation__values__dont_obfuscate():
    OwnerFactory.create(
        name="Testi Testinen",
        identifier="123456-789A",
        email=None,
        non_disclosure=False,
    )

    # non_disclosure missing, we assume owner should be obfuscated
    owner = Owner.objects.values("name", "identifier", "email", "non_disclosure").first()

    assert owner["name"] == "Testi Testinen"
    assert owner["identifier"] == "123456-789A"
    assert owner["email"] is None

    # No cache created when using values()
    assert not hasattr(owner, "_unobfuscated_data")


@pytest.mark.django_db
def test_owner_obfuscation__values_list__obfuscate():
    OwnerFactory.create(
        name="Testi Testinen",
        identifier="123456-789A",
        email=None,
        non_disclosure=True,
    )

    owner = Owner.objects.values_list("name", "identifier", "email", "non_disclosure").first()

    assert owner[0] == ""
    assert owner[1] is None
    assert owner[2] is None

    # No cache created when using values_list()
    assert not hasattr(owner, "_unobfuscated_data")


@pytest.mark.django_db
def test_owner_obfuscation__values_list__obfuscate__non_disclosure_missing():
    OwnerFactory.create(
        name="Testi Testinen",
        identifier="123456-789A",
        email=None,
        non_disclosure=True,
    )

    msg = (
        "Due to owner obfuscation, 'non_disclosure' field should always be included "
        "when fetching owners. Field not found in fields: ('name', 'identifier', 'email')"
    )

    with pytest.raises(RuntimeError, match=re.escape(msg)):
        Owner.objects.values_list("name", "identifier", "email").first()


@pytest.mark.django_db
def test_owner_obfuscation__values_list__dont_obfuscate():
    OwnerFactory.create(
        name="Testi Testinen",
        identifier="123456-789A",
        email=None,
        non_disclosure=False,
    )

    owner = Owner.objects.values_list("name", "identifier", "email", "non_disclosure").first()

    assert owner[0] == "Testi Testinen"
    assert owner[1] == "123456-789A"
    assert owner[2] is None

    # No cache created when using values_list()
    assert not hasattr(owner, "_unobfuscated_data")


@pytest.mark.django_db
def test_owner_obfuscation__values_list_flat():
    OwnerFactory.create(
        name="Testi Testinen",
        identifier="123456-789A",
        email=None,
        non_disclosure=True,
    )

    msg = (
        "Due to owner obfuscation, 'non_disclosure' field should always be included "
        "when fetching owners. When using .values_list(..., flat=True), this cannot be done."
        "Please use some other way to fetch this value."
    )

    with pytest.raises(RuntimeError, match=re.escape(msg)):
        Owner.objects.values_list("name", flat=True).first()
