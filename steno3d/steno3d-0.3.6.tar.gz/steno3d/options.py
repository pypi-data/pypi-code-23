"""options.py defines the base option classes for steno3d"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from json import dumps
import properties

from .props import HasSteno3DProps


class Options(HasSteno3DProps):
    """Generic options for all steno3d resources"""

    @property
    def _json(self):
        """returns json representation of options"""
        opts_json = {}
        for key in self._props:
            opts_json[key] = getattr(self, key)
        return dumps(opts_json)

    @properties.validator(properties.everything)
    def _opt_defaulter(self, change):
        if change['value'] is None:
            change['value'] = self._props[change['name']].default


class ColorOptions(Options):
    """Options related to resource display color"""
    color = properties.Color(
        doc='Solid color',
        default='random',
        required=False
    )
    opacity = properties.Float(
        doc='Opacity',
        default=1.,
        min=0.,
        max=1.,
        required=False
    )


class MeshOptions(Options):
    """Options related to mesh display"""
    wireframe = properties.Boolean(
        doc='Wireframe',
        default=False,
        required=False
    )
