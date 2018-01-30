# coding=utf-8
from .base_object import BaseObject


class MCCampaignDefaults(BaseObject):
    item_url = None

    def __init__(self, json_data={}):
        super(MCCampaignDefaults, self).__init__()
        self.from_name = None
        self.from_email = None
        self.subject = None
        self.language = None

        if json_data:
            self.from_name = json_data.get('from_name')
            self.from_email = json_data.get('from_email')
            self.subject = json_data.get('subject')
            self.language = json_data.get('language')

    def to_dict(self):
        return {
            'from_name': self.from_name,
            'from_email': self.from_email,
            'subject': self.subject,
            'language': self.language
        }
