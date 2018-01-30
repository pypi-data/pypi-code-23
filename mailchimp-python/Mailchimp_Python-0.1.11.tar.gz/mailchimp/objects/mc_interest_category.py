# coding=utf-8
import logging

from mailchimp.exceptions import MCInterestCategoryNotFound, MCListNotFound, ObjectNotFound
from mailchimp import Request

from .base_object import BaseObject
from .mc_link import MCLink

logger = logging.getLogger(__name__)


class MCInterestCategory(BaseObject):
    item_url = '/lists/{list_id}/interest-categories'

    def __init__(self, json_data={}):
        super(MCInterestCategory, self).__init__()
        self._update(json_data)

    def _update(self, json_data):
        self.id = json_data.get("id")
        self.list_id = json_data.get("list_id")
        self.title = json_data.get("title")
        self.display_order = json_data.get("display_order")
        self.type = json_data.get("type")
        self.links = [MCLink(link) for link in json_data.get('_links')] if json_data.get('_links') else []

    @classmethod
    def get_list_url(cls, list_id):
        """
        Replace the placeholder for the list id with the list id sent to the method - creates a valid url.

        :param list_id: the list to get the url for

        :return: the url for the list
        """
        return cls.item_url.replace("{list_id}", list_id)

    @classmethod
    def get(cls, list_id, category_id):
        """
        Get the category from the mailchimp API. list_id has to be a valid list and category_id should be the
        id of the category to retrieve.

        :param list_id: the list id to get the category from
        :param category_id: the category to get

        :return: a MCInterestCategory object containing the category if successful, raises an MCInterestCategoryNotFound
        exception otherwise
        """
        try:
            response = Request.get("%s/%s" % (MCInterestCategory.get_list_url(list_id), category_id))
            return MCInterestCategory(response.json())

        except ObjectNotFound:
            raise MCInterestCategoryNotFound(list_id, category_id)

    @classmethod
    def list(cls, list_id, params={}):
        """
        Get the list of categories for the list corresponding with the id list_id from the mailchimp API.

        :param list_id: the id of the list to get members from
        :param params: parameters for defining limits for the search - can be used to page result or search for a
        specific status.

        :return: an array of MCInterestCategory objects if successful, raises a MCListNotFound exception otherwise
        """
        try:
            response = Request.get("%s" % MCInterestCategory.get_list_url(list_id), params)
            return [MCInterestCategory(category) for category in response.json()['categories']]

        except ObjectNotFound:
            raise MCListNotFound(list_id)

    def delete(self):
        """
        Deletes the current category from the list

        :return: True if successful
        """
        if not self.id:
            return False

        try:
            Request.delete("%s/%s" % (MCInterestCategory.get_list_url(self.list_id), self.id))
            return True

        except Exception as e:
            logger.error("Unable to delete member from list")
            raise e

    def save(self):
        """
        Saves the current category to the list

        :return: True if successful
        """
        hash_value = self.id

        if not self.id:
            md = hashlib.md5()
            md.update(self.email_address.lower().encode("utf-8"))
            hash_value = md.hexdigest()

        try:
            response = Request.put("%s/%s" % (MCMember.get_list_url(self.list_id), hash_value),
                                   self.to_dict())
            self._update(response.json())
            return True

        except Exception as e:
            logger.error("Unable to save member")
            raise e
