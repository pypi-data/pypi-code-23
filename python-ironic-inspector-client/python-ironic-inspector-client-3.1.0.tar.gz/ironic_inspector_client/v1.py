# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Client for V1 API."""

from collections import OrderedDict
import logging
import time

import six

from ironic_inspector_client.common import http
from ironic_inspector_client.common.i18n import _


DEFAULT_API_VERSION = (1, 0)
"""Server API version used by default."""

MAX_API_VERSION = (1, 8)
"""Maximum API version this client was designed to work with.

This does not mean that other versions won't work at all - the server might
still support them.
"""

# using huge timeout by default, as precise timeout should be set in
# ironic-inspector settings
DEFAULT_RETRY_INTERVAL = 10
"""Default interval (in seconds) between retries when waiting for introspection
to finish."""
DEFAULT_MAX_RETRIES = 3600
"""Default number of retries when waiting for introspection to finish."""

LOG = logging.getLogger(__name__)


class WaitTimeoutError(Exception):
    """Timeout while waiting for nodes to finish introspection."""


class ClientV1(http.BaseClient):
    """Client for API v1.

    Create this object to use Python API, for example::

        import ironic_inspector_client
        client = ironic_inspector_client.ClientV1(session=keystone_session)

    This code creates a client with API version *1.0* and a given Keystone
    `session
    <https://docs.openstack.org/keystoneauth/latest/using-sessions.html>`_.
    The service URL is fetched from the service catalog in this case. Optional
    arguments ``service_type``, ``interface`` and ``region_name`` can be
    provided to modify how the URL is looked up.

    If the catalog lookup fails, the local host with port 5050 is tried.
    However, this behaviour is deprecated and should not be relied on.
    Also an explicit ``inspector_url`` can be passed to bypass service catalog.

    Optional ``api_version`` argument is a minimum API version that a server
    must support. It can be a tuple (MAJ, MIN), string "MAJ.MIN" or integer
    (only major, minimum supported minor version is assumed).

    :ivar rules: Reference to the introspection rules API.
        Instance of :py:class:`ironic_inspector_client.v1.RulesAPI`.
    """

    def __init__(self, **kwargs):
        """Create a client.

        See :py:class:`ironic_inspector_client.common.http.HttpClient` for the
        list of acceptable arguments.

        :param kwargs: arguments to pass to the BaseClient constructor.
                       api_version is set to DEFAULT_API_VERSION by default.
        """
        kwargs.setdefault('api_version', DEFAULT_API_VERSION)
        super(ClientV1, self).__init__(**kwargs)
        self.rules = RulesAPI(self.request)

    def introspect(self, uuid):
        """Start introspection for a node.

        :param uuid: node UUID or name
        :raises: :py:class:`.ClientError` on error reported from a server
        :raises: :py:class:`.VersionNotSupported` if requested api_version
            is not supported
        :raises: *requests* library exception on connection problems.
        """
        if not isinstance(uuid, six.string_types):
            raise TypeError(
                _("Expected string for uuid argument, got %r") % uuid)

        self.request('post', '/introspection/%s' % uuid)

    def reprocess(self, uuid):
        """Reprocess stored introspection data.

        :param uuid: node UUID or name.
        :raises: :py:class:`.ClientError` on error reported from a server
        :raises: :py:class:`.VersionNotSupported` if requested api_version
            is not supported
        :raises: *requests* library exception on connection problems.
        :raises: TypeError if uuid is not a string.
        """
        if not isinstance(uuid, six.string_types):
            raise TypeError(_("Expected string for uuid argument, got"
                              " %r instead") % uuid)

        return self.request('post',
                            '/introspection/%s/data/unprocessed' %
                            uuid)

    def list_statuses(self, marker=None, limit=None):
        """List introspection statuses.

        Supports pagination via the marker and limit params. The items are
        sorted by the server according to the `started_at` attribute, newer
        items first.

        :param marker: pagination maker, UUID or None
        :param limit: pagination limit, int or None
        :raises: :py:class:`.ClientError` on error reported from a server
        :raises: :py:class:`.VersionNotSupported` if requested api_version
            is not supported
        :raises: *requests* library exception on connection problems.
        :return: a list of status dictionaries with the keys:

            * `error` an error string or None,
            * `finished` whether introspection was finished,
            * `finished_at` an ISO8601 timestamp or None,
            * `links` with a self-link URL,
            * `started_at` an ISO8601 timestamp,
            * `uuid` the node UUID
        """
        if not (marker is None or isinstance(marker, six.string_types)):
            raise TypeError(_('Expected a string value of the marker, got '
                              '%s instead') % marker)
        if not (limit is None or isinstance(limit, int)):
            raise TypeError(_('Expected an integer value of the limit, got '
                              '%s instead') % limit)

        params = {
            'marker': marker,
            'limit': limit,
        }
        response = self.request('get', '/introspection', params=params)
        return response.json()['introspection']

    def get_status(self, uuid):
        """Get introspection status for a node.

        :param uuid: node UUID or name.
        :raises: :py:class:`.ClientError` on error reported from a server
        :raises: :py:class:`.VersionNotSupported` if requested api_version
            is not supported
        :raises: *requests* library exception on connection problems.
        :return: dictionary with the keys:

            * `error` an error string or None,
            * `finished` whether introspection was finished,
            * `finished_at` an ISO8601 timestamp or None,
            * `links` with a self-link URL,
            * `started_at` an ISO8601 timestamp,
            * `uuid` the node UUID
        """
        if not isinstance(uuid, six.string_types):
            raise TypeError(
                _("Expected string for uuid argument, got %r") % uuid)

        return self.request('get', '/introspection/%s' % uuid).json()

    def wait_for_finish(self, uuids, retry_interval=DEFAULT_RETRY_INTERVAL,
                        max_retries=DEFAULT_MAX_RETRIES,
                        sleep_function=time.sleep):
        """Wait for introspection finishing for given nodes.

        :param uuids: collection of node UUIDs or names.
        :param retry_interval: sleep interval between retries.
        :param max_retries: maximum number of retries.
        :param sleep_function: function used for sleeping between retries.
        :raises: :py:class:`.WaitTimeoutError` on timeout
        :raises: :py:class:`.ClientError` on error reported from a server
        :raises: :py:class:`.VersionNotSupported` if requested api_version
            is not supported
        :raises: *requests* library exception on connection problems.
        :return: dictionary UUID -> status (the same as in get_status).
        """
        result = {}

        # Number of attempts = number of retries + first attempt
        for attempt in range(max_retries + 1):
            new_active_uuids = []
            for uuid in uuids:
                status = self.get_status(uuid)
                if status.get('finished'):
                    result[uuid] = status
                else:
                    new_active_uuids.append(uuid)

            if new_active_uuids:
                if attempt != max_retries:
                    uuids = new_active_uuids
                    LOG.debug('Still waiting for introspection results for '
                              '%(count)d nodes, attempt %(attempt)d of '
                              '%(total)d',
                              {'count': len(new_active_uuids),
                               'attempt': attempt + 1,
                               'total': max_retries + 1})
                    sleep_function(retry_interval)
            else:
                return result

        raise WaitTimeoutError(_("Timeout while waiting for introspection "
                                 "of nodes %s") % new_active_uuids)

    def get_data(self, uuid, raw=False):
        """Get introspection data from the last introspection of a node.

        :param uuid: node UUID or name.
        :param raw: whether to return raw binary data or parsed JSON data
        :returns: bytes or a dict depending on the 'raw' argument
        :raises: :py:class:`.ClientError` on error reported from a server
        :raises: :py:class:`.VersionNotSupported` if requested api_version
            is not supported
        :raises: *requests* library exception on connection problems.
        :raises: TypeError if uuid is not a string
        """
        if not isinstance(uuid, six.string_types):
            raise TypeError(
                _("Expected string for uuid argument, got %r") % uuid)

        resp = self.request('get', '/introspection/%s/data' % uuid)
        if raw:
            return resp.content
        else:
            return resp.json()

    def abort(self, uuid):
        """Abort running introspection for a node.

        :param uuid: node UUID or name.
        :raises: :py:class:`.ClientError` on error reported from a server
        :raises: :py:class:`.VersionNotSupported` if requested api_version
            is not supported
        :raises: *requests* library exception on connection problems.
        :raises: TypeError if uuid is not a string.
        """
        if not isinstance(uuid, six.string_types):
            raise TypeError(_("Expected string for uuid argument, got"
                              " %r") % uuid)

        return self.request('post', '/introspection/%s/abort' % uuid)

    def get_interface_data(self, node_ident, interface, field_sel):
        """Get interface data for the input node and interface

        To get LLDP data, collection must be enabled by the kernel parameter
        ``ipa-collect-lldp=1``, and the inspector plugin ``basic_lldp`` must
        be enabled.

        :param node_ident: node UUID or name
        :param interface: interface name
        :param field_sel: list of all fields for which to get data
        :returns: interface data in OrderedDict
        """
        # Use OrderedDict to maintain order of user-entered fields
        iface_data = OrderedDict()

        data = self.get_data(node_ident)
        all_interfaces = data.get('all_interfaces', [])

        # Make sure interface name is valid
        if interface not in all_interfaces:
            return iface_data

        # If lldp data not available this will still return interface,
        # mac, node_ident etc.
        lldp_proc = all_interfaces[interface].get('lldp_processed', {})

        for f in field_sel:
            if f == 'node_ident':
                iface_data[f] = node_ident
            elif f == 'interface':
                iface_data[f] = interface
            elif f == 'mac':
                iface_data[f] = all_interfaces[interface].get(f)
            elif f == 'switch_port_vlan_ids':
                iface_data[f] = [item['id'] for item in
                                 lldp_proc.get('switch_port_vlans', [])]
            else:
                iface_data[f] = lldp_proc.get(f)

        return iface_data

    def get_all_interface_data(self, node_ident,
                               field_sel, vlan=None):
        """Get interface data for all of the interfaces on this node

        :param node_ident: node UUID or name
        :param field_sel: list of all fields for which to get data
        :param vlan: list of vlans used to filter the lists returned
        :returns: list of interface data, each interface in a list
        """

        # Get inventory data for this node
        data = self.get_data(node_ident)
        all_interfaces = data.get('all_interfaces', [])

        rows = []
        if vlan:
            vlan = set(vlan)
        # walk all interfaces, appending data to row if not filtered
        for interface in all_interfaces:
            iface_dict = self.get_interface_data(node_ident,
                                                 interface,
                                                 field_sel)

            values = list(iface_dict.values())

            # Use (optional) vlans to filter row
            if not vlan:
                rows.append(values)
                continue

            # curr_vlans may be None
            curr_vlans = iface_dict.get('switch_port_vlan_ids', [])
            if curr_vlans and (vlan & set(curr_vlans)):
                rows.append(values)  # vlan matches, display this row

        return rows


