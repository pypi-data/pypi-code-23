from directory_client_core.base import BaseAPIClient


class DirectoryTestAPIClient(BaseAPIClient):

    endpoints = {
        'company_by_ch_id': 'testapi/company/{ch_id}/',
        'published_companies': 'testapi/companies/published/'
    }

    def get_url(self, ch_id):
        return self.endpoints['company_by_ch_id'].format(ch_id=ch_id)

    def get_company_by_ch_id(self, ch_id):
        url = self.get_url(ch_id)
        return self.get(url=url)

    def delete_company_by_ch_id(self, ch_id):
        url = self.get_url(ch_id)
        return self.delete(url=url)

    def get_published_companies(
            self, *, limit=None, minimal_number_of_sectors=None):
        url = self.endpoints['published_companies']
        params = {}
        if limit:
            params['limit'] = limit
        if minimal_number_of_sectors:
            params['minimal_number_of_sectors'] = minimal_number_of_sectors
        return self.get(url=url, params=params)
