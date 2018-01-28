# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from slugify import slugify
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool
from trytond.pyson import Eval

__all__ = ['Category']

STATES = {
    'readonly': ~Eval('active', True),
    }
DEPENDS = ['active']

class Category(ModelSQL, ModelView):
    "Product Category"
    __name__ = 'product.category'

    slug = fields.Char('URI Slug', select=True,
        states=STATES, depends=DEPENDS)

    @fields.depends('name', 'slug')
    def on_change_with_slug(self):
        if self.name and not self.slug:
            return slugify(self.name, only_ascii=True)
        return self.slug

