"""
Classes for implementing a backend for asset management.
"""

import json

from manhattan.assets import Asset

__all__ = ['BaseAssetMgr']


# Classes

class BaseAssetMgr:
    """
    Assets are managed via an asset manager class which must provide the API
    defined by the `BaseAssetMgr` class.
    """

    # A table of functions that convert transforms to a format understood by the
    # backend service.
    _transform_converters = None

    def __init__(self, cache, expires=3600):
        # The cache used to store references to temporary assets, must support
        # `get` and `set` methods, `set` must support an `timeout` argument
        # when the data will expire.
        #
        # `werkzeug.contrib.cache` provides a number of suitable classes for
        # creating caches (e.g `SimpleCache` and `MemcachedCache`).
        self._cache = cache

        # The amount of time before temporary assets expire
        self._expires = expires

    def clear_cache(self, asset):
        """Clear the given asset from the cache"""
        self._cache.delete(asset.key)

    def clone(self, asset, name=None):
        """Returning a temporary asset cloned from the specified asset"""

        # Retrieve the asset we're cloning
        file = self.retrieve(asset)

        # Store the file as a new temporary asset (cloning it)
        cloned = self.store_temporary((file, asset.filename), name=name)

        return cloned

    def generate_variations(self, asset, variations):
        """Generate variations for the asset"""
        raise NotImplementedError()

    def get_temporary_by_key(self, key):
        """Get a temporary asset by it's key"""
        asset_json = self._cache.get(key)
        if asset_json:
            asset = Asset(json.loads(asset_json))
            for name, variation in asset.variations.items():
                asset.variations[name] = Asset(variation)
            return asset

    def remove(self, asset):
        """Remove the specified asset"""
        raise NotImplementedError()

    def retrieve(self, asset):
        """Retrieve the asset"""
        raise NotImplementedError()

    def store_temporary(self, file, name=None):
        """Store an asset temporarily"""
        raise NotImplementedError()

    def store(self, file_or_asset, name=None):
        """
        Store an asset.

        NOTE: The `name` argument is ignored if an asset is provided, to rename
        an existing asset you must clone the asset with a new name and then
        store the resulting temporary asset.
        """
        raise NotImplementedError()

    def update_cache(self, asset):
        """Update the given asset in the cache"""
        if asset.temporary:
            asset_json = json.dumps(asset.to_json_type())
            self._cache.delete(asset.key)
            self._cache.set(asset.key, asset_json, self._expires)

    # Class methods

    @classmethod
    def convert_transforms(cls, transforms):
        """
        Convert a stack of transforms to a format understood by the backend
        service.
        """
        return [cls._transform_converters[t.id](t) for t in transforms]

    @classmethod
    def define_transform_converter(cls, transform_id, func):
        """Define a converter for the given transform (id)"""
        if cls._transform_converters is None:
            cls._transform_converters = {}
        cls._transform_converters[transform_id] = func
