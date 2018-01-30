# coding=utf-8
import logging

from mailchimp.exceptions import MCInterestNotFound, MCCategoryListNotFound, ObjectNotFound
from mailchimp import Request

from .base_object import BaseObject
from .mc_link import MCLink

logger = logging.getLogger(__name__)


class MCInterest(BaseObject):
    item_url = '/lists/{list_id}/interest-categories/{category_id}/interests'

    def __init__(self, json_data={}):
        super(MCInterest, self).__init__()
        self._update(json_data)

    def _update(self, json_data):
        self.id = json_data.get("id")
        self.category_id = json_data.get("category_id")
        self.list_id = json_data.get("list_id")
        self.name = json_data.get("name")
        self.display_order = json_data.get("display_order")
        self.subscriber_count = json_data.get("subscriber_count")
        self.links = [MCLink(link) for link in json_data.get('_links')] if json_data.get('_links') else []

    @classmethod
    def get_list_url(cls, list_id, category_id):
        """
        Replace the placeholder for the list id with the list id sent to the method and replace the placeholder for
         the category id with the category id sent to the method - creates a valid url.

        :param list_id: the list to get the url for
        :param category_id: the category to get the url for

        :return: the url for the list
        """
        return cls.item_url.replace("{list_id}", list_id).replace("{category_id}", category_id)

    @classmethod
    def get(cls, list_id, category_id, interest_id):
        """
        Get the category from the mailchimp API. list_id has to be a valid list, category_id has to be a valid category
        and interest_id should be the id of the interest to retrieve.

        :param list_id: the list id to get the interest from
        :param category_id: the category to get the interest from
        :param interest_id: the interest to get

        :return: a MCInterest object containing the interest if successful, raises an MCInterestNotFound
        exception otherwise
        """
        try:
            response = Request.get("%s/%s" % (MCInterest.get_list_url(list_id, category_id), interest_id))
            return MCInterest(response.json())

        except ObjectNotFound:
            raise MCInterestNotFound(list_id, category_id, interest_id)

    @classmethod
    def list(cls, list_id, category_id, params={}):
        """
        Get the list of categories for the list corresponding with the id list_id from the mailchimp API.

        :param list_id: the id of the list to get members from
        :param category_id: the category to get

        :param params: parameters for defining limits for the search - can be used to page result or search for a
        specific status.

        :return: an array of MCInterest objects if successful, raises a MCListNotFound exception otherwise
        """
        try:
            response = Request.get("%s" % MCInterest.get_list_url(list_id, category_id), params)
            return [MCInterest(interest) for interest in response.json()['interests']]

        except ObjectNotFound:
            raise MCCategoryListNotFound(list_id, category_id)
