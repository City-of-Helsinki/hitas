import pytest
from django.core.exceptions import ValidationError

from hitas.models.utils import validate_building_id, validate_business_id, validate_property_id


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
