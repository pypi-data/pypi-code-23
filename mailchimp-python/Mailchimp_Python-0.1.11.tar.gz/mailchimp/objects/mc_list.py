# coding=utf-8
import logging

from mailchimp.exceptions import MCListNotFound, ObjectNotFound
from mailchimp import Request

from .base_object import BaseObject
from .mc_campaign_defaults import MCCampaignDefaults
from .mc_contact import MCContact
from .mc_link import MCLink
from .mc_list_stats import MCListStats

logger = logging.getLogger(__name__)


class MCList(BaseObject):
    item_url = '/lists'

    def __init__(self, json_data={}):
        super(MCList, self).__init__()
        self.valid_search_params = self.valid_search_params + ['before_date_created', 'since_date_created']
        self.id = json_data.get('id')
        self.name = json_data.get('name')
        self.contact = MCContact(json_data.get('contact'))
        self.permission_reminder = json_data.get('permission_reminder')
        self.user_archive_bar = json_data.get('use_archive_bar')
        self.campaign_defaults = MCCampaignDefaults(json_data.get('campaign_defaults'))
        self.notify_on_subscribe = json_data.get('notify_on_subscribe')
        self.notify_on_unsubscribe = json_data.get('notify_on_unsubscribe')
        self.date_created = self._parse_date(json_data.get('date_created')) if json_data.get('date_created') else None
        self.list_rating = json_data.get('list_rating')
        self.email_type_option = json_data.get('email_type_option')
        self.subscribe_url_short = json_data.get('subscribe_url_short')
        self.subscribe_url_long = json_data.get('subscribe_url_long')
        self.beamer_address = json_data.get('beamer_address')
        self.visibility = json_data.get('visibility')
        self.modules = json_data.get('modules')
        self.stats = MCListStats(json_data.get('stats'))
        self.links = [MCLink(link) for link in json_data.get('_links')] if json_data.get('_links') else []

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact': self.contact.to_dict(),
            'permission_reminder': self.permission_reminder,
            'user_archive_bar': self.user_archive_bar,
            'campaign_defaults': self.campaign_defaults.to_dict(),
            'notify_on_subscribe': self.notify_on_subscribe,
            'notify_on_unsubscribe': self.notify_on_unsubscribe,
            'email_type_option': self.email_type_option,
            'visibility': self.visibility
        }

    @classmethod
    def get(cls, list_id):
        """
        Get the list corresponding with the id list_id from the mailchimp API.

        :param list_id: the id of the list to get

        :return: the MCList item if successful, raises a ListNotFound exception otherwise
        """
        try:
            response = Request.get("%s/%s" % (cls.item_url, list_id))
            content = response.json()
            return MCList(content)

        except ObjectNotFound:
            raise MCListNotFound(list_id)

    @classmethod
    def list(cls, params={}):
        """
        Get all list items from the mailchimp API for the current user.

        :param params: parameters for defining limits for the search - can be used to page result.

        :return: a list of MCList items.
        """
        search_params = {}
        lists = []

        if params:
            for key in params.keys():
                if key in cls.valid_search_params:
                    search_params[key] = params[key]

        response = Request.get(cls.item_url, search_params)
        content = response.json()

        if 'lists' in content:
            for list_item in content['lists']:
                lists.append(MCList(list_item))

        return lists
