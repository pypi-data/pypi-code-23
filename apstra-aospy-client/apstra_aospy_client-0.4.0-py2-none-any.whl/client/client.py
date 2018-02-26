# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

import six
import os
import socket
import json
from pkg_resources import parse_version, get_distribution
from copy import copy
import requests

from .utils import probe

if six.PY2:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse


__all__ = ['Client']


class Client(object):
    """
    The class is used to create a client connection with the AOS-server REST API.
    """

    ENV = {
        'server':       'AOS_SERVER',
        'port':         'AOS_SERVER_PORT',
        'token':        'AOS_SESSION_TOKEN',
        'username':     'AOS_USER',
        'passowrd':     'AOS_PASSWORD',

        # add a variable that allows the caller to 'force' the AOS version
        # value, rather than use what is provided by the AOS server.  This
        # is necessary for pre-release build usage.

        'forced_version': 'AOS_FORCED_VERSION'
    }

    DEFAULTS = {
        'proto': 'https',
        'username': 'admin',
        'passowrd': 'admin',
        'reference_design': 'two_stage_l3clos'
    }

    def __init__(self, server=None, **kwargs):
        """
        Creates a new client session with the AOS server.  The client will attempt
        to connect unless the option login=False is provided.
        """

        self._host = None
        self._port = None
        self._url = None
        self._version_info = None

        # create a `requests` session object to the client, disable SSL
        # verification.  Finally associate the aospy client object to the
        # requests API so that it can be accessed by other elements attached
        # and passed around.

        self.api = requests.Session()
        self.api.verify = False
        self.api.aos_client = self

        # using the caller provided passed parameters and Environment
        # variables, compose the complete set of config params.

        self.config = copy(kwargs)
        self.config['server'] = server
        self._init_config()

        # finally, attemp to login to the AOS-server, unless the caller
        # explicitly set the option login=False.

        if self.config.get('login', True):
            self.login()

    # #########################################################################
    # ###
    # ###                        PROPERTIES
    # ###
    # #########################################################################

    @property
    def url(self):
        """
        returns <proto>://<server>
        does not include the /api endpoint part, use :meth:`path` for this
        """
        if not self._url:
            raise RuntimeError(
                "not logged into server: config=%s" %
                json.dumps(self.config, indent=3))

        return self._url

    @property
    def path(self):
        """ returns the url with the API endpoint path """
        return self.url + "/api"

    @property
    def token(self):
        """ returns the active session token """
        return self.api.headers['AUTHTOKEN']

    @property
    def server(self):
        """ returns the server hostname/ipaddr value"""
        return self._host

    @property
    def port(self):
        """ returns the HTTP/s port number """
        return self._port

    @property
    def version(self):
        """ returns only the build version string """
        return self._version_info['version']

    @property
    def version_info(self):
        """ returns all version related information as dict """
        return self._version_info

    # #########################################################################
    # ###
    # ###                        PUBLIC METHODS
    # ###
    # #########################################################################

    def verify_token(self):
        """
        Used to verify if the active session token is valid.

        Returns
        -------
        (bool) True if token is valid, False otherwise
        """
        return self.api.get(self.path).ok

    def fetch_version_info(self):
        """
        Used to fetch the current AOS-server API and build version information
        and build the :attr:`version` and :attr:`version_info` properties.

        Returns
        -------
        (dict) the :attr:`version_info` property value
        """

        # store the REST API version

        resp = self.api.get("%s/api/versions/api" % self.url)
        if not resp.ok:
            raise RuntimeError(
                'unable to retrieve API version info', resp)

        self._version_info = dict()
        api_info = resp.json()
        self._version_info['api_version'] = api_info['version']
        self._version_info['api_version_parsed'] = parse_version(api_info['version'])

        # store the build version

        resp = self.api.get(self.path + "/versions/build")
        if not resp.ok:
            raise RuntimeError('unable to get AOS build-version', resp)

        build_info = resp.json()

        # add support for environment variable that allow the user to
        # for a specific AOS version string.  This is needed when using pre-releaded
        # builds and we need to ensure the client library is acting according to
        # the ~eventual~ release string.  Usage example:
        #      $ export AOS_FORCED_VERSION=2.0.0-10

        aos_version = os.getenv('AOS_FORCED_VERSION') or build_info['version']

        version, _, number = aos_version.partition('-')

        self._version_info['version'] = version
        self._version_info['build'] = number
        self._version_info['timestamp'] = build_info['build_datetime']
        self._version_info['parsed'] = parse_version(version)

        # store the client library version

        version = get_distribution('apstra-aospy-client').version
        self._version_info['client_version'] = version

        return self._version_info

    def login(self):
        """
        This method is used to explicity (re)login to the AOS server.  This method is
        generally only used if the Client was originally created with the login=False
        option.
        """
        if not self.server:
            raise RuntimeError("no AOS server information provided")

        do_probe = self.config.get('probe', True)
        if do_probe and not probe(self.server, self.port):
            raise RuntimeError(
                'AOS server "%s:%s" not reachable' %
                (self.server, self.port))

        if 'token' not in self.config:
            cfg = self.config
            user, password = cfg.get('username'), cfg.get('password')
            if not user and password:
                raise RuntimeError('missing login credentials')

            rsp = self.api.post("%s/user/login" % self.path,
                                json=dict(username=user, password=password))

            if not rsp.ok:
                raise RuntimeError('unable to authenticate')

            self.api.headers['AUTHTOKEN'] = rsp.json()['token']
        else:
            self.api.headers['AUTHTOKEN'] = self.config['token']
            if not self.verify_token():
                raise RuntimeError('invalid login token')

        self.fetch_version_info()

    def fetch_apispec(self, reference_design=None):
        """
        This method is used to retrieve the AOS Swagger specs
        for both the platform and the reference_design.

        Parameters
        ----------
        reference_design : str
            The reference-design name.  If not given, will default
            to the two_stage_l3clos value.

        Returns
        -------
        dict
            The combined platform/reference-design Swagger-spec dictionary
        """

        # if a reference design is given, then load that spec, otherwise
        # load the AOS platform spec

        docs_url = self.path + "/docs"

        # get the platform swagger spec

        plat_spec = self.api.get(docs_url).json()

        # get the reference design swagger spec.  If none is
        # provided by the caller, then use the DEFAULTS value.

        reference_design = (reference_design or
                            self.DEFAULTS['reference_design'])

        refd_spec = self.api.get(
            docs_url + "/reference_designs/%s" % reference_design).json()

        # --------------------------------------------------------
        # need to account for issues in the AOS 2.1.0 swagger spec
        # --------------------------------------------------------

        api_ver = self.version_info['api_version_parsed']
        parsed_version = type(api_ver)

        if parsed_version('2.1') <= api_ver <= parsed_version('2.2'):
            from . import apispec
            apispec.patch_aos_2_1_reference_design(refd_spec)
            apispec.patch_aos_2_1_platform(plat_spec)

        # merge the platform and reference design paths & definitions
        # so that the caller has a combined spec

        for key in ['paths', 'definitions']:
            refd_spec[key].update(plat_spec[key])

        return refd_spec

    # #########################################################################
    # ###
    # ###                        PRIVATE METHODS
    # ###
    # #########################################################################

    def _init_config(self):
        """
        (called from __init__)
        Used to take the provided client parameters along with the ENV
        and defaults to create the consolidated dictionary of client
        configuration parameters; later used to create the connection to the
        AOS-server
        """

        # if the 'server' value is not explicity configured then take it
        # from the user ENV

        if not self.config['server']:
            self.config['server'] = os.getenv(Client.ENV['server'])

        if Client.ENV['token'] in os.environ:
            self.config['token'] = os.getenv(Client.ENV['token'])

        if 'username' not in self.config:
            self.config['username'] = (
                os.getenv(Client.ENV['username']) or
                Client.DEFAULTS['username'])

        if 'password' not in self.config:
            self.config['password'] = (
                os.getenv(Client.ENV['passowrd']) or
                Client.DEFAULTS['passowrd'])

        self._init_url()

    def _init_url(self):
        """
        (called from _init_config)
        Used to take the provided client parameters and formulate the
        proper API URL that will be used to communicate with the AOS-server
        """

        server = self.config['server']
        if not server:
            raise RuntimeError("AOS server value not provided")

        # see if the caller provided the server in a URL form.
        # if not in a URL form, then presume that the server value
        # is simply the host/ipaddr value, used the default PROTO
        # and probe the target to ensure that it is valid

        res = urlparse(server)
        if res.scheme:
            server, proto = res.hostname, res.scheme
            cfg_port = res.port
            proto_port = socket.getservbyname(res.scheme)
        else:
            proto = self.DEFAULTS['proto']
            proto_port = socket.getservbyname(proto)
            cfg_port = self.config.get('port')

        try_port = cfg_port or proto_port

        if proto == 'https' and self.api.verify is False:
            from requests.packages import urllib3
            urllib3.disable_warnings()

        self._host = server
        self._port = try_port
        self._url = "{proto}://{server}{opt_port}".format(
            proto=proto, server=server,
            opt_port=(':%s' % cfg_port if cfg_port else ''))

    def __repr__(self):
        return json.dumps({
            'server': self.server,
            'version': self.version,
            'build': self.version_info['build']
        }, indent=3)
