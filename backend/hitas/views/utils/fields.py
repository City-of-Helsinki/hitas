import datetime
from typing import TypeVar, Union, overload
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Manager, QuerySet
from enumfields import Enum
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from rest_framework.relations import SlugRelatedField

from hitas.exceptions import HitasModelNotFound
from hitas.models import HitasPostalCode
from hitas.models._base import ExternalHitasModel


class ValueOrNullField(serializers.Field):
    def to_representation(self, value):
        return value if value != "" else None

    def to_internal_value(self, data):
        return data


class HitasDecimalField(serializers.DecimalField):
    def __init__(self, max_digits=15, decimal_places=2, min_value=0, **kwargs):
        super().__init__(max_digits=max_digits, decimal_places=decimal_places, min_value=min_value, **kwargs)


class UUIDField(serializers.Field):
    def to_representation(self, obj: UUID) -> str:
        return obj.hex

    def to_internal_value(self, data: str) -> UUID:
        try:
            return UUID(hex=str(data))
        except ValueError as error:
            raise ValidationError("Not a valid UUID hex.", code="invalid") from error


TModel = TypeVar("TModel", bound=ExternalHitasModel)


class UUIDRelatedField(SlugRelatedField):
    def __init__(self, queryset: Union[QuerySet[TModel], Manager[TModel]], **kwargs):
        kwargs.setdefault("source", "uuid")
        kwargs.setdefault("slug_field", "uuid")
        super().__init__(queryset=queryset, **kwargs)

    def run_validation(self, data=empty):
        if data == "":
            if self.required:
                raise ValidationError(code="blank")
            return None

        return super().run_validation(data)

    def to_internal_value(self, value: str) -> TModel:
        queryset: QuerySet[TModel] = self.get_queryset()
        try:
            return queryset.get(**{self.slug_field: UUID(hex=value)})
        except (ObjectDoesNotExist, TypeError, ValueError) as error:
            raise ValidationError(f"Object does not exist with given id {value!r}.", code="invalid") from error

    @overload
    def to_representation(self, obj: TModel) -> TModel:
        ...

    @overload
    def to_representation(self, obj: UUID) -> str:
        ...

    def to_representation(self, obj):
        if isinstance(obj, UUID):
            return obj.hex
        return obj


class HitasPostalCodeField(SlugRelatedField):
    def __init__(self, **kwargs):
        super().__init__(slug_field="value", queryset=HitasPostalCode.objects.all(), **kwargs)

    def to_representation(self, instance: HitasPostalCode):
        return instance.value

    def to_internal_value(self, data: str):
        try:
            return super().to_internal_value(data=data)
        except ValueError as error:
            raise HitasModelNotFound(model=HitasPostalCode) from error


class HitasEnumField(serializers.ChoiceField):
    def __init__(self, enum=None, **kwargs):
        assert enum is not None, "Enum class not given given."
        self.enum_class = enum
        super().__init__(choices=self.enum_class.choices(), **kwargs)

    def to_representation(self, enum: Enum):
        return enum.value

    def to_internal_value(self, data: str):
        if data == "":
            raise ValidationError(code="blank")

        try:
            return self.enum_class(data)
        except ValueError as error:
            supported_values = [f"'{e.value}'" for e in self.enum_class]

            raise ValidationError(
                f"Unsupported value '{data}'. Supported values are: [{', '.join(supported_values)}]."
            ) from error


class NumberOrRangeField(serializers.IntegerField):
    """Parse number or a range of numbers into an integer (for a range, use the max value)."""

    def to_internal_value(self, data) -> int:
        if isinstance(data, str) and len(data) > self.MAX_STRING_LENGTH:
            self.fail("max_string_length")

        return self.parse_value(str(data))

    def parse_value(self, value: str) -> int:
        # If a range, get the max value
        value = value.split("-")[-1]
        # Check if a float, but allow e.g. '1.0' as an int, but not '1.2'
        value = self.re_decimal.sub("", value)

        try:
            return int(value)
        except (ValueError, TypeError) as error:
            raise ValidationError(f"Value {value!r} is not an integer or an integer range") from error


class DateOnlyField(serializers.DateField):
    def to_internal_value(self, value):
        if isinstance(value, datetime.datetime):
            value = value.date()
        return super().to_internal_value(value)
