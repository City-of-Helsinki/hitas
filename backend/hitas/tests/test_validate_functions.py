import pytest
from django.core.exceptions import ValidationError

from hitas.models.utils import (
    validate_building_id,
    validate_business_id,
    validate_property_id,
    validate_social_security_number,
)


@pytest.mark.parametrize("business_id", ["1234567-1"])
def test__validate__business_id__valid(business_id):
    validate_business_id(business_id)


@pytest.mark.parametrize("business_id", ["", "1", "12345678", "a1234567-8", "1234567-8a"])
def test__validate__business_id__invalid(business_id):
    with pytest.raises(ValidationError):
        validate_business_id(business_id)


@pytest.mark.parametrize(
    "property_id",
    [
        "0000-0000-0000-0000",
        "0001-0001-0001-0001",
        "1234-5678-9012-3456",
        "1-1-1-1",
        "11-11-11-11",
        "111-111-111-111",
        "1-11-111-1",
    ],
)
def test__validate__property_id__valid(property_id):
    validate_property_id(property_id)


@pytest.mark.parametrize(
    "property_id",
    [
        "",
        "1",
        "1111",
        "1111111111111111",
        "a0-0-0-0",
        "0-0-0-0a",
    ],
)
def test__validate__property_id__invalid(property_id):
    with pytest.raises(ValidationError):
        validate_property_id(property_id)


@pytest.mark.parametrize(
    "building_id",
    [
        "0000-0000-0000-0000 S 001",
        "0001-0001-0001-0001 1 001",
        "1234-5678-9012-3456 s 001",
        "1-1-1-1 S 001",
        "11-11-11-11 S 001",
        "111-111-111-111 S 123",
        "1-11-111-1 S 999",
        "91-17-16-1 9 999",
        "100012345A",
    ],
)
def test__validate__building_id__valid(building_id):
    validate_building_id(building_id)


@pytest.mark.parametrize(
    "building_id",
    [
        "",
        "1",
        "1111",
        "1111111111111111",
        "a0-0-0-0 S 001",
        "0-0-0-0 S 001a",
        "a100012345A",
        "100012345Aa",
        "200012345A",
    ],
)
def test__validate__building_id__invalid(building_id):
    with pytest.raises(ValidationError):
        validate_building_id(building_id)


@pytest.mark.parametrize(
    "social_security_number",
    [
        "220462-3911",
        "040583-182W",
        "120368Y546A",
        "260976-0796",
        "010150-8304",
        "020480X583Y",
        "031069Y860J",
        "211033X321F",
        "300575W813Y",
        "040958X7212",
        "290113-2874",
        "190755V3734",
        "010101-003T",
        "010104A7976",
        "120875+2376",
    ],
)
def test__validate__social_security_number(social_security_number):
    assert validate_social_security_number(social_security_number)


@pytest.mark.parametrize(
    "social_security_number",
    [
        None,
        "",
        "A",
        "AAAAAAAAAAA",
        "260976-0796A",  # Too long
        "391399-0796",  # Wrong date
        "010101-0010",  # Too low seqnum
        "010101-9000",  # Too high seqnum
        "010101-000S",  # Invalid check digit
    ],
)
def test__validate__social_security_number__invalid(social_security_number):
    assert not validate_social_security_number(social_security_number)
