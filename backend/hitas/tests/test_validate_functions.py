import pytest
from django.core.exceptions import ValidationError

from hitas.models.codes import validate_code_number
from hitas.models.housing_company import validate_business_id, validate_property_id


@pytest.mark.parametrize("code", ["000", "001", "100", "801", "999"])
def test_validate_valid_code_number(code):
    print(code)
    validate_code_number(code)


@pytest.mark.parametrize("code", ["", "1", "11", "0000", "foo", "a000", "000a"])
def test_validate_invalid_code_number(code):
    with pytest.raises(ValidationError):
        validate_code_number(code)


@pytest.mark.parametrize("business_id", ["1234567-1"])
def test_validate_valid_business_id(business_id):
    validate_business_id(business_id)


@pytest.mark.parametrize("business_id", ["", "1", "12345678", "a1234567-8", "1234567-8a"])
def test_validate_invalid_business_id(business_id):
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
def test_validate_valid_property_id(property_id):
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
def test_validate_invalid_property_id(property_id):
    with pytest.raises(ValidationError):
        validate_property_id(property_id)
