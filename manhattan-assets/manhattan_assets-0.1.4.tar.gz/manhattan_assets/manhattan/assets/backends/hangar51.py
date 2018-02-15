"""
Asset backend for Hangar51.
"""

from datetime import datetime, timedelta
import json

from hangar51client import Hangar51Client, Hangar51ClientException, Variation

from manhattan.assets import Asset
from manhattan.assets.backends.base import BaseAssetMgr
from manhattan.assets.backends.exceptions import RetrieveError, StoreError

__all__ = ['AssetMgr']


class AssetMgr(BaseAssetMgr):
    """
    Asset manager using the Hangar51 service API.
    """

    # A table of functions that convert transforms to a format understood by the
    # backend service.
    _transform_converters = {
        'image.crop': lambda t: [
            'crop',
            [
                t.settings['top'],
                t.settings['right'],
                t.settings['bottom'],
                t.settings['left']
            ]
        ],
        'image.fit': lambda t: [
            'fit',
            [
                t.settings['width'],
                t.settings['height']
            ]
        ],
        'image.output': lambda t: ['output', t.settings],
        'image.rotate': lambda t: ['rotate', t.settings['angle']]
    }

    def __init__(self, api_key, api_endpoint=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set up an client for the Hangar51 API
        if api_endpoint:
            self._client = Hangar51Client(api_key, api_endpoint=api_endpoint)
        else:
            self._client = Hangar51Client(api_key)

    def generate_variations(self, asset, variations):
        """Generate variations for the asset"""

        # Convert the variations
        h51_variations = {}
        for name, transforms in variations.items():
            variation = Variation()
            variation.ops = self.convert_transforms(transforms)
            h51_variations[name] = variation

        # Generate the variations
        try:
            result = self._client.generate_variations(asset.key, h51_variations)
        except Hangar51ClientException as e:
            raise StoreError(str(e))

        # Store the variations against the asset
        for name, variation in result.items():
            asset_variation = Asset(
                base=False,
                key='{0}.{1}'.format(asset.key, variation['version']),
                filename=variation['store_key'],
                type=asset.type,
                core_meta=variation['meta']
                )
            asset.variations[name] = asset_variation

        # If the asset is a temporary asset then update the asset cache
        self.update_cache(asset)

    def remove(self, asset):
        """Remove the specified asset"""
        try:
            self._client.set_expires(asset.key, expires=datetime.now())
        except Hangar51ClientException as e:
            raise StoreError(str(e))

    def retrieve(self, asset):
        """Retrieve the asset (the file)"""
        try:
            data = self._client.download(asset.key)
        except Hangar51ClientException as e:
            raise RetrieveError(str(e))
        return data

    def store_temporary(self, file, name=None):
        """Store an asset temporarily"""

        # Store the file
        expires = datetime.now() + timedelta(0, self._expires)
        try:
            result = self._client.upload(file, name=name, expires=expires)
        except Hangar51ClientException as e:
            raise StoreError(str(e))

        # Create an asset representing the file
        asset = Asset(
            base=True,
            key=result['uid'],
            filename=result['store_key'],
            type=result['type'],
            core_meta=result['meta'],
            temporary=True
            )

        # Store the asset as a temporary asset
        self.update_cache(asset)

        return asset

    def store(self, file_or_asset, name=None):
        """
        Store an asset.

        NOTE: The `name` argument is ignored if an asset is provided, to rename
        an existing asset you must clone the asset with a new name and then
        store the resulting temporary asset.
        """

        asset = None
        if isinstance(file_or_asset, Asset):
            asset = file_or_asset
            asset.temporary = False

            # Remove the assets expiry date
            try:
                self._client.set_expires(asset.key)
            except Hangar51ClientException as e:
                raise StoreError(str(e))

            # Clear any reference to the temporary asset
            self.clear_cache(asset)

        else:
            # Store the file
            try:
                result = self._client.upload(file_or_asset, name=name)
            except Hangar51ClientException as e:
                raise StoreError(str(e))

            # Create an asset representing the file
            asset = Asset(
                base=True,
                key=result['uid'],
                filename=result['store_key'],
                type=result['type'],
                core_meta=result['meta']
                )

        return asset
