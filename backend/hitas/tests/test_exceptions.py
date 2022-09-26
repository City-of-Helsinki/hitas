import pytest
from rest_framework.exceptions import ErrorDetail

from hitas.exceptions import _convert_fields


@pytest.mark.parametrize(
    "message,code,expected_message",
    [
        ("This field may not be null.", "null", "This field is mandatory and cannot be null."),
        ("This field is required.", "required", "This field is mandatory and cannot be null."),
        ("Invalid input.", "blank", "This field is mandatory and cannot be blank."),
        ("Enter a valid value.", "invalid", None),
        ("Official name provided is already in use. Conflicting official name: 'test-official-name'.", "unique", None),
        ("Ensure this value is greater than or equal to 1.", "min_value", None),
        ("Ensure this value is less than or equal to 4.", "max_value", None),
    ],
)
def test_codes(message: str, code: str, expected_message: str):
    fields = _convert_fields("example-field", [{"message": ErrorDetail(string=message, code=code), "code": code}])
    assert len(fields) == 1
    assert fields[0] == {"field": "example-field", "message": expected_message or message}


def test_multiple():
    fields = _convert_fields(
        "example-field",
        {
            "start": [{"message": ErrorDetail("A valid integer is required.", "invalid"), "code": "invalid"}],
            "end": [{"message": ErrorDetail("This field is required.", "required"), "code": "required"}],
        },
    )
    assert len(fields) == 2
    assert fields[0] == {"field": "example-field.start", "message": "A valid integer is required."}
    assert fields[1] == {"field": "example-field.end", "message": "This field is mandatory and cannot be null."}


def test_inner_list():
    fields = _convert_fields(
        "example-field",
        {
            "construction": {
                "debt_free_purchase_price": [
                    {
                        "message": ErrorDetail("Ensure this value is greater than or equal to 0.", "min_value"),
                        "code": "min_value",
                    }
                ]
            }
        },
    )
    assert len(fields) == 1
    assert fields[0] == {
        "field": "example-field.construction.debt_free_purchase_price",
        "message": "Ensure this value is greater than or equal to 0.",
    }


def test_empty_dict():
    fields = _convert_fields(
        "example-field",
        [
            {},
            {
                "percentage": [
                    {
                        "message": ErrorDetail("Ensure this value is greater than or equal to 0.", "min_value"),
                        "code": "min_value",
                    }
                ]
            },
        ],
    )
    assert len(fields) == 1
    assert fields[0] == {
        "field": "example-field.percentage",
        "message": "Ensure this value is greater than or equal to 0.",
    }


def test_multi_level_dict():
    fields = _convert_fields(
        "example-field",
        {
            "construction_price_index": [
                {
                    "name": [
                        {"message": ErrorDetail(string="This field is required.", code="required"), "code": "required"}
                    ],
                    "completion_date": [
                        {"message": ErrorDetail(string="This field is required.", code="required"), "code": "required"}
                    ],
                    "value": [
                        {"message": ErrorDetail(string="This field is required.", code="required"), "code": "required"}
                    ],
                    "depreciation_percentage": [
                        {"message": ErrorDetail(string="This field is required.", code="required"), "code": "required"}
                    ],
                }
            ]
        },
    )
    assert len(fields) == 4
    assert fields[0] == {
        "field": "example-field.construction_price_index.name",
        "message": "This field is mandatory and cannot be null.",
    }
    assert fields[1] == {
        "field": "example-field.construction_price_index.completion_date",
        "message": "This field is mandatory and cannot be null.",
    }
    assert fields[2] == {
        "field": "example-field.construction_price_index.value",
        "message": "This field is mandatory and cannot be null.",
    }
    assert fields[3] == {
        "field": "example-field.construction_price_index.depreciation_percentage",
        "message": "This field is mandatory and cannot be null.",
    }
