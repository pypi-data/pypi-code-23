import requests


class XreaError(Exception):
    pass


class XreaApiResponseError(XreaError):
    def __init__(self, api_response):
        self.api_response = api_response

    def __str__(self):
        def _msg():
            return self.error_message or self.message or ''

        def _code():
            if self.error_code and self.status_code:
                return '[status: {}, error: {}]'.format(
                    self.status_code, self.error_code)
            elif self.error_code:
                return '[error: {}]'.format(self.error_code)
            elif self.status_code:
                return '[status: {}]'.format(self.status_code)
            else:
                return ''

        if self.error_code or self.status_code:
            return _code() + _msg()

        try:
            self.api_response.raw_response.raise_for_status()
        except requests.HTTPError as err:
            return str(err)

        return 'HTTP status code: {}'.format(
            self.api_response.http_status_code)

    @property
    def error_code(self):
        return self.api_response.json.get('error_code')

    @property
    def error_message(self):
        return self.api_response.json.get('error_message')

    @property
    def message(self):
        return self.api_response.json.get('message')

    @property
    def status_code(self):
        return self.api_response.json.get('status_code')
