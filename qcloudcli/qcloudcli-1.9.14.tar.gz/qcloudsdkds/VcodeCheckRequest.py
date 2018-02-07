# -*- coding: utf-8 -*-

from qcloudsdkcore.request import Request

class VcodeCheckRequest(Request):

    def __init__(self):
        super(VcodeCheckRequest, self).__init__(
            'ds', 'qcloudcliV1', 'VcodeCheck', 'ds.api.qcloud.com')

    def get_contractResId(self):
        return self.get_params().get('contractResId')

    def set_contractResId(self, contractResId):
        self.add_param('contractResId', contractResId)

    def get_module(self):
        return self.get_params().get('module')

    def set_module(self, module):
        self.add_param('module', module)

    def get_operation(self):
        return self.get_params().get('operation')

    def set_operation(self, operation):
        self.add_param('operation', operation)

    def get_resid(self):
        return self.get_params().get('resid')

    def set_resid(self, resid):
        self.add_param('resid', resid)

    def get_verifyCode(self):
        return self.get_params().get('verifyCode')

    def set_verifyCode(self, verifyCode):
        self.add_param('verifyCode', verifyCode)
