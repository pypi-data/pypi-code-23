"""
Asset backend for Hangar51.
"""

import os

from box51 import Box51, Box51Exception

from manhattan.assets import Asset
from manhattan.assets.backends.base import BaseAssetMgr
from manhattan.assets.backends.exceptions import RetrieveError, StoreError

__all__ = ['AssetMgr']


class AssetMgr(BaseAssetMgr):
    """
    Asset manager using the Box51 library.
    """

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

    def __init__(self, asset_root, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._client = Box51(asset_root)

    def generate_variations(self, asset, variations):
        """Generate variations for the asset"""

        # Generate the variations
        box51_variations = {}
        for name, transforms in variations.items():
            box51_variations[name] = self.convert_transforms(transforms)

        try:
            result = self._client.generate_variations(
                asset.key,
                box51_variations
            )
        except Box51Exception as e:
            raise StoreError(str(e))

        # Store the variations against the asset
        prefix_path = ''
        if asset.temporary:
            prefix_path = self._client.TMP_DIR

        for name, variation in result.items():
            asset_variation = Asset(
                base=False,
                key=variation['store_key'],
                filename=os.path.join(prefix_path, variation['store_key']),
                type=asset.type,
                core_meta=variation['meta']
                )
            asset.variations[name] = asset_variation

        # If the asset is a temporary asset then update the asset cache
        self.update_cache(asset)

    def remove(self, asset):
        """Remove the specified asset"""
        try:
            self._client.remove(asset.key)
        except Box51Exception as e:
            raise StoreError(str(e))

    def retrieve(self, asset):
        """Retrieve the asset (the file)"""

        try:
            data = self._client.retrieve(asset.key)
        except Box51Exception as e:
            raise RetrieveError(str(e))
        return data

    def store_temporary(self, file, name=None):
        """Store an asset temporarily"""

        if isinstance(file, tuple):
            file = file[1]

        try:
            result = self._client.store(file, name=name, temporary=True)
        except Box51Exception as e:
            raise StoreError(str(e))

        # Create an asset representing the file
        tmp_path = self._client.TMP_DIR
        asset = Asset(
            base=True,
            key=result['store_key'],
            filename=os.path.join(tmp_path, result['store_key']),
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
                filename_remap = self._client.make_permanent(asset.key)
            except Box51Exception as e:
                raise StoreError(str(e))

            # Clear any reference to the temporary asset
            self.clear_cache(asset)

            # Switch asset and varation to use the new permenant paths
            asset.filename = filename_remap[asset.filename]
            for variation in asset.variations.values():
                variation.filename = filename_remap[variation.filename]

        else:
            if isinstance(file_or_asset, tuple):
                file_or_asset = file_or_asset[1]

            # Store the file
            try:
                result = self._client.store(file_or_asset, name=name)
            except Box51Exception as e:
                raise StoreError(str(e))

            # Create an asset representing the file
            asset = Asset(
                base=True,
                key=result['store_key'],
                filename=result['store_key'],
                type=result['type'],
                core_meta=result['meta']
            )

        return asset
