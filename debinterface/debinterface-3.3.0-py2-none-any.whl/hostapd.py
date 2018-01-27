# -*- coding: utf-8 -*-
from __future__ import print_function, with_statement, absolute_import
import os
import shutil

from . import toolutils


class Hostapd(object):
    """ basic hostapd conf file handling """

    def __init__(self, path, backup_path=None):
        self._config = {}
        self._path = path
        if not backup_path:
            self.backup_path = path + ".bak"
        else:
            self.backup_path = backup_path

    @property
    def config(self):
        return self._config

    def set(self, key, value):
        if isinstance(value, str):
            self._config[str(key).strip()] = value.strip()
        else:
            self._config[str(key).strip()] = value

    def validate(self):
        """Not sure which ones are really necessary for everyone,
            here are the ones I require.
            I created 4 groups of keys : basic must always be there,
            wireless if you want to be an AP, auth if you want to add
            some security, bridge for, well, bridging
            Not foul proof !

            Returns:
                bool: True if everything went ok

            Raises:
                KeyError : missing key
                ValueError : invalid data
        """

        basic = ['interface', 'driver']
        bridge = ['bridge']
        wireless = ['ssid', 'channel', 'hw_mode']
        auth = ['wpa', 'wpa_passphrase', 'wpa_key_mgmt']

        for k in basic:
            if self._config[k] is None:
                raise ValueError("Missing required {0} option".format(k))

        if 'bridge' in self._config:
            for k in bridge:
                if self._config[k] is None:
                    raise ValueError("Missing required {0} option "
                                     "for bridge".format(k))

        if 'ssid' in self._config:
            for k in wireless:
                if self._config[k] is None:
                    raise ValueError("Missing required {0} option for "
                                     "wireless".format(k))
            # will raise value error if not int
            self._config['channel'] = int(self._config['channel'])

        if 'wpa' in self._config:
            self._config['wpa'] = int(self._config['wpa'])
            if not self._config['wpa'] in [1, 2, 3]:
                raise ValueError("Wpa option is not valid")
            for k in auth:
                if self._config[k] is None:
                    raise ValueError("Missing required {0} option for "
                                     "wireless security".format(k))
            if self._config['wpa'] in [1, 3]:
                if not self._config['wpa_pairwise']:
                    raise ValueError("Missing required option for "
                                     "wireless security : wpa_pairwise")
            if self._config['wpa'] in [2, 3]:
                if not self._config['rsn_pairwise']:
                    raise ValueError("Missing required option for "
                                     "wireless security rsn_pairwise")
        return True

    def set_defaults(self):
        """ ssid and wpa_passphrase defaults to
        cashpad-FTED and cashpad-GH67
        """
        self._config = {
            'interface': 'wlan0',
            'driver': 'nl80211',

            # logs
            'logger_syslog': -1,
            'logger_syslog_level': 2,
            'logger_stdout': -1,
            'logger_stdout_level': 2,

            # debug
            'debug': 4,

            # wifi
            'hw_mode': 'g',

            # security goodies
            'macaddr_acl': 0,
            'eapol_key_index_workaround': 0,
            'eap_server': 0,
            'eapol_version': 1,

            # wifi auth
            'channel': 4,
            'ssid': 'cashpad-FTED',
            'wpa_passphrase': 'cashpad-GH67',
            'auth_algs': 3,
            'wpa': 3,  # WPA + WPA2. set to 2 to restrict to WPA2
            'wpa_key_mgmt': 'WPA-PSK',
            'wpa_pairwise': 'TKIP',
            # some windows clients may have issues with this one:
            'rsn_pairwise': 'CCMP'
        }

    def read(self, path=None):
        if path is None:
            path = self._path

        self._config = {}

        with open(path, "r") as hostapd:
            for line in hostapd:
                if line.startswith('#') is True or line == "\n" or line == "":
                    pass
                else:
                    param, value = line.replace("\n", "").split("=")
                    if param and value:
                        self.set(param.strip(), value.strip())

    def write(self, path=None):
        self.validate()

        if path is None:
            path = self._path

        self.backup()

        with toolutils.atomic_write(path) as hostapd:
            for k, v in self._config.items():
                key = str(k).strip()
                value = str(v).strip()
                hostapd.write("{0}={1}\n".format(key, value))

    @staticmethod
    def controlService(action):
        """ return True/False, command output """

        if action not in ["start", "stop", "restart"]:
            return False, "Invalid action"
        return toolutils.safe_subprocess(["/etc/init.d/hostapd", action])

    def backup(self):
        """ return True/False, command output """

        if self.backup_path:
            shutil.copy(self._path, self.backup_path)

    def restore(self):
        """ return True/False, command output """

        if self.backup_path:
            shutil.copy(self.backup_path, self._path)

    def delete(self):
        """ return True/False, command output """

        if self.backup_path:
            os.remove(self._path)
