from directory_client_core.base import BaseAPIClient


class DirectoryCMSClient(BaseAPIClient):

    endpoints = {
        'page': '/api/pages/{page_id}/',
    }

    def get_page(self, page_id, draft_token=None, language_code=None):
        params = {}
        if draft_token:
            params['draft_token'] = draft_token
        if language_code:
            params['lang'] = language_code
        url = self.endpoints['page'].format(page_id=page_id)
        return self.get(url, params=params)
