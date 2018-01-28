# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import logging

from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool
from trytond.pyson import Eval

__all__ = ['Image', 'Template', 'Product']

logger = logging.getLogger(__name__)

STATES = {
    'readonly': ~Eval('active', True),
    }
DEPENDS = ['active']


class Image(ModelSQL, ModelView):
    "Product Image"
    __name__ = "product.image"
    _order = [
        ('product', 'ASC'),
        ('sort_rank', 'ASC'),
        ('file_name', 'ASC'),
        ]
    active = fields.Boolean('Active', select=True)
    product = fields.Many2One('product.template', 'Product Template',
        required=True, ondelete='CASCADE', select=True, states=STATES,
        depends=DEPENDS)
    sort_rank = fields.Integer('Sort Rank', select=True,
        states=STATES, depends=DEPENDS)
    file_name = fields.Char('Image Filename', size=None, required=True,
        states=STATES, depends=DEPENDS)
    file_data = fields.Binary('Image File', filename='file_name',
        states=STATES, depends=DEPENDS)

    @staticmethod
    def default_active():
        return True


class Template(ModelSQL, ModelView):
    "Product Template"
    __name__ = 'product.template'
    images = fields.One2Many('product.image', 'product', 'Images',
        states=STATES, depends=DEPENDS)


class Product(ModelSQL, ModelView):
    "Product Variant"
    __name__ = 'product.product'
    main_image = fields.Many2One('product.image', 'Main Image',
        domain=[('product', '=', Eval('template'))],
        states=STATES, depends=DEPENDS)
    display_image = fields.Function(fields.Many2One('product.image',
        'Display Image'), 'get_display_image')

    def get_display_image(self, name):
        if self.main_image:
            return self.main_image
        if self.template.images:
            return self.template.images[0]
        return None

