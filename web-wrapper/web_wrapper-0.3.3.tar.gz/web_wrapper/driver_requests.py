import sys
import requests
from web_wrapper.web import Web
import logging

logger = logging.getLogger(__name__)


class DriverRequests(Web):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver_type = 'requests'

        self._create_session()

    # Headers Set/Get
    def get_headers(self):
        return self.driver.headers

    def set_headers(self, headers):
        self.driver.headers = headers

    def update_headers(self, headers):
        self.driver.headers.update(headers)

    # Cookies Set/Get
    def get_cookies(self):
        return self.driver.cookies.get_dict()

    def set_cookies(self, cookies):
        safe_cookies = {}
        if isinstance(cookies, list) is True:
            for cookie in cookies:
                safe_cookies.update({'name': cookie.get('name', ''), 'value': cookie.get('value', '')})

        else:
            safe_cookies = cookies

        self.driver.cookies = safe_cookies

    def update_cookies(self, cookies):
        if isinstance(cookies, list) is True:
            for cookie in cookies:
                safe_cookie = {cookie.get('name', ''): cookie.get('value', '')}
                self.driver.cookies.update(safe_cookie)
        else:
            self.driver.cookies.update(cookies)

    # Proxy Set/Get
    def set_proxy(self, proxy):
        """
        Set proxy for requests session
        """
        # TODO: Validate proxy url format

        if proxy is None:
            self.driver.proxies = {'http': None,
                                   'https': None
                                   }
        else:
            self.driver.proxies = {'http': proxy,
                                   'https': proxy
                                   }

        self.current_proxy = proxy

    def get_proxy(self):
        return self.current_proxy

    # Session
    def _create_session(self):
        """
        Creates a fresh session with the default header (random UA)
        """
        self.driver = requests.Session(**self.driver_args)
        # Set default headers
        self.update_headers(self.current_headers)
        self.update_cookies(self.current_cookies)
        self.set_proxy(self.current_proxy)

    def reset(self):
        """
        Kills old session and creates a new one with the default headers
        """
        self.driver = None
        self._create_session()

    def quit(self):
        """
        Generic function to close distroy and session data
        """
        self.driver = None

    # Actions
    def _get_site(self, url, page_format, headers, cookies, timeout, driver_args, driver_kwargs, parser):
        """
        Try and return page content in the requested format using requests
        """
        try:
            # Headers and cookies are combined to the ones stored in the requests session
            #  Ones passed in here will override the ones in the session if they are the same key
            response = self.driver.get(url,
                                       *driver_args,
                                       headers=headers,
                                       cookies=cookies,
                                       timeout=timeout,
                                       **driver_kwargs)

            # Set data to access from script
            self.status_code = response.status_code
            self.url = response.url
            self.response = response

            if response.status_code == requests.codes.ok:
                # Return the correct format
                return self.parse_source(response.text, page_format, parser)

            response.raise_for_status()

        except Exception as e:
            raise e.with_traceback(sys.exc_info()[2])
