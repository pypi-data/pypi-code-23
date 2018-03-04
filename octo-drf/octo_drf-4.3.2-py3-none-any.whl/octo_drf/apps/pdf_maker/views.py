


try:
    import cStringIO as StringIO
except ImportError:
    # python3 import
    from io import StringIO

from rest_framework import status
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import render_to_string
from octo_drf.apps.base.views import BaseReadOnlyModelViewSet
from rest_framework.response import Response

from .serializers import PDFTemplateSerializer
from .models import PDFTemplate


class PDFViewSet(BaseReadOnlyModelViewSet):

    queryset = PDFTemplate.objects.all()
    lookup_field = 'name'
    serializer_class = PDFTemplateSerializer

    def retrieve(self, request, *args, **kwargs):
        context = {}
        # Формируем контекст
        instances = self.restore_multiply_instances()
        template_obj = self.get_object()
        serializer = self.get_serializer(template_obj)

        # Формируем PDF
        context.update(instances)
        context.update(serializer.data)
        html = render_to_string(template_obj.template, context)
        result = StringIO.StringIO()
        pdf = pisa.pisaDocument(StringIO.StringIO(html.encode('UTF-8')), result, encoding='UTF-8')
        if not pdf.err:
            return HttpResponse(result.getvalue(), content_type='application/pdf')
        return Response(status=status.HTTP_400_BAD_REQUEST)
