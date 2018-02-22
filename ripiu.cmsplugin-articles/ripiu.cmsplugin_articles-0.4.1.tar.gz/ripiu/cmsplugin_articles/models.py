from cms.models import CMSPlugin
from cms.models.fields import PageField
from djangocms_attributes_field.fields import AttributesField
from modelmixins import ModelMixin

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .conf import settings as conf  # NOQA

LEFT = 'left'
RIGHT = 'right'
CENTER = 'center'
ALIGN_CHOICES = (
    (LEFT, _('left')),
    (RIGHT, _('right')),
    (CENTER, _('center')),
)


def get_templates():
    choices = [
        ('default', _('Default')),
    ]
    choices += settings.RIPIU_ARTICLES_TEMPLATES
    return choices


class TemplateAttributesMixin(ModelMixin):
    template = models.CharField(
        _('Template'),
        choices=get_templates(),
        default=get_templates()[0][0],
        max_length=255,
    )

    attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
    )


class HeadedPluginModel(CMSPlugin):
    H1 = 1
    H2 = 2
    H3 = 3
    H4 = 4
    H5 = 5
    H6 = 6
    HEADING_LEVELS = (
        (H1, 'H1'),
        (H2, 'H2'),
        (H3, 'H3'),
        (H4, 'H4'),
        (H5, 'H5'),
        (H6, 'H6'),
    )

    title = models.CharField(
        _('title'), max_length=400, default='', blank=True
    )

    heading_level = models.PositiveSmallIntegerField(
        _('heading level'),
        choices=HEADING_LEVELS,
        default=H2,
        help_text=_('Choose a heading level'),
    )

    subtitle = models.CharField(
        _('subtitle'), max_length=400, default='', blank=True,
    )

    header_alignment = models.CharField(
        _('header alignment'),
        max_length=10, blank=True,
        choices=ALIGN_CHOICES
    )

    def __str__(self):
        return self.title or ""

    class Meta:
        abstract = True


class ArticlePluginModel(TemplateAttributesMixin, HeadedPluginModel):
    """
    An article
    """

    full_article = PageField(
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name=_("Full article page"),
        help_text=_('You may specify a page with a full article'),
    )

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')


class SectionPluginModel(TemplateAttributesMixin, HeadedPluginModel):
    """
    A section
    """

    class Meta:
        verbose_name = _('Section')
        verbose_name_plural = _('Sections')
