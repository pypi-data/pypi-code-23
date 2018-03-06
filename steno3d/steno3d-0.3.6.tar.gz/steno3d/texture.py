"""texture.py contains the texture resource structures"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple
from io import BytesIO
from json import dumps
from six import string_types
import properties

from .base import BaseTexture2D
from .props import image_download


FileProp = namedtuple('FileProp', ['file', 'dtype'])


class Texture2DImage(BaseTexture2D):
    """Contains an image that can be mapped to a 2D surface"""

    _resource_class = 'image'

    O = properties.Vector3(
        doc='Origin of the texture'
    )
    U = properties.Vector3(
        doc='U axis of the texture'
    )
    V = properties.Vector3(
        doc='V axis of the texture'
    )
    image = properties.ImagePNG(
        doc='Image file',
        deserializer=image_download,
    )

    def _nbytes(self, img=None):
        if img is None or (isinstance(img, string_types) and img == 'image'):
            img = self.image
        try:
            img.seek(0)
            return len(img.read())
        except:
            raise ValueError('Texture2DImage cannot calculate the number of '
                             'bytes of {}'.format(img))

    @properties.validator('image')
    def _reject_large_files(self, change):
        self._validate_file_size(change['name'], change['value'])

    @properties.validator
    def _validate_image(self):
        self._validate_file_size('image', self.image)
        return True

    def _get_dirty_files(self, force=False):
        files = super(Texture2DImage, self)._get_dirty_files(force)
        dirty = self._dirty_props
        if 'image' in dirty or force:
            self.image.seek(0)
            copy = BytesIO()
            copy.name = 'texture_copy.png'
            copy.write(self.image.read())
            copy.seek(0)
            files['image'] = FileProp(copy, 'png')
        return files

    def _get_dirty_data(self, force=False):
        datadict = super(Texture2DImage, self)._get_dirty_data(force)
        dirty = self._dirty_props
        if ('O' in dirty or 'U' in dirty or 'V' in dirty) or force:
            datadict['OUV'] = dumps(dict(
                O=self.O.tolist(),
                U=self.U.tolist(),
                V=self.V.tolist(),
            ))
        return datadict

    def _repr_png_(self):
        """For IPython display"""
        if self.image is None:
            return None
        self.image.seek(0)
        return self.image.read()

    @classmethod
    def _build_from_json(cls, json, **kwargs):
        tex = Texture2DImage(
            title=kwargs['title'],
            description=kwargs['description'],
            O=json['OUV']['O'],
            U=json['OUV']['U'],
            V=json['OUV']['V'],
            image=cls._props['image'].deserialize(json['image'])
        )
        return tex

    @classmethod
    def _build_from_omf(cls, omf_tex, omf_project):
        tex = Texture2DImage(
            title=omf_tex.name,
            description=omf_tex.description,
            O=omf_tex.origin + omf_project.origin,
            U=omf_tex.axis_u,
            V=omf_tex.axis_v,
            image=omf_tex.image
        )
        return tex


__all__ = ['Texture2DImage']
