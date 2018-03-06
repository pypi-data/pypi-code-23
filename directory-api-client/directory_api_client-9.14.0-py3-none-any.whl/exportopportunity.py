from directory_client_core.base import BaseAPIClient


class ExportOpportunityAPIClient(BaseAPIClient):

    endpoints = {
        'create-opportunity-food': '/export-opportunity/food/',
        'create-opportunity-legal': '/export-opportunity/legal/',

    }

    def create_opportunity_food(self, form_data):
        return self.post(
            self.endpoints['create-opportunity-food'],
            data=form_data
        )

    def create_opportunity_legal(self, form_data):
        return self.post(
            self.endpoints['create-opportunity-legal'],
            data=form_data
        )
