from decimal import Decimal

from rest_framework.renderers import JSONRenderer
from rest_framework.utils.encoders import JSONEncoder

from hitas.calculations.helpers import roundup


class HitasEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(roundup(obj))

        return super().default(obj)


class HitasJSONRenderer(JSONRenderer):
    encoder_class = HitasEncoder
