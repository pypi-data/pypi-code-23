"""
A set of maker classes for producing fake asset data.
"""

import random

import flask
from mongoframes.factory.makers import Faker, Maker
from shortuuid import ShortUUID

from manhattan.assets import Asset

__all__ = [
    'FileAsset',
    'ImageAsset'
    ]


class FileAsset(Maker):
    """
    Generate a fake file asset.
    """

    def __init__(self, extensions):
        # The file extension to use for the generate file asset
        self._extensions = extensions

    def _assemble(self):
        key = FileAsset.generate_uid(6)
        filename = Faker.get_fake().slug()
        return {
            'base': True,
            'key': key,
            'filename': '{filename}.{key}.{extension}'.format(
                extension=random.choice(self._extensions),
                filename=filename,
                key=key
                ),
            'type': 'file',
            'core_meta': {
                '__manhattan_fake__': True,
                'filename': filename,
                'length': int(abs(random.gauss(5000000, 3000000)))
                },
            'user_meta': {},
            'temporary': False,
            'variations': {}
            }

    def _finish(self, value):
        return Asset(value)

    @staticmethod
    def generate_uid(length):
        """Generate a uid of a given length"""
        su = ShortUUID(alphabet='abcdefghijklmnopqrstuvwxyz0123456789')
        return su.uuid()[:length]


class ImageAsset(Maker):
    """
    Generate a fake image asset.
    """

    def __init__(self, size, variations=None):
        # The size of the original image in the form of a 2 element list, e.g:
        # `[width, height]`.
        self._size = size

        # The variations that should exist for the Asset. Commonly these are
        # passed directly from the manage config class, e.g:
        #
        #     image = ImageAsset(
        #         [1000, 1000],
        #         variations=ProductCfg.image_variations)
        #         )
        #
        # However any valid dictionary of named variations can be provided, e.g:
        #
        #     image = ImageAsset(
        #         [1000, 1000],
        #         variations={'listing': [Fit(200, 200), Output('jpg', 90)]}
        #         )
        #
        self._variations = variations or {}

    def _assemble(self):
        # Generate a base image asset
        key = FileAsset.generate_uid(6)
        extension = 'jpg'
        filename = Faker.get_fake().slug()
        size = [int(self._size[0]), int(self._size[1])]
        asset = {
            'base': True,
            'key': key,
            'filename': '{filename}.{key}.{extension}'.format(
                extension=extension,
                filename=filename,
                key=key
                ),
            'type': 'image',
            'core_meta': {
                '__manhattan_fake__': True,
                'filename': filename,
                'image': {
                    'size': size,
                    'mode': 'RGB'
                    },
                'length': size[0] * size[1] * 3
                },
            'user_meta': {},
            'temporary': False,
            'transforms': [],
            'variations': {}
            }

        # Generate variations of the base asset
        filename_str = '{filename}.{key}.{name}.{version}.{extension}'

        # Build the list of required variations
        for name, transforms in self._variations.items():

            # Determine the size and output format of the variation
            variation_extension = extension
            variation_size = list(size)
            version = FileAsset.generate_uid(3)

            # We're only concerned with changes to the size of the image and the
            # output format.
            for transform in transforms:
                # Crop
                if transform.id == 'image.crop':
                    crop = transform.settings
                    variation_size = [
                        int(variation_size[0] * (crop['right'] - crop['left'])),
                        int(variation_size[1] * (crop['bottom'] - crop['top']))
                        ]

                # Fit
                elif transform.id == 'image.fit':
                    fit = transform.settings
                    scale = min(
                        fit['width'] / variation_size[0],
                        fit['height']/ variation_size[1]
                        )
                    variation_size[0] = int(scale * variation_size[0])
                    variation_size[1] = int(scale * variation_size[1])

                # Output
                elif transform.id == 'image.output':
                    extension = transform.settings['format']

                # Rotate
                elif transform.id == 'image.rotate':
                    if transform.setttings.angle in [90, 270]:
                        variation_size = [variation_size[1], variation_size[0]]

            # Create the variation
            asset['variations'][name] = {
                'base': False,
                'key': '.'.join([key, version]),
                'filename': filename_str.format(
                    extension=extension,
                    filename=filename,
                    key=key,
                    name=name,
                    version=version
                    ),
                'type': 'image',
                'core_meta': {
                    '__manhattan_fake__': True,
                    'filename': filename,
                    'image': {
                        'size': variation_size,
                        'mode': 'RGB'
                        },
                    'length': variation_size[0] * variation_size[1] * 3
                    },
                'user_meta': {},
                'temporary': False,
                'variations': {}
                }

        return asset

    def _finish(self, value):
        asset = Asset(value)
        for name, variation in asset.variations.items():
            asset.variations[name] = Asset(variation)
        return asset
