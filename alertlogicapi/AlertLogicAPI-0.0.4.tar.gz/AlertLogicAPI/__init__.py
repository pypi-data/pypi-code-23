# Copyright 2018 Frederick Reimer.
#
# This file is part of the AlertLogicAPI Python Package.
#
# AlertLogicAPI  Python Package is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# AlertLogicAPI  Python Package is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# AlertLogicAPI Python Package.  If not, see <http://www.gnu.org/licenses/>.

__version__ = '0.0.4'
__author__ = 'Fred Reimer <freimer@freimer.org>'
__copyright__ = "Frederick Reimer"
__license__ = "GPL v3"

import requests.auth
import AlertLogicAPI.Exceptions


class Client(object):

    def __init__(self, customer_id, apikey, data_center: str = 'US',verify_path=None):
        self.customer_id = customer_id
        self.auth = requests.auth.HTTPBasicAuth(apikey, '')
        if data_center not in ['US', 'Ashburn', 'UK']:
            raise AlertLogicAPI.Exceptions.ArgumentError(
                'AlertLogic.Client(): data_center must be one of [US, Ashburn, UK]')
        self.base_url = {
            'US': 'https://publicapi.alertlogic.net',
            'Ashburn': 'https://publicapi.alertlogic.com',
            'UK': 'https://publicapi.alertlogic.co.uk',
        }[data_center]
        self.verify_path = verify_path

    def get_protected_host(self, protectedhost_id: str, cid: str = None) -> dict:
        """Retrieve data for the specified protected host.

        :param str protectedhost_id: Specifies the ID of the protected host to retrieve.
        :param str cid: Specifies the ID of the customer account, which must be a child customer of your parent account.
        :return: dict of protected host data per API Documentation
        :rtype: dict
        :raises: AlertLogic.Exceptions.APIError
        """
        url = '{}/api/tm/v1/{}/protectedhosts/{}'.format(
            self.base_url,
            self.customer_id,
            protectedhost_id
        )
        result = requests.get(url, auth=self.auth, verify=self.verify_path)
        if result.status_code != 200:
            raise AlertLogicAPI.Exceptions.APIError(
                'AlertLogic.Client.get_protected_host(): API result: {}'.format(result))
        return result.json()['protectedhost']

    def get_protected_hosts(self, cid: str = None,
                            id: str = None,
                            local_hostname: str = None,
                            name: str = None,
                            search: str = None,
                            status: str = None,
                            os_type: str = None,
                            tags: str = None,
                            type: str = None,
                            limit: int = None,
                            offset: int = None) -> list:
        """Retrieve a list of protected hosts matching specified criteria.

        :param str id: Specifies the ID of the protected host.
        :param str local_hostname: Specifies the local hostname.
        :param str name: Specifies the descriptive name of the protected host.
        :param str search: Specifies any value to include in the search results. This filter queries all fields of a protected host.
        :param str os_type: Specifies the type of operating system. One of [windows, linux]
        :param str cid: Specifies the ID of the customer account, which must be a child customer of your parent account.
        :param str status: Specifies the status messages. One of [new, ok, warning, error, offline]
        :param str tags: Specifies customer-defined tags.
        :param str type: Specifies the type of protected host. One of [host, role]
        :param int limit: Specifies the maximum number of objects to return.
        :param int offset: Specifies the offset of the first object to return. To use the offset parameter, you must
            also specify the limit parameter.
        :return list: list of the Protected Hosts per API Documentation
        """
        url = '{}/api/tm/v1/{}/protectedhosts'.format(
            self.base_url,
            self.customer_id
        )
        # Input validation
        if status is not None and status not in ['new', 'ok', 'warning', 'error', 'offline']:
            raise AlertLogicAPI.Exceptions.ArgumentError(
                'AlertLogicAPI.Client.get_protected_hosts(): Invalid status argument, must be'
                'one of [new, ok, warning, error, offline]')
        if os_type is not None and os_type not in ['windows', 'linux']:
            raise AlertLogicAPI.Exceptions.ArgumentError(
                'AlertLogicAPI.Client.get_protected_hosts(): Invalid os_type argument, must be'
                'one of [windows, linux]')
        if type is not None and type not in ['host', 'role']:
            raise AlertLogicAPI.Exceptions.ArgumentError(
                'AlertLogicAPI.Client.get_protected_hosts(): Invalid type argument, must be'
                'one of [host, role]')
        # Build parameters
        params = {
            'id': id,
            'metadata.local_hostname': local_hostname,
            'name': name,
            'search': search,
            'status.status': status,
            'metadata.os_type': os_type,
            'tags': tags,
            'type': type,
            'limit': limit,
            'offset': offset
        }
        result = requests.get(url, auth=self.auth, params=params, verify=self.verify_path)
        if result.status_code != 200:
            raise AlertLogicAPI.Exceptions.APIError(
                'AlertLogicAPI.Client.get_protected_hosts(): API result: {}'.format(result)
            )
        # Convert JSON to struct and "unwrap" the protected hosts so they are just a list of dicts
        return [p['protectedhost'] for p in result.json()['protectedhosts']]

    def delete_protected_host(self, protected_host_id: str) -> bool:
        url = '{}/api/tm/v1/{}/protectedhosts/{}'.format(
            self.base_url,
            self.customer_id,
            protected_host_id
        )
        result = requests.delete(url, auth=self.auth, verify=self.verify_path)
        if result.status_code == 404:
            return True
        return False
