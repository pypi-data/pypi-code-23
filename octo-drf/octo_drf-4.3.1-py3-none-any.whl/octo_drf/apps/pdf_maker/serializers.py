


from octo_drf.apps.base.serializers import BaseModelSerializer

from .models import PDFTemplate


class PDFTemplateSerializer(BaseModelSerializer):

    class Meta:
        model = PDFTemplate
        fields = PDFTemplate.get_serializer_fields()
