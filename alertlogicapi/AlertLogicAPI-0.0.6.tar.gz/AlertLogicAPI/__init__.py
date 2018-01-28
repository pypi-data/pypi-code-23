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

__version__ = '0.0.6'
__author__ = 'Fred Reimer <freimer@freimer.org>'
__copyright__ = "Frederick Reimer"
__license__ = "GPL v3"

import requests.auth
import Crypto.PublicKey.RSA
import AlertLogicAPI.Exceptions


class Client(object):

    def __init__(self, customer_id, apikey, data_center: str = 'US', verify_path=None):
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
        if cid is None:
            url = '{}/api/tm/v1//protectedhosts/{}'.format(
                self.base_url,
                protectedhost_id
            )
        else:
            url = '{}/api/tm/v1/{}/protectedhosts/{}'.format(
                self.base_url,
                cid,
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
        :param str search: Specifies any value to include in the search results. This filter queries all fields of a
            protected host.
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
        if cid is None:
            url = '{}/api/tm/v1//protectedhosts'.format(
                self.base_url
            )
        else:
            url = '{}/api/tm/v1/{}/protectedhosts'.format(
                self.base_url,
                cid
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
        if offset is not None and limit is None:
            raise AlertLogicAPI.Exceptions.ArgumentError(
                'AlertLogicAPI.Client.get_protected_hosts(): must specify limit if specifying offset')
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

    def delete_protected_host(self, protectedhost_id: str, cid: str = None) -> bool:
        """Delete the specified protected host.

        :param str protectedhost_id: Specifies the ID of the protected host resource to delete.
        :param str cid: Specifies the ID of the customer account, which must be a child customer of your parent account.
        :return bool: True if deleted, False otherwise
        """
        if cid is None:
            url = '{}/api/tm/v1//protectedhosts/{}'.format(
                self.base_url,
                protectedhost_id
            )
        else:
            url = '{}/api/tm/v1/{}/protectedhosts/{}'.format(
                self.base_url,
                cid,
                protectedhost_id
            )
        result = requests.delete(url, auth=self.auth, verify=self.verify_path)
        if result.status_code == 404:
            return True
        return False

    def update_protected_host(self, protectedhost_id: str, cid: str = None,
                              appliance_policy_id: str = None,
                              config_policy_id: str = None,
                              name: str = None,
                              tags: list = None) -> dict:
        """Update only given fields of the specified protected host, ignoring any missing fields.

        :param str protectedhost_id: Specifies the ID of the protected host to modify.
        :param str cid: Specifies the ID of the customer account, which must be a child customer of your parent account.
        :param str appliance_policy_id: Specifies the appliance policy ID.
        :param str config_policy_id: Specifies the configuration policy ID.
        :param str name: Specifies the new descriptive name for the appliance. (this is from the Alert Logic docs, not
            sure if this really means descriptive name for the protected host...)
        :param list tags: List of tags (str).
        :return dict: Returns dict of protected host data.
        """
        if cid is None:
            url = '{}/api/tm/v1//protectedhosts/{}'.format(
                self.base_url,
                protectedhost_id
            )
        else:
            url = '{}/api/tm/v1/{}/protectedhosts/{}'.format(
                self.base_url,
                cid,
                protectedhost_id
            )
        # Data validation
        data = {'protectedhost': {}}
        num_updates = 0
        if appliance_policy_id is not None:
            data['protectedhost']['apppliance']['policy']['id'] = appliance_policy_id
            num_updates += 1
        if config_policy_id is not None:
            data['protectedhost']['config']['policy']['id'] = config_policy_id
            num_updates += 1
        if name is not None:
            data['protectedhost']['name'] = name
            num_updates += 1
        if tags is not None:
            if isinstance(tags, list) is False:
                raise AlertLogicAPI.Exceptions.ArgumentError(
                    'AlertLogicAPI.Client.update_protected_host(): tags must be a list')
            data['protectedhost']['tags'] = []
            for tag in tags:
                data['protectedhost']['tags'].append({'name': tag})
            num_updates += 1
        if num_updates == 0:
            raise AlertLogicAPI.Exceptions.ArgumentError(
                'AlertLogicAPI.Client.update_protected_host(): you must specify something to update')
        # Perform the update
        result = requests.post(url, auth=self.auth, json=data, verify=self.verify_path)
        if result.status_code != 200:
            raise AlertLogicAPI.Exceptions.APIError(
                'AlertLogic.Client.update_protected_host(): API result: {}'.format(result))
        return result.json()['protectedhost']

    def get_keypairs(self, cid: str = None,
                     host: str = None,
                     id: str = None,
                     name: str = None,
                     port: str = None,
                     type: str = 'pem',
                     search: str = None,
                     limit: str = None,
                     offset: str = None
                     ) -> list:
        """Retrieve a list of keypairs matching specified criteria.

        :param str cid: Specifies the ID of the customer account, which must be a child customer of your parent account.
        :param str host: Specifies the IP address for the keypair host. For example, 10.0.0.1.
        :param str name: Specifies the descriptive name for the keypair.
        :param str id: Specifies the keypair ID.
        :param str port: Specifies the keypair port. Valid values: 1 - 65535
        :param str type: Specifies the keypair type. Valid value: pem
        :param str search: Specifies any value to include in the search results. This filter queries all fields of a
            keypair.
        :param int limit: Specifies the maximum number of objects to return.
        :param int offset: Specifies the offset of the first object to return. To use the offset parameter, you must
            also specify the limit parameter.
        :return list: list of keypairs
        """
        if cid is None:
            url = '{}/api/tm/v1//keypairs'.format(
                self.base_url
            )
        else:
            url = '{}/api/tm/v1/{}/keypairs'.format(
                self.base_url,
                cid
            )
        # Input validation
        if port is not None:
            try:
                i = int(port)
            except ValueError:
                raise AlertLogicAPI.Exceptions.ArgumentError(
                    'AlertLogicAPI.Client.get_keypairs(): Invalid port argument, must be integer')
            if i < 1 or i > 65535:
                raise AlertLogicAPI.Exceptions.ArgumentError(
                    'AlertLogicAPI.Client.get_keypairs(): Invalid port argument, must be 1 - 65535')
        if type is not None and type not in ['pem']:
            raise AlertLogicAPI.Exceptions.ArgumentError(
                'AlertLogicAPI.Client.get_keypairs(): Invalid type argument, must be one of [pem]')
        if offset is not None and limit is None:
            raise AlertLogicAPI.Exceptions.ArgumentError(
                'AlertLogicAPI.Client.get_keypairs(): must specify limit if specifying offset')
        # Build parameters
        params = {
            'host': host,
            'id': id,
            'name': name,
            'port': port,
            'type': type,
            'search': search,
            'limit': limit,
            'offset': offset
        }
        result = requests.get(url, auth=self.auth, params=params, verify=self.verify_path)
        if result.status_code != 200:
            raise AlertLogicAPI.Exceptions.APIError(
                'AlertLogic.Client.get_keypairs(): API result: {}'.format(result))
        return result.json()['keypairs']

    def create_keypair(self, cid: str = None,
                       name: str = None,
                       host: str = None,
                       port: str = '443',
                       type: str = 'pem',
                       certificate: str = None,
                       certificate_path: str = None,
                       private_key: str = None,
                       private_key_path: str = None,
                       private_key_password: str = None
                       ) -> dict:
        """Creat a keypair.

        This can accept a variety of methods for specifying the certificate and private key.  If the arguments ending
        with _path are used, they files specified are read and the contents used.  Otherwise, the arguments without
        the _path must be specified.  Decrypting the private key is performed if private_key_password is provided.

        :param str cid: Specifies the ID of the customer account, which must be a child customer of your parent account.
        :param str name: Specifies the descriptive name for the keypair.
        :param str host: Specifies the IP address for the keypair host. For example, 10.0.0.1.
        :param str port: Specifies the keypair port. Valid values: 1 - 65535
        :param str type: Specifies the keypair type. Valid value: pem
        :param str certificate: Specifies certificate content, which must include the header and footer notes
        :param str certificate_path: Specifies path to certificate file
        :param str private_key: Specifies the private key in RSA format, which must include the header and footer notes
        :param str private_key_path: Specifies path to private key file
        :param str private_key_password: If set, specifies the password to decrypt the private key
        :return dict: created keypair info
        """
        if cid is None:
            url = '{}/api/tm/v1//keypairs'.format(
                self.base_url
            )
        else:
            url = '{}/api/tm/v1/{}/keypairs'.format(
                self.base_url,
                cid
            )
        # Input validation
        if host is None:
            raise AlertLogicAPI.Exceptions.ArgumentError(
                'AlertLogicAPI.Client.create_keypair(): host argument is required')
        if port is not None:
            try:
                i = int(port)
            except ValueError:
                raise AlertLogicAPI.Exceptions.ArgumentError(
                    'AlertLogicAPI.Client.create_keypair(): Invalid port argument, must be integer')
            if i < 1 or i > 65535:
                raise AlertLogicAPI.Exceptions.ArgumentError(
                    'AlertLogicAPI.Client.create_keypair(): Invalid port argument, must be 1 - 65535')
        if type is not None and type not in ['pem']:
            raise AlertLogicAPI.Exceptions.ArgumentError(
                'AlertLogicAPI.Client.create_keypair(): Invalid type argument, must be one of [pem]')
        if certificate_path is not None:
            try:
                certificate = open(certificate_path).read()
            except IOError:
                raise AlertLogicAPI.Exceptions.ArgumentError(
                    'AlertLogicAPI.Client.create_keypair(): certificate_path file "{}" unreadable'.format(
                        certificate_path))
        if certificate is None:
            raise AlertLogicAPI.Exceptions.ArgumentError(
                'AlertLogicAPI.Client.create_keypair(): certificate or certificate_path is required')
        if private_key_path is not None:
            try:
                private_key = open(private_key_path).read()
            except IOError:
                raise AlertLogicAPI.Exceptions.ArgumentError(
                    'AlertLogicAPI.Client.create_keypair(): private_key_path file "{}" unreadable'.format(
                        certificate_path))
        if private_key is None:
            raise AlertLogicAPI.Exceptions.ArgumentError(
                'AlertLogicAPI.Client.create_keypair(): private_key or private_key_path is required')
        if private_key_password is not None:
            try:
                rsakey = Crypto.PublicKey.RSA.importKey(private_key, passphrase=private_key_password)
            except (ValueError, IndexError, TypeError):
                raise AlertLogicAPI.Exceptions.ArgumentError(
                    'AlertLogicAPI.Client.create_keypair(): unable to decrypt private key')
            private_key = rsakey.exportKey().decode()
        # Build parameters
        data = {
            'keypair': {
                'host': host,
                'name': name,
                'port': port,
                'type': type,
                'certificate': certificate,
                'private_key': private_key
            }
        }
        result = requests.post(url, auth=self.auth, json=data, verify=self.verify_path)
        if result.status_code != 201:
            raise AlertLogicAPI.Exceptions.APIError(
                'AlertLogic.Client.create_keypair(): API result: {}:\n{}'.format(result, result.text))
        return result.json()['keypair']

    def delete_keypair(self, keypair_id: str, cid: str = None) -> bool:
        """Delete the specified keypair.

        :param str keypair_id: Specifies the ID of the keypair to delete.
        :param str cid: Specifies the ID of the customer account, which must be a child customer of your parent account.
        :return bool: True if deleted, False otherwise
        """
        if cid is None:
            url = '{}/api/tm/v1//keypairs/{}'.format(
                self.base_url,
                keypair_id
            )
        else:
            url = '{}/api/tm/v1/{}/keypairs/{}'.format(
                self.base_url,
                cid,
                keypair_id
            )
        result = requests.delete(url, auth=self.auth, verify=self.verify_path)
        if result.status_code == 404:
            return True
        return False

