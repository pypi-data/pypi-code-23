from cms.models import CMSPlugin
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
        }),
        (_('Advanced settings'), {
            'classes': ('collapse',),
            'fields': (
                'template',
                'attributes',
            )
        })
    )

    def save_model(self, request, obj, form, change):
        """Check for parts"""
        response = super(HeadedPlugin, self).save_model(
            request, obj, form, change
        )
        if not change:
            # new plugin: add its parts
            for i, c in enumerate((HeaderPlugin, MainPlugin), start=1):
                part = CMSPlugin(
                    parent=obj,
                    placeholder=obj.placeholder,
                    language=obj.language,
                    position=i,
                    plugin_type=c.__name__,
                )
                part.save()
        return response

    def render(self, context, instance, placeholder):
        classes = '%(class_name)s ' % {
            'class_name': settings.RIPIU_ARTICLES_CLASSNAME,
        }
        classes += instance.attributes.get('class', '')
        instance.attributes['class'] = classes
        return super(HeadedPlugin, self).render(context, instance, placeholder)


class PartPlugin(CMSPluginBase):
    module = module = settings.RIPIU_ARTICLES_MODULE_NAME
    allow_children = True
    require_parent = True
    parent_classes = ['ArticlePlugin', 'SectionPlugin']
    render_template = 'ripiu/cmsplugin_articles/part.html'


@plugin_pool.register_plugin
class HeaderPlugin(PartPlugin):
    name = _('Header content')
    child_classes = settings.RIPIU_ARTICLES_HEAD_CHILD_CLASSES


@plugin_pool.register_plugin
class MainPlugin(PartPlugin):
    name = _('Main content')
    child_classes = settings.RIPIU_ARTICLES_MAIN_CHILD_CLASSES


@plugin_pool.register_plugin
class ArticlePlugin(HeadedPlugin):
    model = ArticlePluginModel
    name = _('Article')
    fieldsets = HeadedPlugin.fieldsets + (
        (_('Footer'), {
            'classes': ['collapse'],
            'fields': ('full_article', )
        }),)

    def get_render_template(self, context, instance, placeholder):
        return 'ripiu/cmsplugin_articles/%(template)s/article.html' % {
            'template': instance.template,
        }


@plugin_pool.register_plugin
class SectionPlugin(HeadedPlugin):
    model = SectionPluginModel
    name = _('Section')

    def get_render_template(self, context, instance, placeholder):
        return 'ripiu/cmsplugin_articles/%(template)s/section.html' % {
            'template': instance.template,
        }
