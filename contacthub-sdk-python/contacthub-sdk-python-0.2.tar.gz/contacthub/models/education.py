# -*- coding: utf-8 -*-
from copy import deepcopy
from contacthub._api_manager._api_customer import _CustomerAPIManager


class Education(object):
    """
    Education entity definition.
    """
    __attributes__= ('attributes', 'customer', 'customer_api_manager', 'entity_name', 'parent_attr', 'properties_class')

    def __init__(self, customer, parent_attr=None, properties_class=None, **attributes):
        """
        Initialize a new Education object for customer in a node with the specified attributes.
        :param customer: the customer associated to this education object
        :param parent_attr: the parent attribute for compiling the mutation tracker dictionary
        :param properties_class: reference to the actual Properties class
        :param attributes: key-value arguments for generating the structure of the Education's attributes
        """
        self.customer = customer
        self.attributes = attributes
        self.customer_api_manager = _CustomerAPIManager(node=customer.node)
        self.entity_name = 'educations'
        self.parent_attr = parent_attr
        self.properties_class = properties_class


    @classmethod
    def from_dict(cls, customer, attributes=None, parent_attr=None, properties_class=None):
        """
        Create a new Education initialized by a specified dictionary of attributes

        :param customer: the customer associated to this education object
        :param parent_attr: the parent attribute for compiling the mutation tracker dictionary
        :param attributes: key-value arguments for generating the structure of the Education's attributes
        :param properties_class: reference to the actual Properties class
        :return: a new Education object
        """

        o = cls(customer=customer, parent_attr=parent_attr, properties_class=properties_class)
        o.attributes = {} if attributes is None else attributes
        return o

    def to_dict(self):
        """
        Convert this Education in a dictionary containing his attributes.

        :return: a new dictionary representing the attributes of this Education
        """
        return deepcopy(self.attributes)

    def __getattr__(self, item):
        """
        Check if a key is in the dictionary and return it if it's a simple properties

        :param item: the key of the base properties dict
        :return: the item in the attributes dictionary if it's present, raise AttributeError otherwise.
        """
        try:
            return self.attributes[item]
        except KeyError as e:
            raise AttributeError("%s object has no attribute %s" % (type(self).__name__, e))

    def __setattr__(self, attr, val):
        """
        x.__setattr__('attr', val) <==> x.attr = val
        Update the attributes dictionary with the val specified.
        """
        if attr in self.__attributes__:
            return super(Education, self).__setattr__(attr, val)
        else:
            self.attributes[attr] = val
            if self.parent_attr:
                attr = self.parent_attr.split('.')[-1:][0]
                base_attr = self.parent_attr.split('.')[-2:][0]
                self.customer.mute[base_attr + '.' + attr] = self.customer.attributes[base_attr][attr]

    def post(self):
        """
        Post this Education in the list of the Education for a Customer(specified in the constructor of the Education)

        :return: a Education object representing the posted Education
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
        Remove this Education from the list of the Education for a Customer(specified in the constructor of
        the Education)

        :return: a Education object representing the deleted Education
        """
        self.customer_api_manager.delete(_id=self.customer.id, urls_extra=self.entity_name + '/' + self.attributes['id'])

    def put(self):
        """
        Put this Education in the list of the Education for a Customer(specified in the constructor of the Education)

        :return: a Education object representing the putted Education
        """
        try:
            find = False
            for education in self.customer.attributes['base'][self.entity_name]:
                if self.attributes['id'] == education['id']:
                    find = True
            if not find:
                raise ValueError("Education object doesn't exists in the specified customer")
        except KeyError as e:
            raise ValueError("Education object doesn't exists in the specified customer")

        entity_attrs = self.customer_api_manager.put(_id=self.customer.id, body=self.attributes,
                                                     urls_extra=self.entity_name + '/' + self.attributes['id'])

        for education in self.customer.attributes['base'][self.entity_name]:
            if education['id'] == entity_attrs['id']:
                index = self.customer.attributes['base'][self.entity_name].index(education)
                self.customer.attributes['base'][self.entity_name][index] = entity_attrs

    class SCHOOL_TYPES:
        """
        Subclasses with school types for the schoolType field of Education
        """
        PRIMARY_SCHOOL = 'PRIMARY_SCHOOL'
        SECONDARY_SCHOOL = 'SECONDARY_SCHOOL'
        HIGH_SCHOOL = 'HIGH_SCHOOL'
        COLLEGE = 'COLLEGE'
        OTHER = 'OTHER'


