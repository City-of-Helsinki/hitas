import re
from typing import TypeVar
from uuid import UUID

from django.db import models
from rest_framework.exceptions import ValidationError

from hitas.exceptions import HitasModelNotFound

TModel = TypeVar("TModel", bound=models.Model)


def validate_postal_code(postal_code: str) -> str:
    """Validates value is a valid finnish postal code, e.g. '00101'."""
    match = re.match(r"^\d{5}$", postal_code)
    if match is None:
        raise ValidationError(f"{postal_code!r} is not a valid postal code.")
    return postal_code


def validate_quarter(value: str) -> str:
    """Validates value is a valid quarter, e.g. '2022Q3'."""
    match = re.match(r"^\d{4}Q[1234]$", value)
    if match is None:
        raise ValidationError(f"{value!r} is not a valid quarter.")
    return value


def lookup_id_to_uuid(lookup_id: str, model_class: type[TModel]) -> UUID:
    try:
        return UUID(hex=lookup_id)
    except ValueError as error:
        raise HitasModelNotFound(model=model_class) from error


def lookup_model_by_uuid(lookup_id: str, model_class: type[TModel], **kwargs) -> TModel:
    uuid = lookup_id_to_uuid(lookup_id, model_class)

    try:
        return model_class.objects.get(uuid=uuid, **kwargs)
    except model_class.DoesNotExist as error:
        raise HitasModelNotFound(model=model_class) from error


def lookup_model_id_by_uuid(lookup_id: str, model_class: type[TModel], **kwargs) -> int:
    return lookup_model_by_uuid(lookup_id, model_class, **kwargs).id
