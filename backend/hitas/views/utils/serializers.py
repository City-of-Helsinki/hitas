from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from hitas.models._base import ExternalHitasModel
from hitas.views.utils import HitasPostalCodeField


class ReadOnlySerializer(serializers.Serializer):
    def to_internal_value(self, data):
        super().to_internal_value(data)

        try:
            return self.get_model_class().objects.only("id").get(uuid=UUID(hex=data["id"]))
        except (ObjectDoesNotExist, ValueError, TypeError):
            return {}

    def get_model_class(self):
        raise NotImplementedError()

    class Meta:
        abstract = True


class HitasModelSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    def get_id(self, instance: ExternalHitasModel) -> str:
        return instance.uuid.hex

    def to_internal_value(self, data):
        """If referenced in another serializer by id, return an object"""
        if not self.instance and isinstance(data, dict):
            id = data.get("id", None)
            if id is not None:
                try:
                    return self.Meta.model.objects.only("uuid").get(uuid=UUID(hex=str(id)))
                except (self.Meta.model.DoesNotExist, ValueError):
                    raise serializers.ValidationError(f"Object does not exist with given id '{id}'.", code="invalid")
        return super().to_internal_value(data)

    class Meta:
        model = None


class HitasAddressSerializer(serializers.Serializer):
    street_address = serializers.CharField()
    postal_code = HitasPostalCodeField()
    city = serializers.CharField(read_only=True)


class AddressSerializer(serializers.Serializer):
    street_address = serializers.CharField()
    postal_code = serializers.CharField()
    city = serializers.CharField()


class YearMonthSerializer(serializers.DateField):
    format = "%Y-%m"
    input_formats = [format]


class ApartmentHitasAddressSerializer(serializers.Serializer):
    street_address = serializers.CharField()
    postal_code = serializers.CharField(source="building.real_estate.housing_company.postal_code.value", read_only=True)
    city = serializers.CharField(source="building.real_estate.housing_company.postal_code.city", read_only=True)
    apartment_number = serializers.IntegerField(min_value=0)
    floor = serializers.CharField(max_length=50, required=False, allow_null=True, allow_blank=True)
    stair = serializers.CharField(max_length=16)
