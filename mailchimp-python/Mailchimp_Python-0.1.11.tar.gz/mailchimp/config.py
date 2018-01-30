# coding=utf-8


class Config:
    def __init__(self):
        self.api_key = None
        self.base_api_url = 'https://api.mailchimp.com/3.0'

    def get_server_url(self):
        """
        Gets the correct server url for the current api key (if specified). Checks the api key for the datacenter and
        adds it to the base_api_url string.

        :return: the correct server url for the current api key.
        """
        dc = 'us1'

        if self.api_key and self.api_key.find('-'):
            dc = self.api_key.split('-')[1]

        return self.base_api_url.replace('https://api.', 'https://%s.api.' % dc)

mailchimp_config = Config()
