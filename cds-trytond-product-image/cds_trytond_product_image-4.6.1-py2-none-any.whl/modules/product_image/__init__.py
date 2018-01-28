# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from .image import *


def register():
    Pool.register(
        Image,
        Template,
        Product,
        module='product_image', type_='model')
