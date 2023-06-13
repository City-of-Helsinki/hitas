from enumfields.drf import EnumSupportSerializerMixin
from rest_framework.serializers import ModelSerializer

from hitas.models import PDFBody
from hitas.views.utils import HitasModelViewSet


class PDFBodySerializer(EnumSupportSerializerMixin, ModelSerializer):
    class Meta:
        model = PDFBody
        fields = [
            "name",
            "texts",
        ]


class PDFBodyViewSet(HitasModelViewSet):
    model_class = PDFBody
    serializer_class = PDFBodySerializer
    lookup_field = "name"
