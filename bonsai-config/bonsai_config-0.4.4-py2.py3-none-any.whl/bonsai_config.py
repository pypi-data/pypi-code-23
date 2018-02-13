"""
This file contains ip address and port related constants.
"""

import os
from six.moves.configparser import ConfigParser


CONFIG_FILE = os.path.expanduser('~/.bonsai')

_DEFAULT_URL = 'https://api.bons.ai'

# Keys used in the config file.
_DEFAULT_SECTION = 'DEFAULT'
_USERNAME = 'Username'
_ACCESS_KEY = 'AccessKey'
_PROFILE = 'Profile'
_URL = 'Url'

# Deprecated keys
_PORT = 'Port'
_HOST = 'Host'
_USE_SSL = 'UseSsl'


class BonsaiConfig():
    def __init__(self, section=None):
        self.config = ConfigParser(defaults={
            _USERNAME: None,
            _ACCESS_KEY: None
        })
        self.config.read(CONFIG_FILE)
        if section:
            profile = section
        elif self.config.has_option(_DEFAULT_SECTION, _PROFILE):
            profile = self.config.get(_DEFAULT_SECTION, _PROFILE)
        else:
            profile = _DEFAULT_SECTION

        self._set_profile(profile)

        # Support existing port + host + ssl config by setting the
        # default here instead of in the ConfigParser constructor
        url = self.brain_api_url()
        if url is None:
            self.config.set(self.profile, _URL, _DEFAULT_URL)

    def _write(self):
        with open(CONFIG_FILE, 'w') as f:
            self.config.write(f)

    def _get(self, key):
        if self.config.has_option(self.profile, key):
            return self.config.get(self.profile, key)
        return None

    def update_access_key_and_username(self, access_key, username):
        self.config.set(self.profile, _ACCESS_KEY, access_key)
        self.config.set(self.profile, _USERNAME, username)
        self._write()

    def _host(self):
        return self._get(_HOST)

    def _port(self):
        return self._get(_PORT)

    def username(self):
        return self._get(_USERNAME)

    def access_key(self):
        return self._get(_ACCESS_KEY)

    def _use_ssl(self):
        use_ssl = self._get(_USE_SSL)
        return use_ssl is not None and use_ssl.lower() == 'true'

    def _can_omit_port(self, port):
        """Function for determining if we can omit the port when formatting
        urls. We can omit the port when we're using the default port, which
        is 443 for ssl connections and 80 for non ssl connections.
        """
        if self._use_ssl():
            return port == "443"
        else:
            return port == "80"

    def _format_url(self, scheme, host, port):
        if self._can_omit_port(port):
            return "{}://{}".format(scheme, host)
        else:
            return "{}://{}:{}".format(scheme, host, port)

    def brain_api_url(self):
        """ Returns a url for the BRAIN api. """
        url = self._get(_URL)
        if url:
            return url

        return self._piecewise_url()

    def _piecewise_url(self):
        """ Returns the Brain url built from host, port and use_ssl. """

        if (self._host() is None or self._port() is None):
            return None

        scheme = "https" if self._use_ssl() else "http"
        return self._format_url(scheme, self._host(), self._port())

    def brain_websocket_url(self):
        """ Returns a url for a BRAIN websocket. """
        api_url = self.brain_api_url()
        return api_url.replace('http', 'ws', 1)

    def _make_section(self, key):
        if (not self.config.has_section(key) and
                key != _DEFAULT_SECTION):
            self.config.add_section(key)

    def _set_profile(self, section):
        self._make_section(section)
        self.profile = section
        if section == _DEFAULT_SECTION:
            self.config.remove_option(_DEFAULT_SECTION, _PROFILE)
        else:
            self.config.set(_DEFAULT_SECTION, _PROFILE, str(section))

    def update(self, **kwargs):
        """Updates the configuration with the Key/value pairs in kwargs."""
        if not kwargs:
            return
        for key, value in kwargs.items():
            if key.lower() == _PROFILE.lower():
                self._set_profile(value)
            else:
                self.config.set(self.profile, key, str(value))
        self._write()

    def check_section_exists(self, section):
        """Checks the configuration to see if section exists."""
        if section == _DEFAULT_SECTION:
            return True
        return self.config.has_section(section)
