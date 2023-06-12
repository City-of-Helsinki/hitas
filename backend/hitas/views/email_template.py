from enumfields.drf import EnumSupportSerializerMixin
from rest_framework.serializers import ModelSerializer

from hitas.models import EmailTemplate
from hitas.views.utils import HitasModelViewSet


class EmailTemplateSerializer(EnumSupportSerializerMixin, ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = [
            "name",
            "text",
        ]


class EmailTemplateViewSet(HitasModelViewSet):
    model_class = EmailTemplate
    serializer_class = EmailTemplateSerializer
    lookup_field = "name"

    @staticmethod
    def get_base_queryset():
        return EmailTemplate.objects.all()
