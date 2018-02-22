# -*- coding: utf-8 -*-
from copy import deepcopy
from contacthub.lib.read_only_list import ReadOnlyList
from contacthub.lib.utils import generate_mutation_tracker, convert_properties_obj_in_prop
from contacthub.models.education import Education
from contacthub.models.job import Job
from contacthub.models.like import Like
from contacthub.models.subscription import Subscription


class Properties(object):
    """
    Generic Properties for all entities
    """
    __SUBPROPERTIES_LIST__ = {'educations': Education, 'likes': Like, 'jobs': Job, 'subscriptions': Subscription}

    __attributes__ = ('attributes', 'parent_attr', 'mute', 'parent')

    def __init__(self, parent=None, parent_attr=None, **attributes):
        """
        :param parent: the parent that generate this Properties object
        :param parent_attr: the parent attribute for compiling the mutation tracker dictionary
        :param attributes: key-value arguments for generating the structure of the Properties's attributes
        """
        self.parent = parent
        self.mute = {}
        self.parent_attr = parent_attr
        if self.parent:
            try:
                self.mute = parent.mute
            except AttributeError:
                self.mute = parent.customer.mute

        convert_properties_obj_in_prop(properties=attributes, properties_class=Properties)
        self.attributes = attributes

    def __repr__(self):
        return str(self.attributes)

    @classmethod
    def from_dict(cls, parent=None, parent_attr=None, attributes=None):
        """
        Create a new Properties initialized by a specified dictionary of attributes

        :param parent: the parent that generate this Properties object
        :param parent_attr: the parent attribute for compiling the mutation tracker dictionary
        :param attributes: key-value arguments for generating the structure of the Education's attributes
        :return: a new Properties object
        """
        o = cls(parent=parent, parent_attr=parent_attr)
        o.attributes = {} if attributes is None else attributes
        return o

    def to_dict(self):
        """
        Convert this Properties object in a dictionary containing his attributes.

        :return: a new dictionary representing the attributes of this Properties
        """
        return deepcopy(self.attributes)

    def __getattr__(self, item):
        """
        Check if a key is in the dictionary and return it if it's a simple Properties. Otherwise, if the
        element contains an object or list, redirect this element at the corresponding class.

        :param item: the key of the base Properties dict
        :return: an element of the dictionary, or an object if the element associated at the key contains an object or
        a list
        """
        try:
            parent_attr = item if not self.parent_attr else self.parent_attr + '.' + item
            if item in self.__SUBPROPERTIES_LIST__:
                return ReadOnlyList([self.__SUBPROPERTIES_LIST__[item].from_dict(customer=self.parent,
                                                                                 attributes=elements,
                                                                                 parent_attr=parent_attr,
                                                                                 properties_class=Properties)
                                     for elements in self.attributes[item]])
            if isinstance(self.attributes[item], dict):
                return Properties.from_dict(parent_attr=parent_attr, parent=self,
                                            attributes=self.attributes[item])
            if isinstance(self.attributes[item], list):
                if self.attributes[item] and isinstance(self.attributes[item][0], dict):
                    return ReadOnlyList([Properties.from_dict(parent_attr=parent_attr, parent=self, attributes=elem)
                                         for elem in self.attributes[item]])
                else:
                    return ReadOnlyList(self.attributes[item])
            return self.attributes[item]
        except KeyError as e:
            raise AttributeError("%s object has no attribute %s" % (type(self).__name__, e))

    def __setattr__(self, attr, val):
        """
        x.__setattr__('attr', val) <==> x.attr = val
        If `val` is simple type value (dictionary, list, str, int, ecc.), update the attributes dictionary with new
        values, otherwise, if `val` is instance of Properties, check for mutations in the Properties object.
        This method generate the mutation tracker dictionary.
        """
        if attr in self.__attributes__:
            return super(Properties, self).__setattr__(attr, val)
        else:
            if isinstance(val, Properties):
                if self.parent:
                    try:
                        mutations = generate_mutation_tracker(self.attributes[attr], val.attributes)
                        update_tracking_with_new_prop(mutations, val.attributes)
                        self.mute[self.parent_attr + '.' + attr] = mutations
                    except KeyError as e:
                        self.mute[attr] = val.attributes
                self.attributes[attr] = val.attributes
            else:
                if isinstance(val, list):
                    self.attributes[attr] = []
                    for elem in val:
                        try:
                            self.attributes[attr] += [elem.attributes]
                        except AttributeError as e:
                            self.attributes[attr] += [elem]
                else:
                    self.attributes[attr] = val
                if self.parent:
                    field = self.parent_attr.split('.')[-1:][0]
                    if isinstance(self.parent.attributes[field], list):
                        self.mute[self.parent_attr] = self.parent.attributes[field]
                    elif isinstance(self.parent.attributes[field][attr], list):
                        if self.parent_attr in self.mute:
                            self.mute[self.parent_attr][attr] = self.parent.attributes[field][attr]
                        else:
                            self.mute[self.parent_attr + '.' + attr] = self.parent.attributes[field][attr]
                    else:
                        self.mute[self.parent_attr + '.' + attr] = val


def update_tracking_with_new_prop(mutations, new_properties):
    """
    Add at the mutation tracker the new properties assigned with the setattr at a Properties object

    :param mutations: the dictionary representing the mutation tracker
    :param new_properties: the properties to check for adding new attributes to the mutation tracker
    """
    for key in new_properties:
        if (key not in mutations or mutations[key] is None or not mutations[key]) and \
                not isinstance(new_properties[key], dict):
            mutations[key] = new_properties[key]
        elif isinstance(new_properties[key], dict):
            mutations[key] = {}
            update_tracking_with_new_prop(mutations[key], new_properties[key])
