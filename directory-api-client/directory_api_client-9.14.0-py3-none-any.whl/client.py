from directory_client_core.base import BaseAPIClient

from directory_api_client.buyer import BuyerAPIClient
from directory_api_client.company import CompanyAPIClient
from directory_api_client.enrolment import EnrolmentAPIClient
from directory_api_client.supplier import SupplierAPIClient
from directory_api_client.notifications import NotificationsAPIClient
from directory_api_client.exportopportunity import ExportOpportunityAPIClient
from directory_api_client.exportreadiness import ExportReadinessAPIClient


class DirectoryAPIClient(BaseAPIClient):

    endpoints = {
        'ping': 'healthcheck/ping/',
    }

    def __init__(self, base_url=None, api_key=None):
        super(DirectoryAPIClient, self).__init__(base_url, api_key)

        self.enrolment = EnrolmentAPIClient(base_url, api_key)
        self.company = CompanyAPIClient(base_url, api_key)
        self.supplier = SupplierAPIClient(base_url, api_key)
        self.buyer = BuyerAPIClient(base_url, api_key)
        self.notifications = NotificationsAPIClient(base_url, api_key)
        self.exportopportunity = ExportOpportunityAPIClient(base_url, api_key)
        self.exportreadiness = ExportReadinessAPIClient(base_url, api_key)

    def ping(self):
        return self.get(url=self.endpoints['ping'])
