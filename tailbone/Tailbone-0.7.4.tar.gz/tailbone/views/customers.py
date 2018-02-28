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
Customer Views
"""

from __future__ import unicode_literals, absolute_import

import re

import six
import sqlalchemy as sa
from sqlalchemy import orm

import colander
from deform import widget as dfwidget
from pyramid.httpexceptions import HTTPNotFound
from webhelpers2.html import HTML, tags

from tailbone import grids
from tailbone.db import Session
from tailbone.views import MasterView, AutocompleteView

from rattail.db import model


class CustomersView(MasterView):
    """
    Master view for the Customer class.
    """
    model_class = model.Customer
    has_versions = True
    supports_mobile = True
    people_detachable = True

    labels = {
        'id': "ID",
        'default_phone': "Phone Number",
        'default_email': "Email Address",
        'default_address': "Physical Address",
        'active_in_pos': "Active in POS",
        'active_in_pos_sticky': "Always Active in POS",
    }

    grid_columns = [
        'id',
        'number',
        'name',
        'phone',
        'email',
    ]

    form_fields = [
        'id',
        'name',
        'default_phone',
        'default_email',
        'default_address',
        'email_preference',
        'active_in_pos',
        'active_in_pos_sticky',
        'people',
        'groups',
    ]

    mobile_form_fields = [
        'id',
        'name',
        'default_phone',
        'default_email',
        'default_address',
        'email_preference',
        'active_in_pos',
        'active_in_pos_sticky',
        'people',
        'groups',
    ]

    def configure_grid(self, g):
        super(CustomersView, self).configure_grid(g)

        g.joiners['email'] = lambda q: q.outerjoin(model.CustomerEmailAddress, sa.and_(
            model.CustomerEmailAddress.parent_uuid == model.Customer.uuid,
            model.CustomerEmailAddress.preference == 1))
        g.joiners['phone'] = lambda q: q.outerjoin(model.CustomerPhoneNumber, sa.and_(
            model.CustomerPhoneNumber.parent_uuid == model.Customer.uuid,
            model.CustomerPhoneNumber.preference == 1))

        g.filters['email'] = g.make_filter('email', model.CustomerEmailAddress.address,
                                           label="Email Address")
        g.filters['phone'] = g.make_filter('phone', model.CustomerPhoneNumber.number,
                                           label="Phone Number")

        # TODO
        # name=self.filter_ilike_and_soundex(model.Customer.name),

        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'

        g.sorters['email'] = lambda q, d: q.order_by(getattr(model.CustomerEmailAddress.address, d)())
        g.sorters['phone'] = lambda q, d: q.order_by(getattr(model.CustomerPhoneNumber.number, d)())

        g.set_sort_defaults('name')

        g.set_label('id', "ID")
        g.set_label('phone', "Phone Number")
        g.set_label('email', "Email Address")

        g.set_link('id')
        g.set_link('number')
        g.set_link('name')

    def get_mobile_data(self, session=None):
        # TODO: hacky!
        return self.get_data(session=session).order_by(model.Customer.name)

    def get_instance(self):
        try:
            instance = super(CustomersView, self).get_instance()
        except HTTPNotFound:
            pass
        else:
            if instance:
                return instance

        key = self.request.matchdict['uuid']

        # search by Customer.id
        instance = self.Session.query(model.Customer)\
                               .filter(model.Customer.id == key)\
                               .first()
        if instance:
            return instance

        # search by CustomerPerson.uuid
        instance = self.Session.query(model.CustomerPerson).get(key)
        if instance:
            return instance.customer

        # search by CustomerGroupAssignment.uuid
        instance = self.Session.query(model.CustomerGroupAssignment).get(key)
        if instance:
            return instance.customer

        raise HTTPNotFound

    def configure_form(self, f):
        super(CustomersView, self).configure_form(f)
        customer = f.model_instance
        permission_prefix = self.get_permission_prefix()

        # id
        if not self.creating:
            f.set_readonly('id')

        f.set_renderer('default_email', self.render_default_email)
        if not self.creating and customer.emails:
            f.set_default('default_email', customer.emails[0].address)

        f.set_renderer('default_phone', self.render_default_phone)
        if not self.creating and customer.phones:
            f.set_default('default_phone', customer.phones[0].number)

        # default_address
        if self.creating:
            f.remove_field('default_address')
        else:
            f.set_renderer('default_address', self.render_default_address)
            f.set_readonly('default_address')

        f.set_enum('email_preference', self.enum.EMAIL_PREFERENCE)
        preferences = list(self.enum.EMAIL_PREFERENCE.items())
        preferences.insert(0, ('', "(no preference)"))
        f.set_widget('email_preference', dfwidget.SelectWidget(values=preferences))

        # people
        if self.creating:
            f.remove_field('people')
        elif self.viewing and self.request.has_perm('{}.detach_person'.format(permission_prefix)):
            f.set_renderer('people', self.render_people_removable)
        else:
            f.set_renderer('people', self.render_people)
            f.set_readonly('people')

        # groups
        if self.creating:
            f.remove_field('groups')
        else:
            f.set_renderer('groups', self.render_groups)
            f.set_readonly('groups')

    def objectify(self, form, data):
        customer = super(CustomersView, self).objectify(form, data)
        customer = self.objectify_contact(customer, data)
        return customer

    def render_default_email(self, customer, field):
        if customer.emails:
            return customer.emails[0].address

    def render_default_phone(self, customer, field):
        if customer.phones:
            return customer.phones[0].number

    def render_default_address(self, customer, field):
        if customer.addresses:
            return six.text_type(customer.addresses[0])

    def render_people(self, customer, field):
        people = customer.people
        if not people:
            return ""

        items = []
        for person in people:
            link = tags.link_to(person, self.request.route_url('people.view', uuid=person.uuid))
            items.append(HTML.tag('li', link))
        return HTML.tag('ul', HTML.literal('').join(items))

    def render_people_removable(self, customer, field):
        people = customer.people
        if not people:
            return ""

        route_prefix = self.get_route_prefix()
        permission_prefix = self.get_permission_prefix()

        view_url = lambda p, i: self.request.route_url('people.view', uuid=p.uuid)
        actions = [
            grids.GridAction('view', icon='zoomin', url=view_url),
        ]
        if self.people_detachable and self.request.has_perm('{}.detach_person'.format(permission_prefix)):
            url = lambda p, i: self.request.route_url('{}.detach_person'.format(route_prefix),
                                                      uuid=customer.uuid, person_uuid=p.uuid)
            actions.append(
                grids.GridAction('detach', icon='trash', url=url))

        columns = ['first_name', 'last_name', 'display_name']
        g = grids.Grid(
            key='{}.people'.format(route_prefix),
            data=customer.people,
            columns=columns,
            labels={'display_name': "Full Name"},
            url=lambda p: self.request.route_url('people.view', uuid=p.uuid),
            linked_columns=columns,
            main_actions=actions)
        return HTML.literal(g.render_grid())

    def render_groups(self, customer, field):
        groups = customer.groups
        if not groups:
            return ""
        items = []
        for group in groups:
            text = "({}) {}".format(group.id, group.name)
            url = self.request.route_url('customergroups.view', uuid=group.uuid)
            items.append(HTML.tag('li', tags.link_to(text, url)))
        return HTML.tag('ul', HTML.literal('').join(items))

    def get_version_child_classes(self):
        return [
            (model.CustomerPhoneNumber, 'parent_uuid'),
            (model.CustomerEmailAddress, 'parent_uuid'),
            (model.CustomerMailingAddress, 'parent_uuid'),
            (model.CustomerPerson, 'customer_uuid'),
        ]

    def detach_person(self):
        customer = self.get_instance()
        person = self.Session.query(model.Person).get(self.request.matchdict['person_uuid'])
        if not person:
            return self.notfound()

        if person in customer.people:
            customer.people.remove(person)
        else:
            self.request.session.flash("No change; person \"{}\" not attached to customer \"{}\"".format(
                person, customer))

        return self.redirect(self.request.get_referrer())

    @classmethod
    def defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()

        cls._defaults(config)

        # detach person
        if cls.people_detachable:
            config.add_tailbone_permission(permission_prefix, '{}.detach_person'.format(permission_prefix),
                                           "Detach a Person from a {}".format(model_title))
            config.add_route('{}.detach_person'.format(route_prefix), '{}/{{{}}}/detach-person/{{person_uuid}}'.format(url_prefix, model_key),
                             # request_method='POST',
            )
            config.add_view(cls, attr='detach_person', route_name='{}.detach_person'.format(route_prefix),
                            permission='{}.detach_person'.format(permission_prefix))


# # TODO: this is referenced by some custom apps, but should be moved??
# def unique_id(value, field):
#     customer = field.parent.model
#     query = Session.query(model.Customer).filter(model.Customer.id == value)
#     if customer.uuid:
#         query = query.filter(model.Customer.uuid != customer.uuid)
#     if query.count():
#         raise fa.ValidationError("Customer ID must be unique")


# TODO: this only works when creating, need to add edit support?
def unique_id(node, value):
    customers = Session.query(model.Customer).filter(model.Customer.id == value)
    if customers.count():
        raise colander.Invalid(node, "Customer ID must be unique")


class CustomerNameAutocomplete(AutocompleteView):
    """
    Autocomplete view which operates on customer name.
    """
    mapped_class = model.Customer
    fieldname = 'name'


class CustomerPhoneAutocomplete(AutocompleteView):
    """
    Autocomplete view which operates on customer phone number.

    .. note::
       As currently implemented, this view will only work with a PostgreSQL
       database.  It normalizes the user's search term and the database values
       to numeric digits only (i.e. removes special characters from each) in
       order to be able to perform smarter matching.  However normalizing the
       database value currently uses the PG SQL ``regexp_replace()`` function.
    """
    invalid_pattern = re.compile(r'\D')

    def prepare_term(self, term):
        return self.invalid_pattern.sub('', term)

    def query(self, term):
        return Session.query(model.CustomerPhoneNumber)\
            .filter(sa.func.regexp_replace(model.CustomerPhoneNumber.number, r'\D', '', 'g').like('%{0}%'.format(term)))\
            .order_by(model.CustomerPhoneNumber.number)\
            .options(orm.joinedload(model.CustomerPhoneNumber.customer))

    def display(self, phone):
        return "{0} {1}".format(phone.number, phone.customer)

    def value(self, phone):
        return phone.customer.uuid


def customer_info(request):
    """
    View which returns simple dictionary of info for a particular customer.
    """
    uuid = request.params.get('uuid')
    customer = Session.query(model.Customer).get(uuid) if uuid else None
    if not customer:
        return {}
    return {
        'uuid':                 customer.uuid,
        'name':                 customer.name,
        'phone_number':         customer.phone.number if customer.phone else '',
        }


def includeme(config):

    # autocomplete
    config.add_route('customers.autocomplete', '/customers/autocomplete')
    config.add_view(CustomerNameAutocomplete, route_name='customers.autocomplete',
                    renderer='json', permission='customers.list')
    config.add_route('customers.autocomplete.phone', '/customers/autocomplete/phone')
    config.add_view(CustomerPhoneAutocomplete, route_name='customers.autocomplete.phone',
                    renderer='json', permission='customers.list')

    # info
    config.add_route('customer.info', '/customers/info')
    config.add_view(customer_info, route_name='customer.info',
                    renderer='json', permission='customers.view')

    CustomersView.defaults(config)
