import requests
import json
import atexit

from actappliance.models import ActResponse
from actappliance.connections.connection import ApplianceConnection

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util import Retry
# suppress warnings from verify=False
from requests.packages.urllib3.exceptions import SecurityWarning
requests.packages.urllib3.disable_warnings(SecurityWarning)
# This is required if we want to support old versions of py2
# from requests.packages.urllib3.exceptions import SNIMissingWarning
# requests.packages.urllib3.disable_warnings(SNIMissingWarning)


requests_timeout = (121, 241)


class ApplianceRest(ApplianceConnection):

    def __init__(self, *args, **kwargs):
        """
        :param system: Appliance to connect to (ip or dns name)
        :param connect_kwargs: Dictionary of connect_kwargs to send to connect; ex. {'name': 'ex', 'password': 'ex', 'vendorkey': 'ex'}
        :param call_timeout: Maximum time to spend attempting an individual call
        """
        super(ApplianceRest, self).__init__(*args, **kwargs)

        self.connect_kwargs.setdefault('vendorkey', 'novend')

        # Set in method 'connect'
        self.s = self.sid = None

    def connect(self):
        """Connect and get a sessionid from the appliance."""
        # Ensure we have everything we need to connect before attempting
        for input_ in ['name', 'password', 'vendorkey']:
            if input_ not in self.connect_kwargs:
                raise ValueError("Missing parameter {}, cannot login without it.".format(input_))

        self.s = requests.Session()
        adapter = HTTPAdapter(max_retries=Retry(connect=5))
        self.s.mount("https://" + self.system, adapter)

        self.logger.info("Logging in as user '{}'.".format(self.connect_kwargs.get('name', '<no name found>')))

        result = self.s.post("https://" + self.system + "/actifio/api/login", verify=False, params=self.connect_kwargs,
                             timeout=requests_timeout)
        result.raise_for_status()
        result_j = result.json()
        if 'errorcode' in result_j:
            raise ValueError("Failed to connect: {}".format(result_j))

        self.sid = result_j['sessionid']
        self.logger.info('Sessionid {} acquired.'.format(self.sid))

        self.s.keep_alive = False

        # Sign out after execution
        atexit.register(self.disconnect, sid=self.sid)

    def disconnect(self, sid=None):
        """Logout of an actifio rest session."""
        if sid is None:
            sid = self.sid

        # Only try to disconnect if we have a sid. It takes a long time to retry connection to a non-existent machine.
        if sid:
            self.logger.debug("Logging out of session {}".format(sid))
            url = ("https://{}/actifio/api/logout?sessionid={}".format(self.system, sid))
            try:
                self.s.post(url, verify=False, timeout=requests_timeout)
            except requests.ConnectionError:
                # Don't raise connection error. It's safe to let it timeout.
                self.logger.info("Unable to logout of session, it may have already expired.")
            self.s.close()

        # set sid to None for the case where it was set as self.sid
        self.sid = None if self.sid is sid else self.sid

    def _auto_connect(self):
        if not self.sid:
            self.connect()

    def call(self, act_cmd):
        super(ApplianceRest, self).call(act_cmd)

        r = self._protect_sid(**act_cmd.input.rest_kwargs)
        try:
            r.raise_for_status()
        except requests.HTTPError as e:  # NOQA: keep this object for debugging
            self.logger.debug("Bad HTTP Status {}.\nResponse: {}\nUrl {}".format(r.status_code, r.json(), r.url))
            # Let the user handle errors

        act_cmd.output.result = r.json()

    def _protect_sid(self, method, url, params, verify=False, **kwargs):
        """Resend the operation if it looks like the sessionid has been dropped (default times out at 30 minutes)."""
        try:
            r = self.s.request(method, url, params=params, verify=verify, **kwargs)
            self.logger.info('Request url: {}'.format(r.url))
            self.logger.debug(r.content)
            r.raise_for_status()
        except requests.HTTPError as e:
            # errorcode 10020 is User is not logged in
            # {'errorcode': 10020, 'errormessage': 'User is not logged in'}
            try:
                errorcode = r.json()['errorcode']
            except KeyError:
                self.logger.debug(r.json())
                self.logger.exception("Status code was bad, but no errorcode could be found!")
                raise
            if e.response.status_code == 500 and errorcode == 10020:
                self.logger.exception('Sessionid was invalid, re-authenticating and sending again.')
                self.logger.debug(r.json())
                self.logger.debug("Failed sessionid is '{}'".format(self.sid))
                self.connect()
                params['sessionid'] = self.sid
                self.logger.debug("New sessionid is '{}'".format(self.sid))
                r = self.s.request(method, url, params=params, verify=verify, **kwargs)

            # Don't re-raise let the user handle all other errors

        return r

    def ui_call(self, method, url_suffix, params=None, data=None, **kwargs):
        """
        Used to send Actifio desktop rest calls.

        :param method: type of rest call to make. ie. GET, POST
        :param input_dictionary: python object to be converted to json
        :param url_suffix: What follows actifio in the UI call. i.e. https://<some_hostname>/actifio/<url_suffix here>
        :return: ActResponse object of request
        """
        if not self.sid:
            self.connect()

        if params is None:
            params = {}
        url = "https://{}/actifio/{}".format(self.system, url_suffix)
        params['sessionid'] = self.sid
        r = self._protect_sid(method, url, params=params, data=data, timeout=requests_timeout, **kwargs)
        r.raise_for_status()
        # strip the unparseable parts of the response that the UI framework needs and convert to dictionary
        answer = json.loads(r.text[1:-1])
        self.logger.debug(answer)
        if answer.get('status') != 'ok':
            ar = ActResponse(answer)
            ar.raise_for_error()
        return answer
