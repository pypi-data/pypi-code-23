# -*- coding: utf-8 -*-
from copy import deepcopy
from contacthub._api_manager._api_customer import _CustomerAPIManager
from contacthub.lib.read_only_list import ReadOnlyList


class Subscription(object):
    """
    Subscription entity definition.
    """
    __attributes__ = (
        'attributes', 'customer', 'customer_api_manager', 'entity_name', 'parent_attr', 'properties_class')

    def __init__(self, customer, parent_attr=None, properties_class=None, **attributes):
        """
        Initialize a new Subscription object for customer in a node with the specified attributes.

        :param customer: the customer associated to this subscription object
        :param parent_attr: the parent attribute for compiling the mutation tracker dictionary
        :param attributes: key-value arguments for generating the structure of the Subscription's attributes
        :param properties_class: reference to the actual Properties class
        """
        self.customer = customer
        self.attributes = attributes
        self.customer_api_manager = _CustomerAPIManager(node=customer.node)
        self.entity_name = 'subscriptions'
        self.parent_attr = parent_attr
        self.properties_class = properties_class

    @classmethod
    def from_dict(cls, customer, attributes=None, parent_attr=None, properties_class=None):
        """
        Create a new Subscription initialized by a specified dictionary of attributes


        :param customer: the customer associated to this subscription object
        :param parent_attr: the parent attribute for compiling the mutation tracker dictionary
        :param attributes: key-value arguments for generating the structure of the Subscription's attributes
        :param properties_class: reference to the actual Properties class
        :return: a new Subscription object
        """
        o = cls(customer=customer, parent_attr=parent_attr, properties_class=properties_class)
        o.attributes = {} if attributes is None else attributes
        return o

    def to_dict(self):
        """
        Convert this Subscription in a dictionary containing his attributes.

        :return: a new dictionary representing the attributes of this Subscription
        """
        return deepcopy(self.attributes)

    def __getattr__(self, item):
        """
        Check if a key is in the dictionary and return it if it's a simple properties

        :param item: the key of the base properties dict
        :return: the item in the attributes dictionary if it's present, raise AttributeError otherwise.
        """
        try:
            parent_attr = self.parent_attr + '.' + item if self.parent_attr else item
            if isinstance(self.attributes[item], list):
                if self.attributes[item] and isinstance(self.attributes[item][0], dict):
                    return ReadOnlyList([self.properties_class.from_dict(parent_attr=parent_attr, parent=self,
                                                                         attributes=elem)
                                         for elem in self.attributes[item]])
                else:
                    ReadOnlyList(self.attributes[item])
            return self.attributes[item]

        except KeyError as e:
            raise AttributeError("%s object has no attribute %s" % (type(self).__name__, e))

    def __setattr__(self, attr, val):
        """
        x.__setattr__('attr', val) <==> x.attr = val
        Update the attributes dictionary with the val specified.
        """
        if attr in self.__attributes__:
            return super(Subscription, self).__setattr__(attr, val)
        else:
            if isinstance(val, list):
                self.attributes[attr] = []
                for elem in val:
                    try:
                        self.attributes[attr] += [elem.attributes]
                    except AttributeError:
                        self.attributes[attr] += [elem]
            else:
                self.attributes[attr] = val
            if self.parent_attr:
                attr = self.parent_attr.split('.')[-1:][0]
                base_attr = self.parent_attr.split('.')[-2:][0]
                self.customer.mute[base_attr + '.' + attr] = self.customer.attributes[base_attr][attr]

    def post(self):
        """
        Post this Subscription in the list of the Subscription for a Customer(specified in the constructor of the Subscription)

        :return: a Subscription object representing the posted Subscription
        """
        entity_attrs = self.customer_api_manager.post(body=self.attributes, urls_extra=self.customer.id + '/'
                                                                                       + self.entity_name)
        if 'base' not in self.customer.attributes:
            self.customer.attributes['base'] = {}
        if self.entity_name not in self.customer.attributes['base']:
            self.customer.attributes['base'][self.entity_name] = []
        self.customer.attributes['base'][self.entity_name] += [entity_attrs]

    def delete(self):
        """
        Remove this Subscription from the list of the Subscription for a Customer(specified in the constructor of
        the Subscription)

        :return: a Subscription object representing the deleted Subscription
        """
        self.customer_api_manager.delete(_id=self.customer.id,
                                         urls_extra=self.entity_name + '/' + self.attributes['id'])

    def put(self):
        """
        Put this Subscription in the list of the Subscription for a Customer(specified in the constructor of the Subscription)

        :return: a Subscription object representing the putted Subscription
        """
        try:
            find = False
            for subscription in self.customer.attributes['base'][self.entity_name]:
                if self.attributes['id'] == subscription['id']:
                    find = True
            if not find:
                raise ValueError("Subscription object doesn't exists in the specified customer")
        except KeyError as e:
            raise ValueError("Subscription object doesn't exists in the specified customer")

        entity_attrs = self.customer_api_manager.put(_id=self.customer.id, body=self.attributes,
                                                     urls_extra=self.entity_name + '/' + self.attributes['id'])

        for subscription in self.customer.attributes['base'][self.entity_name]:
            if subscription['id'] == entity_attrs['id']:
                index = self.customer.attributes['base'][self.entity_name].index(subscription)
                self.customer.attributes['base'][self.entity_name][index] = entity_attrs

    class KINDS:
        DIGITAL_MESSAGE = 'DIGITAL_MESSAGE'
        SERVICE = 'SERVICE'
        OTHER = 'OTHER'
