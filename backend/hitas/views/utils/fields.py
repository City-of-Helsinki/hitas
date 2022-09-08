from uuid import UUID

from enumfields import Enum
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.relations import SlugRelatedField

from hitas.exceptions import HitasModelNotFound
from hitas.models import HitasPostalCode


class ValueOrNullField(serializers.Field):
    def to_representation(self, value):
        return value if value != "" else None

    def to_internal_value(self, data):
        return data


class HitasDecimalField(serializers.DecimalField):
    def __init__(self, max_digits=15, decimal_places=2, min_value=0, **kwargs):
        super().__init__(max_digits=max_digits, decimal_places=decimal_places, min_value=min_value, **kwargs)


class UUIDField(serializers.Field):
    def to_representation(self, obj):
        return obj.hex

    def to_internal_value(self, data: str):
        return super().to_internal_value(data=UUID(hex=str(data)))


class UUIDRelatedField(SlugRelatedField):
    def __init__(self, **kwargs):
        super().__init__(slug_field="uuid", **kwargs)

    def run_validation(self, data=empty):
        if data == "":
            raise serializers.ValidationError(code="blank")

        return super().run_validation(data)

    def to_representation(self, obj):
        return getattr(obj, self.slug_field).hex

    def to_internal_value(self, data: str):
        try:
            return super().to_internal_value(data=UUID(hex=str(data)))
        except ValueError:
            raise HitasModelNotFound(model=self.get_queryset().model)


class HitasPostalCodeField(SlugRelatedField):
    def __init__(self, **kwargs):
        super().__init__(slug_field="value", queryset=HitasPostalCode.objects.all(), **kwargs)

    def to_representation(self, instance: HitasPostalCode):
        return instance.value

    def to_internal_value(self, data: str):
        try:
            return super().to_internal_value(data=data)
        except ValueError:
            raise HitasModelNotFound(model=HitasPostalCode)


class HitasEnumField(serializers.ChoiceField):
    def __init__(self, enum=None, **kwargs):
        assert enum is not None, "Enum class not given given."
        self.enum_class = enum
        super().__init__(choices=self.enum_class.choices(), **kwargs)

    def to_representation(self, enum: Enum):
        return enum.value

    def to_internal_value(self, data: str):
        try:
            return self.enum_class(data)
        except ValueError:
            raise serializers.ValidationError(f"Unsupported {self.enum_class.__name__} '{data}'.")
