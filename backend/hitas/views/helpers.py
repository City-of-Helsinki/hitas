from typing import Any, Optional, TypedDict


def value_or_null(s: str) -> Optional[str]:
    return s if s != "" else None


class Address(TypedDict):
    street: str
    postal_code: str
    city: str


def address_obj(obj: Any) -> Address:
    return {
        "street": obj.street_address,
        "postal_code": obj.postal_code.value,
        "city": obj.city,
    }


def to_float(s: Optional[str]) -> Optional[float]:
    if s is None:
        return None

    return float(s)
