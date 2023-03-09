from datetime import datetime
from decimal import Decimal

from rest_framework.renderers import JSONRenderer
from rest_framework.utils.encoders import JSONEncoder

from hitas.utils import roundup


class Month:
    def __init__(self, date: datetime.date):
        self.date = date


class HitasEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Month):
            return obj.date.strftime("%Y-%m")

        if isinstance(obj, Decimal):
            return float(roundup(obj))

        return super().default(obj)


class HitasJSONRenderer(JSONRenderer):
    encoder_class = HitasEncoder
