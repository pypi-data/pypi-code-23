# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Form Schema Types
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

import colander

from tailbone.db import Session


class JQueryTime(colander.Time):
    """
    Custom type for jQuery widget Time data.
    """

    def deserialize(self, node, cstruct):
        if not cstruct:
            return colander.null

        formats = [
            '%I:%M %p',
            '%I:%M%p',
            '%I %p',
            '%I%p',
        ]
        for fmt in formats:
            try:
                return colander.timeparse(cstruct, fmt)
            except ValueError:
                pass

        # re-try first format, for "better" error message
        return colander.timeparse(cstruct, formats[0])


class ObjectType(colander.SchemaType):
    """
    Custom schema type for scalar ORM relationship fields.
    """
    model_class = None

    @property
    def model_title(self):
        self.model_class.get_model_title()

    @property
    def session(self):
        return Session()

    def serialize(self, node, appstruct):
        if appstruct is colander.null:
            return colander.null
        return six.text_type(appstruct)

    def deserialize(self, node, cstruct):
        if not cstruct:
            return None
        obj = self.session.query(self.model_class).get(cstruct)
        if not obj:
            raise colander.Invalid(node, "{} not found".format(self.model_title))
        return obj


class StoreType(ObjectType):
    """
    Custom schema type for store field.
    """
    model_class = model.Store


class CustomerType(ObjectType):
    """
    Custom schema type for customer field.
    """
    model_class = model.Customer


class ProductType(ObjectType):
    """
    Custom schema type for product relationship field.
    """
    model_class = model.Product


class UserType(ObjectType):
    """
    Custom schema type for user field.
    """
    model_class = model.User