class RulesAPI(object):
    """Introspection rules API.

    Do not create instances of this class directly, use
    :py:attr:`ironic_inspector_client.v1.ClientV1.rules` instead.
    """

    def __init__(self, requester):
        self._request = requester

    def create(self, conditions, actions, uuid=None, description=None):
        """Create a new introspection rule.

        :param conditions: list of rule conditions
        :param actions: list of rule actions
        :param uuid: rule UUID, will be generated if not specified
        :param description: optional rule description
        :returns: rule representation
        :raises: :py:class:`.ClientError` on error reported from a server
        :raises: :py:class:`.VersionNotSupported` if requested api_version
            is not supported
        """
        if uuid is not None and not isinstance(uuid, six.string_types):
            raise TypeError(
                _("Expected string for uuid argument, got %r") % uuid)
        for name, arg in [('conditions', conditions), ('actions', actions)]:
            if not isinstance(arg, list) or not all(isinstance(x, dict)
                                                    for x in arg):
                raise TypeError(_("Expected list of dicts for %(arg)s "
                                  "argument, got %(real)r"),
                                {'arg': name, 'real': arg})

        body = {'uuid': uuid, 'conditions': conditions, 'actions': actions,
                'description': description}
        return self.from_json(body)

    def from_json(self, json_rule):
        """Import an introspection rule from JSON data.

        :param json_rule: rule information as a dict with keys matching
            arguments of :py:meth:`RulesAPI.create`.
        :returns: rule representation
        :raises: :py:class:`.ClientError` on error reported from a server
        :raises: :py:class:`.VersionNotSupported` if requested api_version
            is not supported
        """
        return self._request('post', '/rules', json=json_rule).json()

    def get_all(self):
        """List all introspection rules.

        :returns: list of short rule representations (uuid, description
                  and links)
        :raises: :py:class:`.ClientError` on error reported from a server
        :raises: :py:class:`.VersionNotSupported` if requested api_version
            is not supported
        """
        return self._request('get', '/rules').json()['rules']

    def get(self, uuid):
        """Get detailed information about an introspection rule.

        :param uuid: rule UUID
        :returns: rule representation
        :raises: :py:class:`.ClientError` on error reported from a server
        :raises: :py:class:`.VersionNotSupported` if requested api_version
            is not supported
        """
        if not isinstance(uuid, six.string_types):
            raise TypeError(
                _("Expected string for uuid argument, got %r") % uuid)
        return self._request('get', '/rules/%s' % uuid).json()

    def delete(self, uuid):
        """Delete an introspection rule.

        :param uuid: rule UUID
        :raises: :py:class:`.ClientError` on error reported from a server
        :raises: :py:class:`.VersionNotSupported` if requested api_version
            is not supported
        """
        if not isinstance(uuid, six.string_types):
            raise TypeError(
                _("Expected string for uuid argument, got %r") % uuid)
        self._request('delete', '/rules/%s' % uuid)

    def delete_all(self):
        """Delete all introspection rules.

        :raises: :py:class:`.ClientError` on error reported from a server
        :raises: :py:class:`.VersionNotSupported` if requested api_version
            is not supported
        """
        self._request('delete', '/rules')
