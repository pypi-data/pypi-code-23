"""
Classes for storing assets.
"""

import mimetypes
import os
from urllib.parse import urljoin, urlparse

import flask
from mongoframes import SubFrame
from mongoframes.factory.makers.images import ImageURL

__all__ = ['Asset']


# Additional common mimetypes not part of the standard mimetypes library
mimetypes.add_type('text/csv', '.csv')
mimetypes.add_type('image/webp', '.webp')


class Asset(SubFrame):
    """
    The `Asset` class provides a representation of assets as embedded documents
    with the database. The asset data is stored separately via an asset backend,
    but information about each asset including their URLs are stored in the
    database and access via the asset class.
    """

    # The root location for assets, this value is used to generate the assets
    # `path` and `url` (URL) properties.
    _asset_root = ''

    _fields = {
        # A flag indicating if this is the base asset or (if False) a variation
        # of a base asset.
        'base',

        # A unique key (at least within the scope of the application) for the
        # asset.
        'key',

        # The assets filename
        'filename',

        # The type of asset, must be either 'file' or 'image'
        'type',

        # A table of meta data describing the asset (provided by the backend
        # service).
        'core_meta',

        # A table of user defined meta information for the asset
        'user_meta',

        # A flag indicating if the asset is temporary. Temporary assets are
        # typically created prior to an asset being saved permenantly. They
        # allow the asset's information to be held against a single unique key
        # which can easily be transferred between client and server.
        #
        # On committing a change temporary assets are converted to 'permenant'
        # assets and any variations for the asset are generated.
        #
        # NOTE: The `temporary` flag is only set for base assets, variations
        # don't require the flag as there existance is based on their parent
        # base asset.
        'temporary',

        # A stack of base transforms applied to all varations (but not the base
        # asset). This allows user manipulations of the base asset to be applied
        # to any variation.
        'base_transforms',

        # A stack of local transforms applied to the asset (only applicable to
        # variations). This allows variations to be regenerated.
        'local_transforms',

        # A table of variations for the asset. A variation is also an asset,
        # based on the base variation but transformed (e.g resized, rotated,
        # etc.) The `variations` property holds a named set of assets each of
        # which is a varation of the (base) asset.
        'variations'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # By default assign an empty dictionary to the `core_meta`, `user_meta`
        # and `variations` fields if not specified.
        if not self.core_meta:
            self.core_meta = {}

        if not self.user_meta:
            self.user_meta = {}

        if not self.base_transforms:
            self.base_transforms = []

        if not self.local_transforms:
            self.local_transforms = []

        if not self.variations:
            self.variations = {}

        # Set up access to the assets meta data
        self._meta = AssetMeta(self)

    def __str__(self):
        return self.url

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.key == other.key
        return False

    @property
    def content_type(self):
        # Return a content type for the asset based on the extension
        return mimetypes.guess_type(self.filename)[0]

    @property
    def ext(self):
        # Return the assets file extension
        return os.path.splitext(self.filename)[1]

    @property
    def fake_url(self, size=None):
        # Return a fake URL for the asset

        try:
            size = None
            # Check if the assets size is given
            if 'image' in self.meta and 'size' in self.meta.image:
                size = self.meta.image['size']
            else:
                # If no size is available default to something small
                size = [500, 500]

            # Check for fake URL configuration settings
            options = flask.current_app.config.get('ASSET_FAKE_MAKER_OPTIONS', {})
        except Exception as e:
            print(e)

        return ImageURL(size[0], size[1], **options)._assemble()

    @property
    def meta(self):
        # Return a special Meta class that will manage core and user meta for
        # the asset.
        return self._meta

    @meta.setter
    def meta(self, value):
        for k, v in value:
            self._meta[k] = v

    @property
    def path(self):
        # Return the relative path for the asset
        return urljoin(urlparse(self._asset_root).path, self.filename)

    @property
    def url(self):
        # Return the absolute URL for the asset

        # If the current flask application is configured to be aware of fake
        # assets then we check for fake assets and return a dummy URL.
        if flask.current_app.config.get('ASSET_ENABLE_FAKES'):
            if self.core_meta.get('__manhattan_fake__'):
                return self.fake_url

        return urljoin(self._asset_root, self.filename)

    @property
    def v(self):
        # Short-cut property for variations. Can be used anywhere but was added
        # primarily to reduce clutter in templates.
        return self.variations

    def to_json_type(self):
        document_dict = super().to_json_type()

        # Add the asset's content type
        document_dict['content_type'] = self.content_type

        # Add the asset's extension
        document_dict['ext'] = self.ext

        # Add the asset's URL
        document_dict['url'] = self.url

        return document_dict

    @classmethod
    def default_projection(cls):
        """
        Short-cut for defining a simple projection, usage:

            projection = {
                'image': Asset.default_projection()
            }

        """
        projection = {'$sub': cls}
        projection.update(cls._default_projection)
        return projection


# Whilst the default projection isn't typically used directly it is useful when
# defining projection for classes with assets fields. For example:
#
#    _default_projection = {
#        'image': {'$sub': assets.Asset, **assets.Asset._default_projection}
#        }
#
# See the `default_projection` shortcut class method.
#
Asset._default_projection = {'variations': {'$sub.': Asset}}


class AssetMeta:
    """
    The `AssetMeta` class provides a mechanism for managing asset meta data
    using both the core and user defined meta data.

    By default values are returned from the user defined meta data but if not
    present then the core meta data value is used.

    Meta values are always set against the user defined meta data.
    """

    def __init__(self, asset):

        # The asset meta is being managed for
        self._asset = asset

    def __getattr__(self, name):
        if '_asset' in self.__dict__:
            asset = self.__dict__['_asset']

            # Check user defined meta data
            if name in asset.user_meta:
                return asset.user_meta[name]

            # Check core meta data
            if name in asset.core_meta:
                return asset.core_meta[name]

        return None

    def __setattr__(self, name, value):
        if '_asset' in self.__dict__:
            asset = self.__dict__['_asset']
            if value is None:
                # Remove value if set to `None`
                if name in asset.user_meta:
                    del asset.user_meta[name]
            else:
                # Set the value
                asset.user_meta[name] = value
        else:
            super(AssetMeta, self).__setattr__(name, value)

    def __getitem__(self, name):
        asset = self.__dict__['_asset']

        # Check user defined meta data
        if name in asset.user_meta:
            return asset.user_meta[name]

        # Check core meta data
        return asset.core_meta.get(name, None)

    def __contains__(self, name):
        asset = self.__dict__['_asset']
        return name in asset.user_meta or name in asset.core_meta

    def get(self, name, default=None):
        asset = self.__dict__['_asset']

        # Check user defined meta data
        if name in asset.user_meta:
            return asset.user_meta[name]

        # Check core meta data
        return asset.core_meta.get(name, None)
