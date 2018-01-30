from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import SchemaGenerator, get_schema_view

from drf_api_actions.renderers import ApiJsRenderer


class ActionReadMixin(object):
    """
    让coreapi schema生成的时候，识别出来的action为"read"（而不是 "list"）
    """

    @classmethod
    def as_view(cls, **initkwargs) -> object:
        view = super(ActionReadMixin, cls).as_view(**initkwargs)
        view.actions = {'get': 'retrieve'}
        return view


class SchemaGeneratorEx(SchemaGenerator):
    def has_view_permissions(self, path, method, view):  # 需要登录的API也列出来
        return True


class Views:
    @classmethod
    def docs_as_view(cls, title="API", generator_class=SchemaGeneratorEx):
        return include_docs_urls(title=title, generator_class=generator_class)

    @classmethod
    def schema_as_view(cls, title="API", generator_class=SchemaGeneratorEx):
        return get_schema_view(title, generator_class=generator_class)

    @classmethod
    def api_js_as_view(cls, title="API", generator_class=SchemaGeneratorEx):
        return get_schema_view(title, generator_class=generator_class, renderer_classes=[ApiJsRenderer])
