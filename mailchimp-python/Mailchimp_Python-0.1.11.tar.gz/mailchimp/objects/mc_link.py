# coding=utf-8
from .base_object import BaseObject


class MCLink(BaseObject):
    item_url = None

    def __init__(self, json_data={}):
        super(MCLink, self).__init__()
        self.rel = None
        self.href = None
        self.method = None
        self.targetSchema = None

        if json_data:
            self.rel = json_data.get('rel')
            self.href = json_data.get('href')
            self.method = json_data.get('method')
            self.targetSchema = json_data.get('targetSchema')
