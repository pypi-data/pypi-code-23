from bureaucracy import DocxTemplate
from bureaucracy.utils import DOCUMENT_MIME_TYPES
from django.http import HttpResponse

from django_bureaucracy.models import Document


def render_to_download(template, context, format='docx'):
    """
    :param template: a Document, DocxTemplate, path or file-like object representing the template.
    :param context: a dict with the context to render with
    :return:
    """
    if isinstance(template, DocxTemplate):
        doc = template
    elif isinstance(template, Document):
        doc = DocxTemplate(template.template_file.path)
    else:
        doc = DocxTemplate(template)

    data = doc.render(context, format=format)

    return HttpResponse(data, content_type=DOCUMENT_MIME_TYPES[format])
