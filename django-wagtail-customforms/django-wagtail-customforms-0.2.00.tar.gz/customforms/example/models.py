from __future__ import absolute_import, unicode_literals

from django.db import models

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from modelcluster.fields import ParentalKey

from customforms.models import FormPageMixin

"""
Inherit from FormPageMixin and add foreignkey to Form model
Then include the form in the template see example template.
"""
class HomePage(FormPageMixin, Page):
    body = RichTextField(blank=True)

    form = ParentalKey(
        'customforms.Form',
        related_name='pages',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
        FieldPanel('form', classname="full"),
    ]
