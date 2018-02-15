from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from .models import ArticlePluginModel, SectionPluginModel


class HeadedPlugin(CMSPluginBase):
    module = module = settings.RIPIU_ARTICLES_MODULE_NAME
    allow_children = True
    fieldsets = (
        (_('Header'), {
            'fields': (
                'title',
                'subtitle',
                ('heading_level', 'header_alignment'),
            )
        }), (_('Featured image'), {
            'fields': (
                'featured_image',
                'thumbnail_option',
                'alignment',
            )
        }),
    )

    def render(self, context, instance, placeholder):
        context = super(HeadedPlugin, self).render(
            context, instance, placeholder
        )
        thumb_opts = {
            'width': settings.RIPIU_ARTICLES_IMAGE_WIDTH,
            'height': settings.RIPIU_ARTICLES_IMAGE_HEIGHT,
            'crop': settings.RIPIU_ARTICLES_IMAGE_CROP,
            'upscale': settings.RIPIU_ARTICLES_IMAGE_UPSCALE,
        }
        if instance.alignment:
            thumb_opts['alignment'] = instance.alignment
        if instance.thumbnail_option:
            if instance.thumbnail_option.width:
                thumb_opts['width'] = instance.thumbnail_option.width
            if instance.thumbnail_option.height:
                thumb_opts['height'] = instance.thumbnail_option.height
            thumb_opts['crop'] = instance.thumbnail_option.crop
            thumb_opts['upscale'] = instance.thumbnail_option.upscale
        thumb_opts['size'] = (
            thumb_opts['width'],
            thumb_opts['height'],
        )
        context.update({
            'instance': instance,
            'placeholder': placeholder,
            'featured_image': {
                'image': instance.featured_image,
                'thumbnail_option': thumb_opts,
                'alignment': instance.alignment,
                # 'alt': instance.featured_image.default_alt_text,
            }
        })
        return context


@plugin_pool.register_plugin
class ArticlePlugin(HeadedPlugin):
    model = ArticlePluginModel
    name = _('Article')
    render_template = 'ripiu/cmsplugin_articles/article.html'


@plugin_pool.register_plugin
class SectionPlugin(HeadedPlugin):
    model = SectionPluginModel
    name = _('Section')
    render_template = 'ripiu/cmsplugin_articles/section.html'
