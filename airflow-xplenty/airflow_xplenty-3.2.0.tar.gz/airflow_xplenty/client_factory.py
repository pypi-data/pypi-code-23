from airflow import configuration
from xplenty import Job, XplentyClient


# Since the base XplentyClient must support v1 and v2 of the Xplenty API, the
# core team for xplenty.py does not want to add support for features that are
# specific to v2 of the API (e.g. the `outputs` field in the get jobs response).
#
# @see https://github.com/xplenty/xplenty.py/pull/23
class XplentyV2Client(XplentyClient):
    def get_job(self, id):
        method_path = 'jobs/%s' % str(id)
        url = self._join_url(method_path)
        resp = self.get(url)

        # BaseModel.new_from_dict allows us to add arbitrary attributes in
        # **kwargs.
        return Job.new_from_dict(resp, h=self, outputs=resp['outputs'])


"""Convenience factory for constructing an XplentyClient with proper credentials"""
class ClientFactory:
    def __init__(self):
        self.account_id = configuration.get('xplenty', 'account_id')
        self.api_key = configuration.get('xplenty', 'api_key')

    def client(self):
        return XplentyV2Client(self.account_id, self.api_key)
