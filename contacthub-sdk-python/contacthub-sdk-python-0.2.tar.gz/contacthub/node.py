# -*- coding: utf-8 -*-
from contacthub._api_manager._api_customer import _CustomerAPIManager
from contacthub._api_manager._api_event import _EventAPIManager
from contacthub.lib.paginated_list import PaginatedList
from contacthub.lib.utils import resolve_mutation_tracker, convert_properties_obj_in_prop
from contacthub.models import Properties
from contacthub.models.customer import Customer
from contacthub.models.education import Education
from contacthub.models.event import Event
from contacthub.models.job import Job
from contacthub.models.like import Like
from contacthub.models.query.query import Query
import uuid

from contacthub.models.subscription import Subscription


class Node(object):
    """
    Node class for accessing data on a Contacthub node.
    """

    def __init__(self, workspace, node_id):
        """
        :param workspace: A Workspace Object for authenticating on Contacthub
        :param node_id: The id of the Contacthub node
        """
        self.workspace = workspace
        self.node_id = str(node_id)
        self.customer_api_manager = _CustomerAPIManager(node=self)
        self.event_api_manager = _EventAPIManager(node=self)

    def get_customers(self, external_id=None, page=None, size=None, fields=None):
        """
        Get all the customers in this node

        :param external_id: the external id of the customer to retrieve
        :param size: the size of the pages containing customers
        :param page: the number of the page for retrieve customer data
        :param fields: : a list of strings representing the properties to include in the response
        :return: A list containing Customer object of a node
        """
        return PaginatedList(node=self, function=self.customer_api_manager.get_all, entity_class=Customer,
                             externalId=external_id, page=page, size=size, fields=fields)

    def get_customer(self, id=None, external_id=None):
        """
        Retrieve a customer from the associated node by its id or external ID. Only one parameter can be specified for
        getting a customer.

        :param id: the id of the customer to retrieve
        :param external_id: the external id of the customer to retrieve
        :return: a Customer object representing the fetched customer
        """
        if id and external_id:
            raise ValueError('Cannot get a customer by both its id and external_id')
        if not id and not external_id:
            raise ValueError('Insert an id or an external_id')

        if external_id:
            customers = self.get_customers(external_id=external_id)
            if len(customers) == 1:
                return customers[0]
            else:
                return customers
        else:
            return Customer(node=self, **self.customer_api_manager.get(_id=id))

    def query(self, entity):
        """
        Create a QueryBuilder object for a given entity, that allows to filter the entity's data

        :param entity: A class of model on which to run the query
        :return: A QueryBuilder object for the specified entity
        """
        return Query(node=self, entity=entity)

    def delete_customer(self, id, **attributes):
        """
        Delete the specified Customer from contacthub. For deleting an existing customer object, you should::

            node.delete_customer(**c.to_dict())

        :param id: a the id of the customer to delete
        :param attributes: the attributes of the customer to delete
        :return: an object representing the deleted customer
        """
        return Customer(node=self, **self.customer_api_manager.delete(_id=id))

    def add_customer(self, force_update=False, **attributes):
        """
        Add a new customer in contacthub. If the customer already exist and force update is true, this method will update
        the entire customer with new data

        :param attributes: the attributes for inserting the customer in the node
        :param force_update: a flag for update an already present customer
        :return: the customer added or updated
        """
        convert_properties_obj_in_prop(properties=attributes, properties_class=Properties)
        return Customer(node=self, **self.customer_api_manager.post(body=attributes, force_update=force_update))

    def update_customer(self, id, full_update=False, **attributes):
        """
        Update a customer in contacthub with new data. If full_update is true, this method will update the full customer (PUT)
        and not only the changed data (PATCH)

        :param id: the customer ID for updating the customer with new attributes
        :param full_update: a flag for execute a full update to the customer
        :param attributes: the attributes to patch or put in the customer
        :return: the customer updated
        """
        convert_properties_obj_in_prop(properties=attributes, properties_class=Properties)
        if full_update:
            attributes['id'] = id
            return Customer(node=self, **self.customer_api_manager.put(_id=id, body=attributes))
        else:
            return Customer(node=self, **self.customer_api_manager.patch(_id=id, body=attributes))

    def add_customer_session(self, customer_id, session_id):
        """
        Add a new session id for a customer.

        :param customer_id: the customer ID for adding the session id
        :param session_id: a session ID for create a new session
        :return: the session id of the new session inserted
        """
        body = {'value': str(session_id)}
        return self.customer_api_manager.post(body=body, urls_extra=customer_id + '/sessions')['value']

    @staticmethod
    def create_session_id():
        """
        Create a new random session id conformed to the UUID standard

        :return: a new session id conformed to the UUID standard
        """
        return str(uuid.uuid4())

    def add_tag(self, customer_id, tag):
        """
        Add a new tag in the list of customer's tags

        :param customer_id: the id customer in which adding the tag
        :param tag: a string, int, representing the tag to add
        """
        customer = self.get_customer(id=customer_id)
        new_tags = customer.tags.manual
        new_tags += [tag]
        customer.tags.manual = new_tags
        self.update_customer(id=customer_id, **resolve_mutation_tracker(customer.mute))

    def remove_tag(self, customer_id, tag):
        """
        Remove (if exists) a tag in the list of customer's tag

        :param customer_id: the id customer in which adding the tag
        :param tag: a string, int, representing the tag to add
        """
        customer = self.get_customer(id=customer_id)
        new_tags = list(customer.tags.manual)
        try:
            new_tags.remove(tag)
            customer.tags.manual = new_tags
            self.update_customer(id=customer_id, **resolve_mutation_tracker(customer.mute))
        except ValueError as e:
            raise ValueError("Tag not in Customer's Tags")

    def get_customer_job(self, customer_id, job_id):
        """
        Get a job associated to a customer by its ID

        :param job_id: the unique id of the job to get in a customer
        :param customer_id: the id of the customer for getting the job
        :return: a new Job object containing the attributes associated to the job
        """
        return Job(customer=self.get_customer(id=customer_id), **self.customer_api_manager.get(_id=customer_id, urls_extra='jobs/' +
                                                                                                         job_id))

    def add_job(self, customer_id, **attributes):
        """
        Insert a new Job for the given Customer

        :param customer_id: the id of the customer for adding the job
        :param attributes: the attributes representing the new job to add
        :return: a Job object representing the added Job
        """
        entity_attrs = self.customer_api_manager.post(body=attributes, urls_extra=customer_id + '/jobs')
        return Job(customer=self.get_customer(id=customer_id), **entity_attrs)

    def remove_job(self, customer_id, job_id):
        """
        Remove a the given Job for the given Customer

        :param customer_id: the id of the customer associated to the job to remove
        :param job_id: the id of the job to remove
        """
        self.customer_api_manager.delete(_id=customer_id, urls_extra='jobs/' + job_id)

    def update_job(self, customer_id, id, **attributes):
        """
        Update the given job of the given customer with new specified attributes

        :param customer_id: the id of the customer associated to the job to update
        :param id: the id of the job to update
        :param attributes: the attributes for update the job
        :return: a Job object representing the updated Job
        """
        entity_attrs = self.customer_api_manager.put(_id=customer_id, body=attributes, urls_extra='jobs/' + id)
        return Job(customer=self.get_customer(id=customer_id), **entity_attrs)

    def get_customer_like(self, customer_id, like_id):
        """
        Get a like associated to a customer by its ID

        :param like_id: the unique id of the like to get in a customer
        :param customer_id: the id of the customer for getting the like
        :return: a new Like object containing the attributes associated to the like
        """
        return Like(customer=self.get_customer(id=customer_id), **self.customer_api_manager.get(_id=customer_id, urls_extra='likes/' +
                                                                                                         like_id))

    def add_like(self, customer_id, **attributes):
        """
        Insert a new Like for the given Customer

        :param customer_id: the id of the customer for adding the Like
        :param attributes: the attributes representing the new Like to add
        :return: a Like object representing the added Like
        """
        entity_attrs = self.customer_api_manager.post(body=attributes, urls_extra=customer_id + '/likes')
        return Like(customer=self.get_customer(id=customer_id), **entity_attrs)

    def remove_like(self, customer_id, like_id):
        """
        Remove a the given Like for the given Customer

        :param customer_id: the id of the customer associated to the Like to remove
        :param like_id: the id of the Like to remove
        """
        self.customer_api_manager.delete(_id=customer_id, urls_extra='likes/' + like_id)

    def update_like(self, customer_id, id, **attributes):
        """
        Update the given Like of the given customer with new specified attributes

        :param customer_id: the id of the customer associated to the Like to update
        :param id: the id of the Like to update
        :param attributes: the attributes for update the Like
        :return: a Like object representing the updated Like
        """
        entity_attrs = self.customer_api_manager.put(_id=customer_id, body=attributes, urls_extra='likes/' + id)
        return Like(customer=self.get_customer(id=customer_id), **entity_attrs)

    def get_customer_education(self, customer_id, education_id):
        """
        Get an education associated to a customer by its ID

        :param education_id: the unique id of the education to get in a customer
        :param customer_id: the id of the customer for getting the education
        :return: a new Education object containing the attributes associated to the education
        """
        return Education(customer=self.get_customer(id=customer_id), **self.customer_api_manager.get(_id=customer_id, urls_extra='educations/' +
                                                                                                         education_id))

    def add_education(self, customer_id, **attributes):
        """
        Insert a new Education for the given Customer

        :param customer_id: the id of the customer for adding the Education
        :param attributes: the attributes representing the new Education to add
        :return: a Education object representing the added Education
        """
        entity_attrs = self.customer_api_manager.post(body=attributes, urls_extra=customer_id + '/educations')
        return Education(customer=self.get_customer(id=customer_id), **entity_attrs)

    def remove_education(self, customer_id, education_id):
        """
        Remove a the given Education for the given Customer

        :param customer_id: the id of the customer associated to the Education to remove
        :param education_id: the id of the Education to remove
        """
        self.customer_api_manager.delete(_id=customer_id, urls_extra='educations/' + education_id)

    def update_education(self, customer_id, id, **attributes):
        """
        Update the given Education of the given customer with new specified attributes

        :param customer_id: the id of the customer associated to the Education to update
        :param id: the id of the Education to update
        :param attributes: the attributes for update the Education
        :return: a Education object representing the updated Education
        """
        entity_attrs = self.customer_api_manager.put(_id=customer_id, body=attributes, urls_extra='educations/' + id)
        return Education(customer=self.get_customer(id=customer_id), **entity_attrs)

    def get_events(self, customer_id, event_type=None, context=None, event_mode=None, date_from=None, date_to=None,
                   page=None, size=None):
        """
        Get all events associated to a customer.

        :param customer_id: The id of the customer owner of the event
        :param event_type: the type of the event present in Event.TYPES
        :param context: the context of the event present in Event.CONTEXT
        :param event_mode: the mode of event. ACTIVE if the customer made the event, PASSIVE if the customer recive the event
        :param date_from: From string or datetime for search of event
        :param date_to: From string or datetime for search of event
        :param size: the size of the pages containing events
        :param page: the number of the page for retrieve event data
        :return: a list containing the fetched events associated to the given customer id
        """
        return PaginatedList(node=self, function=self.event_api_manager.get_all, entity_class=Event,
                             customer_id=customer_id, type=event_type, mode=event_mode, dateFrom=date_from,
                             dateTo=date_to, page=page, size=size, context=context)

    def get_event(self, id):
        """
        Get a single event by its own id

        :param id: the id of the event to get
        :return: a new Event object representing the fetched event
        """
        return Event(node=self, **self.event_api_manager.get(_id=id))

    def add_event(self, **attributes):
        """
        Add an event in this node. For adding it and associate with a known customer, specify the customer id in the
        attributes of the Event. For associate it to an external Id or a session id of a customer, specify in the
        bringBackProperties object like:
        {'type':'EXTERNAL_ID',
        'value':'value',
        'nodeId':'nodeId'
        }

        :param attributes: the attributes of the event to add in the node
        :return: a new Event object representing the event added in this node
        """
        convert_properties_obj_in_prop(properties=attributes, properties_class=Properties)
        self.event_api_manager.post(body=attributes)
        return Event(node=self, **attributes)

    def get_customer_subscription(self, customer_id, subscription_id):
        """
        Get an subscription associated to a customer by its ID

        :param subscription_id: the unique id of the subscription to get in a customer
        :param customer_id: the id of the customer for getting the subscription
        :return: a new Subscription object containing the attributes associated to the subscription
        """
        return Subscription(customer=self.get_customer(id=customer_id), properties_class=Properties,
                         **self.customer_api_manager.get(_id=customer_id, urls_extra='subscriptions/' +
                                                                                     subscription_id))

    def add_subscription(self, customer_id, **attributes):
        """
        Insert a new Subscription for the given Customer

        :param customer_id: the id of the customer for adding the Subscription
        :param attributes: the attributes representing the new Subscription to add
        :return: a Subscription object representing the added Subscription
        """
        entity_attrs = self.customer_api_manager.post(body=attributes, urls_extra=customer_id + '/subscriptions')
        return Subscription(customer=self.get_customer(id=customer_id), **entity_attrs)

    def remove_subscription(self, customer_id, subscription_id):
        """
        Remove a the given Subscription for the given Customer

        :param customer_id: the id of the customer associated to the Subscription to remove
        :param subscription_id: the id of the Subscription to remove
        """
        self.customer_api_manager.delete(_id=customer_id, urls_extra='subscriptions/' + subscription_id)

    def update_subscription(self, customer_id, id, **attributes):
        """
        Update the given Subscription of the given customer with new specified attributes

        :param customer_id: the id of the customer associated to the Subscription to update
        :param id: the id of the Subscription to update
        :param attributes: the attributes for update the Subscription
        :return: a Subscription object representing the updated Subscription
        """
        entity_attrs = self.customer_api_manager.put(_id=customer_id, body=attributes, urls_extra='subscriptions/' + id)
        return Subscription(customer=self.get_customer(id=customer_id), **entity_attrs)