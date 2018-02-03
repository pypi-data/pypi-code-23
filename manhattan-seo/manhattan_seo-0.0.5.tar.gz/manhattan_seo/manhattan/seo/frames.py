from flask import current_app, url_for

from manhattan.assets import Asset
from manhattan.comparable.frames import ComparableFrame, _ComparableFrameMeta
from manhattan.formatters.flask import path_to_url
from manhattan.publishing import PublishableFrame
from mongoframes import *
from mongoframes.frames import _FrameMeta

__all__ = [
    'BaseSEOMeta',
    'SEOMetaProps'
    ]


class _BaseSEOMetaMeta(_ComparableFrameMeta):
    """
    Meta class for `BaseSEOMeta`s to ensure that we copy the configured and
    mapped properties dictionaries.
    """

    def __new__(meta, name, bases, dct):

        # Ensure we copy configured and mapped properties
        if '_config_props' in dct:
            dct['_config_props'] = dct['_config_props'].copy()

        if '_mapped_props' in dct:
            dct['_mapped_props'] = dct['_mapped_props'].copy()

        cls = super(_BaseSEOMetaMeta, meta).__new__(meta, name, bases, dct)

        # Add a decorated dictionary against the class to store instances used
        # as decorators.
        cls._decorated = {}

        if dct.get('_parent_frame_cls'):

            # Add handlers for the insert and delete signals against the
            # parent frame.
            parent_cls = dct['_parent_frame_cls']
            parent_cls.listen('inserted', cls._on_parent_inserted)
            parent_cls.listen('deleted', cls._on_parent_deleted)

            # Add a property to the parent frame class as a shortcut to get the
            # associated SEO meta class.
            def get_seo_meta(self):
                seo_meta = cls.one(
                    Q.document == self,
                    projection=cls._property_projection
                )
                seo_meta.document = self
                return seo_meta

            parent_cls.seo_meta = property(get_seo_meta)

        return cls


