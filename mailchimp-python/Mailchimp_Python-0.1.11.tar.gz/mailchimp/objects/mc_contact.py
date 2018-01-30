# coding=utf-8
from .base_object import BaseObject


class MCContact(BaseObject):
    item_url = None

    def __init__(self, json_data={}):
        super(MCContact, self).__init__()
        self.company = None
        self.address1 = None
        self.address2 = None
        self.city = None
        self.state = None
        self.zip = None
        self.country = None
        self.phone = None

        if json_data:
            self.company = json_data.get('company')
            self.address1 = json_data.get('address1')
            self.address2 = json_data.get('address2')
            self.city = json_data.get('city')
            self.state = json_data.get('state')
            self.zip = json_data.get('zip')
            self.country = json_data.get('country')
            self.phone = json_data.get('phone')

    def to_dict(self):
        return {
            'company': self.company,
            'address1': self.address1,
            'address2': self.address2,
            'city': self.city,
            'state': self.state,
            'zip': self.zip,
            'country': self.country,
            'phone': self.phone
        }
