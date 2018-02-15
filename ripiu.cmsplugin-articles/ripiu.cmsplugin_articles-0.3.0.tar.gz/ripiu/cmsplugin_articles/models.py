from cms.models import CMSPlugin
from cms.models.fields import PageField
from filer.fields.image import FilerImageField

from django.db import models
from django.utils.translation import ugettext_lazy as _

from .conf import settings  # NOQA

LEFT = 'left'
RIGHT = 'right'
CENTER = 'center'
ALIGN_CHOICES = (
    (LEFT, _('left')),
    (RIGHT, _('right')),
    (CENTER, _('center')),
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


class ImageHeadedPluginModel(HeadedPluginModel):
    """Something with a title and a featured image"""

    featured_image = FilerImageField(
        blank=True, null=True,
        verbose_name=_('featured image'),
    )

    thumbnail_option = models.ForeignKey(
        'filer.ThumbnailOption', null=True, blank=True,
        verbose_name=_('thumbnail option'),
    )

    alignment = models.CharField(
        _('image alignment'),
        max_length=10, blank=True, null=True,
        choices=ALIGN_CHOICES
    )

    class Meta:
        abstract = True


class ArticlePluginModel(ImageHeadedPluginModel):
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


class SectionPluginModel(ImageHeadedPluginModel):
    """
    A section
    """

    class Meta:
        verbose_name = _('Section')
        verbose_name_plural = _('Sections')