class BaseSEOMeta(ComparableFrame, metaclass=_BaseSEOMetaMeta):
    """
    A subframe (embedded document) that holds SEO and social information for its
    parent frame (document).
    """

    # By default we store all SEOMeta information in a single collection
    _collection = 'SEOMeta'

    # The frame the SEO meta data represents (optional)
    _parent_frame_cls = None

    _fields = {
        'cls',
        'title',

        # Often titles include pre/post decorators, for example
        #
        # 'About us | mywebsite.com'
        #
        # However, if the `full_title` flag is set to true this indicates that
        # the title represents the full page title and should not be decorated.
        'full_title',

        # `BaseSEOMeta` documents 'typically' represent a parent document,
        # however they may also represent an endpoint/view (when applied as
        # a view decorator).
        'document',

        # Meta
        'meta_description',
        'meta_robots',

        # Sitemap
        'sitemap_visible',
        'sitemap_frequency',
        'sitemap_priority',

        # Open graph
        'og_title',
        'og_description',
        'og_audio',
        'og_image',
        'og_video'
    }

    _indexes = [
        IndexModel([('cls', ASC), ('document', ASC)], unique=True)
    ]

    _uncompared_fields = ComparableFrame._uncompared_fields | {
        'cls',
        'document'
    }

    # The projection used when returning an SEO meta instance via the
    # `seo_meta` property against the related parent document.
    _property_projection = {
        'og_image': Asset.default_projection()
    }

    # The projection used when generating a sitemap using the `seo_meta`. This
    # should include a projection for the `document` field which allows a URL
    # for the document to be generated, and if `visible`, `priority` and/or
    # `frequency` are mapped then it should included the required fields to map
    # these.
    _sitemap_projection = None

    # SEO properties
    #
    # SEO properties maybe stored in fields against a `BaseSEOMeta`, or they
    # maybe mapped to a property against the related parent document or finally
    # they be directly configured against the class itself.
    #
    # The order above is important, when requesting an SEO property first we
    # check to see if one is set against the SEO meta document, then we check to
    # see if one is defined against a mapped field in the related parent
    # document and then finally we check to see if one is configured against the
    # SEO meta class itself.
    #
    # For this reason it's common to define a base class for your website that
    # has a number of default configured properties and then to define separate
    # SEO meta classes for each document type (collection/frame).

    # A dictionary of configured SEO properties.
    _config_props = {
        # 'title_postfix'
        # 'og_locale'
        # 'og_site_name'
        # 'og_type'
        # 'twitter_site'
    }

    # A dictionary of mapped SEO properties.
    _mapped_props = {
        # 'sitemap_lastmod',
        # 'url'
    }

    def __init__(self, *args, **kw):
        # If the instance is called as a decorator a path can be passed to
        # override the default behaviour of attempting to generate the path
        # from decorated views endpoint.
        self.path = None
        if 'path' in kw:
            self.path = kw.pop('path')

        super().__init__(*args, **kw)

        # Store a reference to the class name against the document
        self.cls = self.__class__.__name__

        # Reference to a view function decorated by the SEO meta class
        self._view_func = None

    def __call__(self, func):

        # Wrap the function so that it receives the SEO meta as an argument
        def wrapper(**kwargs):
            kwargs['seo_meta'] = self
            return func(**kwargs)

        # Ensure the name of the wrapping function has the same name as the
        # wrapped function.
        wrapper.__name__ = func.__name__

        # Store an internal reference to the view function
        self._view_func = wrapper

        # Store this SEO meta instance against a map of views decorated by this
        # class.
        self.__class__._decorated[wrapper] = self

        return wrapper

    @property
    def exclude_from_sitemap(self):
        return self.sitemap_visible == False

    @exclude_from_sitemap.setter
    def exclude_from_sitemap(self, value):
        if value:
            self.sitemap_visible = False
        else:
            self.sitemap_visible = None

    @property
    def props(self):
        """Return an `SEOMetaProps` instance for this SEO meta instance"""
        return SEOMetaProps(self)

    @property
    def url(self):
        """
        Return the URL for the SEO meta instance.
        """

        if self.path:
            return path_to_url(self.path)

        if not self._view_func:
            return

        match = None
        for endpoint, view_func in current_app.view_functions.items():
            if view_func is self._view_func:
                match = endpoint
                break

        if match:
            self.path = url_for(endpoint)
            return path_to_url(self.path)

    @classmethod
    def count(cls, filter=None, **kwargs):
        return super().count(filter=cls.restrict(filter), **kwargs)

    @classmethod
    def decorated(cls):
        """
        Return a list of SEO meta instances for the class that decorate views.
        """
        metas = []
        for meta in list(cls._decorated.values()):

            # If the path is callable then call it and generate separate SEO
            # meta instances for each path returned.
            if callable(meta.path):
                for path in meta.path():
                    sub_meta = cls(**meta._document, path=path)
                    metas.append(sub_meta)
            else:
                metas.append(meta)

        return metas

    @classmethod
    def ids(cls, filter=None, **kwargs):
        return super().ids(filter=cls.restrict(filter), **kwargs)

    @classmethod
    def many(cls, filter=None, **kwargs):
        return super().many(filter=cls.restrict(filter), **kwargs)

    @classmethod
    def one(cls, filter=None, **kwargs):
        return super().one(filter=cls.restrict(filter), **kwargs)

    @classmethod
    def restrict(cls, filter=None):
        """Update the given filter so it restricts it to select only articles"""
        if filter:
            return And(filter, Q.cls == cls.__name__)
        return Q.cls == cls.__name__

    @classmethod
    def _on_parent_inserted(cls, sender, frames):
        """Handle the insert of one or more parent documents"""

        # Check for publishable frames, in which case we ignore inserts in the
        # published context.
        if issubclass(sender, PublishableFrame):
            if not sender._context_manager.is_draft:
                return

        # Insert an associated SEO meta document for each of the newly inserted
        # parent documents.
        for frame in frames:
            inst = cls(document=frame)
            inst.insert()

    @classmethod
    def _on_parent_deleted(cls, sender, frames):
        """Handle the deletion of one or more parent documents"""

        # Check for publishable frames, in which case we ignore deletes in the
        # published context.
        if issubclass(sender, PublishableFrame):
            if not sender._context_manager.is_draft:
                return

        # Deleted any associated SEO meta document for each of the deleted
        # parent documents.
        for frame in frames:
            inst = cls.one(Q.document == frame)
            if inst:
                inst.delete()


class SEOMetaProps:
    """
    SEO meta properties must be looked up in a set order (instance, mapped,
    class - see the `BaseSEOMeta` class > SEO Properties). The `SEOMetaProps`
    class implements this look up order through a convienent read-only
    dictionary(-like) class that supports dot notation.
    """

    def __init__(self, seo_meta):
        self._seo_meta = seo_meta

    def __getattr__(self, name):

        if '_seo_meta' in self.__dict__:
            seo_meta = self.__dict__['_seo_meta']
            value = None

            # First check the SEO meta document
            if hasattr(seo_meta, name):
                value = getattr(seo_meta, name)

            # Second check the parent document (if there is one)
            if value is None and seo_meta.document:
                if name in seo_meta._mapped_props:
                    mapped_name = seo_meta._mapped_props[name]
                    value = getattr(seo_meta.document, mapped_name)

            # Finally check the config
            if value is None:
                if seo_meta._config_props.get(name) is not None:
                    value = seo_meta._config_props[name]

            if callable(value):
                return value(seo_meta)

            return value

        raise AttributeError(
            "'{0}' has no attribute '{1}'".format(self.__class__.__name__, name)
        )

    def __getitem__(self, name):
        return self.__dict__['_document'][name]

    def __contains__(self, name):

        if '_seo_meta' in self.__dict__:
            seo_meta = self.__dict__['_seo_meta']

            # First check the SEO meta document
            if name in seo_meta:
                return True

            # Second check the parent document (if there is one)
            if seo_meta.document:
                if name in seo_meta._mapped_props:
                    return True

            # Finally check the config
            if name in seo_meta._config_props:
                return True

            return False

    def get(self, name, default=None):
        value = self.__getattr__(name)
        if value is not None:
            return value
        return default
