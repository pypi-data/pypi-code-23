import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from bureaucracy import DocxTemplate


def upload_path(inst, fn):
    return os.path.join(settings.MEDIA_ROOT, 'doc_templates', inst.type, fn)


class Document(models.Model):
    template_file = models.FileField(upload_to=upload_path)
    type = models.CharField(max_length=50)
    validate_fields = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, editable=False)

    def render(self, context, format='docx'):
        return DocxTemplate(self.template_file).render(context, format=format)

    def render_to_file(self, context, path, format='docx'):
        DocxTemplate(self.template_file).render_and_save(context, path, format)

    def clean(self):
        if self.validate_fields:
            if not hasattr(settings, 'DOCX_TEMPLATE_VARS'):
                raise ValidationError("Can't validate fields if DOCX_TEMPLATE_VARS is not set.")

            if self.type not in settings.DOCX_TEMPLATE_VARS:
                raise ValidationError(
                    "Specified document type not found."
                    " Either uncheck validate fields or add it to the DOCX_TEMPLATE_VARS setting")

            field_names_in_doc = DocxTemplate(self.template_file).get_field_names()

            if set(settings.DOCX_TEMPLATE_VARS[self.type]) != field_names_in_doc:
                missing = set(settings.DOCX_TEMPLATE_VARS[self.type]) - field_names_in_doc
                superfluous = field_names_in_doc - set(settings.DOCX_TEMPLATE_VARS[self.type])
                raise ValidationError(
                    {'template_file': 'Mailmerge fields in template did not match the ones configured for this type.'
                                      'missing: {missing}, superfluous: {superfluous}'.format(missing=missing,
                                                                                              superfluous=superfluous)})
        else:
            pass
