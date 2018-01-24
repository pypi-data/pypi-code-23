# Copyright 2012 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import abc
import collections
import os
import re
import shutil
import time

import netaddr
from neutron_lib.api.definitions import extra_dhcp_opt as edo_ext
from neutron_lib import constants
from neutron_lib import exceptions
from neutron_lib.utils import file as file_utils
from oslo_log import log as logging
import oslo_messaging
from oslo_utils import excutils
from oslo_utils import fileutils
from oslo_utils import uuidutils
import six

from neutron._i18n import _
from neutron.agent.common import utils as agent_common_utils
from neutron.agent.linux import external_process
from neutron.agent.linux import ip_lib
from neutron.agent.linux import iptables_manager
from neutron.cmd import runtime_checks as checks
from neutron.common import constants as n_const
from neutron.common import ipv6_utils
from neutron.common import utils as common_utils
from neutron.ipam import utils as ipam_utils

LOG = logging.getLogger(__name__)

UDP = 'udp'
TCP = 'tcp'
DNS_PORT = 53
DHCPV4_PORT = 67
DHCPV6_PORT = 547
METADATA_DEFAULT_PREFIX = 16
METADATA_DEFAULT_IP = '169.254.169.254'
METADATA_DEFAULT_CIDR = '%s/%d' % (METADATA_DEFAULT_IP,
                                   METADATA_DEFAULT_PREFIX)
METADATA_PORT = 80
WIN2k3_STATIC_DNS = 249
NS_PREFIX = 'qdhcp-'
DNSMASQ_SERVICE_NAME = 'dnsmasq'


class DictModel(dict):
    """Convert dict into an object that provides attribute access to values."""

    def __init__(self, *args, **kwargs):
        """Convert dict values to DictModel values."""
        super(DictModel, self).__init__(*args, **kwargs)

        def needs_upgrade(item):
            """Check if `item` is a dict and needs to be changed to DictModel.
            """
            return isinstance(item, dict) and not isinstance(item, DictModel)

        def upgrade(item):
            """Upgrade item if it needs to be upgraded."""
            if needs_upgrade(item):
                return DictModel(item)
            else:
                return item

        for key, value in self.items():
            if isinstance(value, (list, tuple)):
                # Keep the same type but convert dicts to DictModels
                self[key] = type(value)(
                    (upgrade(item) for item in value)
                )
            elif needs_upgrade(value):
                # Change dict instance values to DictModel instance values
                self[key] = DictModel(value)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(e)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]

    def __str__(self):
        pairs = ['%s=%s' % (k, v) for k, v in self.items()]
        return ', '.join(sorted(pairs))


class NetModel(DictModel):

    def __init__(self, d):
        super(NetModel, self).__init__(d)

        self._ns_name = "%s%s" % (NS_PREFIX, self.id)

    @property
    def namespace(self):
        return self._ns_name


@six.add_metaclass(abc.ABCMeta)
class DhcpBase(object):

    def __init__(self, conf, network, process_monitor,
                 version=None, plugin=None):
        self.conf = conf
        self.network = network
        self.process_monitor = process_monitor
        self.device_manager = DeviceManager(self.conf, plugin)
        self.version = version

    @abc.abstractmethod
    def enable(self):
        """Enables DHCP for this network."""

    @abc.abstractmethod
    def disable(self, retain_port=False):
        """Disable dhcp for this network."""

    def restart(self):
        """Restart the dhcp service for the network."""
        self.disable(retain_port=True)
        self.enable()

    @abc.abstractproperty
    def active(self):
        """Boolean representing the running state of the DHCP server."""

    @abc.abstractmethod
    def reload_allocations(self):
        """Force the DHCP server to reload the assignment database."""

    @classmethod
    def existing_dhcp_networks(cls, conf):
        """Return a list of existing networks ids that we have configs for."""

        raise NotImplementedError()

    @classmethod
    def check_version(cls):
        """Execute version checks on DHCP server."""

        raise NotImplementedError()

    @classmethod
    def get_isolated_subnets(cls, network):
        """Returns a dict indicating whether or not a subnet is isolated"""
        raise NotImplementedError()

    @classmethod
    def should_enable_metadata(cls, conf, network):
        """True if the metadata-proxy should be enabled for the network."""
        raise NotImplementedError()


@six.add_metaclass(abc.ABCMeta)
class DhcpLocalProcess(DhcpBase):
    PORTS = []

    def __init__(self, conf, network, process_monitor, version=None,
                 plugin=None):
        super(DhcpLocalProcess, self).__init__(conf, network, process_monitor,
                                               version, plugin)
        self.confs_dir = self.get_confs_dir(conf)
        self.network_conf_dir = os.path.join(self.confs_dir, network.id)
        fileutils.ensure_tree(self.network_conf_dir, mode=0o755)

    @staticmethod
    def get_confs_dir(conf):
        return os.path.abspath(os.path.normpath(conf.dhcp_confs))

    def get_conf_file_name(self, kind):
        """Returns the file name for a given kind of config file."""
        return os.path.join(self.network_conf_dir, kind)

    def _remove_config_files(self):
        shutil.rmtree(self.network_conf_dir, ignore_errors=True)

    @staticmethod
    def _get_all_subnets(network):
        non_local_subnets = getattr(network, 'non_local_subnets', [])
        return network.subnets + non_local_subnets

    def _enable_dhcp(self):
        """check if there is a subnet within the network with dhcp enabled."""
        for subnet in self.network.subnets:
            if subnet.enable_dhcp:
                return True
        return False

    def enable(self):
        """Enables DHCP for this network by spawning a local process."""
        if self.active:
            self.restart()
        elif self._enable_dhcp():
            fileutils.ensure_tree(self.network_conf_dir, mode=0o755)
            interface_name = self.device_manager.setup(self.network)
            self.interface_name = interface_name
            self.spawn_process()

    def _get_process_manager(self, cmd_callback=None):
        return external_process.ProcessManager(
            conf=self.conf,
            uuid=self.network.id,
            namespace=self.network.namespace,
            default_cmd_callback=cmd_callback,
            pid_file=self.get_conf_file_name('pid'),
            run_as_root=True)

    def disable(self, retain_port=False):
        """Disable DHCP for this network by killing the local process."""
        self.process_monitor.unregister(self.network.id, DNSMASQ_SERVICE_NAME)
        self._get_process_manager().disable()
        if not retain_port:
            self._destroy_namespace_and_port()
        self._remove_config_files()

    def _destroy_namespace_and_port(self):
        try:
            self.device_manager.destroy(self.network, self.interface_name)
        except RuntimeError:
            LOG.warning('Failed trying to delete interface: %s',
                        self.interface_name)

        if not ip_lib.network_namespace_exists(self.network.namespace):
            LOG.debug("Namespace already deleted: %s", self.network.namespace)
            return
        try:
            ip_lib.delete_network_namespace(self.network.namespace)
        except RuntimeError:
            LOG.warning('Failed trying to delete namespace: %s',
                        self.network.namespace)

    def _get_value_from_conf_file(self, kind, converter=None):
        """A helper function to read a value from one of the state files."""
        file_name = self.get_conf_file_name(kind)
        msg = _('Error while reading %s')

        try:
            with open(file_name, 'r') as f:
                try:
                    return converter(f.read()) if converter else f.read()
                except ValueError:
                    msg = _('Unable to convert value in %s')
        except IOError:
            msg = _('Unable to access %s')

        LOG.debug(msg, file_name)
        return None

    @property
    def interface_name(self):
        return self._get_value_from_conf_file('interface')

    @interface_name.setter
    def interface_name(self, value):
        interface_file_path = self.get_conf_file_name('interface')
        file_utils.replace_file(interface_file_path, value)

    @property
    def active(self):
        return self._get_process_manager().active

    @abc.abstractmethod
    def spawn_process(self):
        pass


class Dnsmasq(DhcpLocalProcess):
    # The ports that need to be opened when security policies are active
    # on the Neutron port used for DHCP.  These are provided as a convenience
    # for users of this class.
    PORTS = {constants.IP_VERSION_4:
             [(UDP, DNS_PORT), (TCP, DNS_PORT), (UDP, DHCPV4_PORT)],
             constants.IP_VERSION_6:
             [(UDP, DNS_PORT), (TCP, DNS_PORT), (UDP, DHCPV6_PORT)],
             }

    _TAG_PREFIX = 'tag%d'

    _ID = 'id:'

    _IS_DHCP_RELEASE6_SUPPORTED = None

    @classmethod
    def check_version(cls):
        pass

    @classmethod
    def existing_dhcp_networks(cls, conf):
        """Return a list of existing networks ids that we have configs for."""
        confs_dir = cls.get_confs_dir(conf)
        try:
            return [
                c for c in os.listdir(confs_dir)
                if uuidutils.is_uuid_like(c)
            ]
        except OSError:
            return []

    def _build_cmdline_callback(self, pid_file):
        # We ignore local resolv.conf if dns servers are specified
        # or if local resolution is explicitly disabled.
        _no_resolv = (
            '--no-resolv' if self.conf.dnsmasq_dns_servers or
            not self.conf.dnsmasq_local_resolv else '')
        cmd = [
            'dnsmasq',
            '--no-hosts',
            _no_resolv,
            '--strict-order',
            '--except-interface=lo',
            '--pid-file=%s' % pid_file,
            '--dhcp-hostsfile=%s' % self.get_conf_file_name('host'),
            '--addn-hosts=%s' % self.get_conf_file_name('addn_hosts'),
            '--dhcp-optsfile=%s' % self.get_conf_file_name('opts'),
            '--dhcp-leasefile=%s' % self.get_conf_file_name('leases'),
            '--dhcp-match=set:ipxe,175',
        ]
        if self.device_manager.driver.bridged:
            cmd += [
                '--bind-interfaces',
                '--interface=%s' % self.interface_name,
            ]
        else:
            cmd += [
                '--bind-dynamic',
                '--interface=%s' % self.interface_name,
                '--interface=tap*',
                '--bridge-interface=%s,tap*' % self.interface_name,
            ]

        possible_leases = 0
        for i, subnet in enumerate(self._get_all_subnets(self.network)):
            mode = None
            # if a subnet is specified to have dhcp disabled
            if not subnet.enable_dhcp:
                continue
            if subnet.ip_version == 4:
                mode = 'static'
            else:
                # Note(scollins) If the IPv6 attributes are not set, set it as
                # static to preserve previous behavior
                addr_mode = getattr(subnet, 'ipv6_address_mode', None)
                ra_mode = getattr(subnet, 'ipv6_ra_mode', None)
                if (addr_mode in [constants.DHCPV6_STATEFUL,
                                  constants.DHCPV6_STATELESS] or
                        not addr_mode and not ra_mode):
                    mode = 'static'

            cidr = netaddr.IPNetwork(subnet.cidr)

            if self.conf.dhcp_lease_duration == -1:
                lease = 'infinite'
            else:
                lease = '%ss' % self.conf.dhcp_lease_duration

            # mode is optional and is not set - skip it
            if mode:
                if subnet.ip_version == 4:
                    cmd.append('--dhcp-range=%s%s,%s,%s,%s,%s' %
                               ('set:', self._TAG_PREFIX % i,
                                cidr.network, mode, cidr.netmask, lease))
                else:
                    if cidr.prefixlen < 64:
                        LOG.debug('Ignoring subnet %(subnet)s, CIDR has '
                                  'prefix length < 64: %(cidr)s',
                                  {'subnet': subnet.id, 'cidr': cidr})
                        continue
                    cmd.append('--dhcp-range=%s%s,%s,%s,%d,%s' %
                               ('set:', self._TAG_PREFIX % i,
                                cidr.network, mode,
                                cidr.prefixlen, lease))
                possible_leases += cidr.size

        mtu = getattr(self.network, 'mtu', 0)
        # Do not advertise unknown mtu
        if mtu > 0:
            cmd.append('--dhcp-option-force=option:mtu,%d' % mtu)

        # Cap the limit because creating lots of subnets can inflate
        # this possible lease cap.
        cmd.append('--dhcp-lease-max=%d' %
                   min(possible_leases, self.conf.dnsmasq_lease_max))

        if self.conf.dhcp_renewal_time > 0:
            cmd.append('--dhcp-option-force=option:T1,%ds' %
                       self.conf.dhcp_renewal_time)

        if self.conf.dhcp_rebinding_time > 0:
            cmd.append('--dhcp-option-force=option:T2,%ds' %
                       self.conf.dhcp_rebinding_time)

        cmd.append('--conf-file=%s' % self.conf.dnsmasq_config_file)
        for server in self.conf.dnsmasq_dns_servers:
            cmd.append('--server=%s' % server)

        if self.conf.dns_domain:
            cmd.append('--domain=%s' % self.conf.dns_domain)

        if self.conf.dhcp_broadcast_reply:
            cmd.append('--dhcp-broadcast')

        if self.conf.dnsmasq_base_log_dir:
            log_dir = os.path.join(
                self.conf.dnsmasq_base_log_dir,
                self.network.id)
            try:
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
            except OSError:
                LOG.error('Error while create dnsmasq log dir: %s', log_dir)
            else:
                log_filename = os.path.join(log_dir, 'dhcp_dns_log')
                cmd.append('--log-queries')
                cmd.append('--log-dhcp')
                cmd.append('--log-facility=%s' % log_filename)

        return cmd

    def spawn_process(self):
        """Spawn the process, if it's not spawned already."""
        # we only need to generate the lease file the first time dnsmasq starts
        # rather than on every reload since dnsmasq will keep the file current
        self._output_init_lease_file()
        self._spawn_or_reload_process(reload_with_HUP=False)

    def _spawn_or_reload_process(self, reload_with_HUP):
        """Spawns or reloads a Dnsmasq process for the network.

        When reload_with_HUP is True, dnsmasq receives a HUP signal,
        or it's reloaded if the process is not running.
        """

        self._output_config_files()

        pm = self._get_process_manager(
            cmd_callback=self._build_cmdline_callback)

        pm.enable(reload_cfg=reload_with_HUP)

        self.process_monitor.register(uuid=self.network.id,
                                      service_name=DNSMASQ_SERVICE_NAME,
                                      monitored_process=pm)

    def _is_dhcp_release6_supported(self):
        if self._IS_DHCP_RELEASE6_SUPPORTED is None:
            self._IS_DHCP_RELEASE6_SUPPORTED = checks.dhcp_release6_supported()
            if not self._IS_DHCP_RELEASE6_SUPPORTED:
                LOG.warning("dhcp_release6 is not present on this system, "
                            "will not call it again.")
        return self._IS_DHCP_RELEASE6_SUPPORTED

    def _release_lease(self, mac_address, ip, client_id=None,
                       server_id=None, iaid=None):
        """Release a DHCP lease."""
        if netaddr.IPAddress(ip).version == constants.IP_VERSION_6:
            if not self._is_dhcp_release6_supported():
                return
            cmd = ['dhcp_release6', '--iface', self.interface_name,
                   '--ip', ip, '--client-id', client_id,
                   '--server-id', server_id, '--iaid', iaid]
        else:
            cmd = ['dhcp_release', self.interface_name, ip, mac_address]
            if client_id:
                cmd.append(client_id)
        ip_wrapper = ip_lib.IPWrapper(namespace=self.network.namespace)
        try:
            ip_wrapper.netns.execute(cmd, run_as_root=True)
        except RuntimeError as e:
            # when failed to release single lease there's
            # no need to propagate error further
            LOG.warning('DHCP release failed for %(cmd)s. '
                        'Reason: %(e)s', {'cmd': cmd, 'e': e})

    def _output_config_files(self):
        self._output_hosts_file()
        self._output_addn_hosts_file()
        self._output_opts_file()

    def reload_allocations(self):
        """Rebuild the dnsmasq config and signal the dnsmasq to reload."""

        # If all subnets turn off dhcp, kill the process.
        if not self._enable_dhcp():
            self.disable()
            LOG.debug('Killing dnsmasq for network since all subnets have '
                      'turned off DHCP: %s', self.network.id)
            return
        if not self.interface_name:
            # we land here if above has been called and we receive port
            # delete notifications for the network
            LOG.debug('Agent does not have an interface on this network '
                      'anymore, skipping reload: %s', self.network.id)
            return

        self._release_unused_leases()
        self._spawn_or_reload_process(reload_with_HUP=True)
        LOG.debug('Reloading allocations for network: %s', self.network.id)
        self.device_manager.update(self.network, self.interface_name)

    def _sort_fixed_ips_for_dnsmasq(self, fixed_ips, v6_nets):
        """Sort fixed_ips so that stateless IPv6 subnets appear first.

        For example, If a port with v6 extra_dhcp_opts is on a network with
        IPv4 and IPv6 stateless subnets. Then dhcp host file will have
        below 2 entries for same MAC,

        fa:16:3e:8f:9d:65,30.0.0.5,set:aabc7d33-4874-429e-9637-436e4232d2cd
        (entry for IPv4 dhcp)
        fa:16:3e:8f:9d:65,set:aabc7d33-4874-429e-9637-436e4232d2cd
        (entry for stateless IPv6 for v6 options)

        dnsmasq internal details for processing host file entries
        1) dnsmasq reads the host file from EOF.
        2) So it first picks up stateless IPv6 entry,
           fa:16:3e:8f:9d:65,set:aabc7d33-4874-429e-9637-436e4232d2cd
        3) But dnsmasq doesn't have sufficient checks to skip this entry and
           pick next entry, to process dhcp IPv4 request.
        4) So dnsmasq uses this entry to process dhcp IPv4 request.
        5) As there is no ip in this entry, dnsmasq logs "no address available"
           and fails to send DHCPOFFER message.

        As we rely on internal details of dnsmasq to understand and fix the
        issue, Ihar sent a mail to dnsmasq-discuss mailing list
        http://lists.thekelleys.org.uk/pipermail/dnsmasq-discuss/2015q2/
        009650.html

        So if we reverse the order of writing entries in host file,
        so that entry for stateless IPv6 comes first,
        then dnsmasq can correctly fetch the IPv4 address.
        """
        return sorted(
            fixed_ips,
            key=lambda fip: ((fip.subnet_id in v6_nets) and (
                v6_nets[fip.subnet_id].ipv6_address_mode == (
                    constants.DHCPV6_STATELESS))),
            reverse=True)

    def _iter_hosts(self):
        """Iterate over hosts.

        For each host on the network we yield a tuple containing:
        (
            port,  # a DictModel instance representing the port.
            alloc,  # a DictModel instance of the allocated ip and subnet.
                    # if alloc is None, it means there is no need to allocate
                    # an IPv6 address because of stateless DHCPv6 network.
            host_name,  # Host name.
            name,  # Canonical hostname in the format 'hostname[.domain]'.
            no_dhcp,  # A flag indicating that the address doesn't need a DHCP
                      # IP address.
            no_opts,  # A flag indication that options shouldn't be written
        )
        """
        v6_nets = dict((subnet.id, subnet) for subnet in
                       self._get_all_subnets(self.network)
                       if subnet.ip_version == 6)

        for port in self.network.ports:
            fixed_ips = self._sort_fixed_ips_for_dnsmasq(port.fixed_ips,
                                                         v6_nets)
            # Confirm whether Neutron server supports dns_name attribute in the
            # ports API
            dns_assignment = getattr(port, 'dns_assignment', None)
            if dns_assignment:
                dns_ip_map = {d.ip_address: d for d in dns_assignment}
            for alloc in fixed_ips:
                no_dhcp = False
                no_opts = False
                if alloc.subnet_id in v6_nets:
                    addr_mode = v6_nets[alloc.subnet_id].ipv6_address_mode
                    no_dhcp = addr_mode in (constants.IPV6_SLAAC,
                                            constants.DHCPV6_STATELESS)
                    # we don't setup anything for SLAAC. It doesn't make sense
                    # to provide options for a client that won't use DHCP
                    no_opts = addr_mode == constants.IPV6_SLAAC

                # If dns_name attribute is supported by ports API, return the
                # dns_assignment generated by the Neutron server. Otherwise,
                # generate hostname and fqdn locally (previous behaviour)
                if dns_assignment:
                    hostname = dns_ip_map[alloc.ip_address].hostname
                    fqdn = dns_ip_map[alloc.ip_address].fqdn
                else:
                    hostname = 'host-%s' % alloc.ip_address.replace(
                        '.', '-').replace(':', '-')
                    fqdn = hostname
                    if self.conf.dns_domain:
                        fqdn = '%s.%s' % (fqdn, self.conf.dns_domain)
                yield (port, alloc, hostname, fqdn, no_dhcp, no_opts)

    def _get_port_extra_dhcp_opts(self, port):
        return getattr(port, edo_ext.EXTRADHCPOPTS, False)

    def _output_init_lease_file(self):
        """Write a fake lease file to bootstrap dnsmasq.

        The generated file is passed to the --dhcp-leasefile option of dnsmasq.
        This is used as a bootstrapping mechanism to avoid NAKing active leases
        when a dhcp server is scheduled to another agent. Using a leasefile
        will also prevent dnsmasq from NAKing or ignoring renewals after a
        restart.

        Format is as follows:
        epoch-timestamp mac_addr ip_addr hostname client-ID
        """
        filename = self.get_conf_file_name('leases')
        buf = six.StringIO()

        LOG.debug('Building initial lease file: %s', filename)
        # we make up a lease time for the database entry
        if self.conf.dhcp_lease_duration == -1:
            # Even with an infinite lease, a client may choose to renew a
            # previous lease on reboot or interface bounce so we should have
            # an entry for it.
            # Dnsmasq timestamp format for an infinite lease is 0.
            timestamp = 0
        else:
            timestamp = int(time.time()) + self.conf.dhcp_lease_duration
        dhcp_enabled_subnet_ids = [s.id for s in
                                   self._get_all_subnets(self.network)
                                   if s.enable_dhcp]
        for host_tuple in self._iter_hosts():
            port, alloc, hostname, name, no_dhcp, no_opts = host_tuple
            # don't write ip address which belongs to a dhcp disabled subnet
            # or an IPv6 SLAAC/stateless subnet
            if no_dhcp or alloc.subnet_id not in dhcp_enabled_subnet_ids:
                continue

            ip_address = self._format_address_for_dnsmasq(alloc.ip_address)
            # all that matters is the mac address and IP. the hostname and
            # client ID will be overwritten on the next renewal.
            buf.write('%s %s %s * *\n' %
                      (timestamp, port.mac_address, ip_address))
        contents = buf.getvalue()
        file_utils.replace_file(filename, contents)
        LOG.debug('Done building initial lease file %s with contents:\n%s',
                  filename, contents)
        return filename

    @staticmethod
    def _format_address_for_dnsmasq(address):
        # (dzyu) Check if it is legal ipv6 address, if so, need wrap
        # it with '[]' to let dnsmasq to distinguish MAC address from
        # IPv6 address.
        if netaddr.valid_ipv6(address):
            return '[%s]' % address
        return address

    def _output_hosts_file(self):
        """Writes a dnsmasq compatible dhcp hosts file.

        The generated file is sent to the --dhcp-hostsfile option of dnsmasq,
        and lists the hosts on the network which should receive a dhcp lease.
        Each line in this file is in the form::

            'mac_address,FQDN,ip_address'

        IMPORTANT NOTE: a dnsmasq instance does not resolve hosts defined in
        this file if it did not give a lease to a host listed in it (e.g.:
        multiple dnsmasq instances on the same network if this network is on
        multiple network nodes). This file is only defining hosts which
        should receive a dhcp lease, the hosts resolution in itself is
        defined by the `_output_addn_hosts_file` method.
        """
        buf = six.StringIO()
        filename = self.get_conf_file_name('host')

        LOG.debug('Building host file: %s', filename)
        dhcp_enabled_subnet_ids = [s.id for s in
                                   self._get_all_subnets(self.network)
                                   if s.enable_dhcp]
        # NOTE(ihrachyshka): the loop should not log anything inside it, to
        # avoid potential performance drop when lots of hosts are dumped
        for host_tuple in self._iter_hosts():
            port, alloc, hostname, name, no_dhcp, no_opts = host_tuple
            if no_dhcp:
                if not no_opts and self._get_port_extra_dhcp_opts(port):
                    buf.write('%s,%s%s\n' %
                              (port.mac_address, 'set:', port.id))
                continue

            # don't write ip address which belongs to a dhcp disabled subnet.
            if alloc.subnet_id not in dhcp_enabled_subnet_ids:
                continue

            ip_address = self._format_address_for_dnsmasq(alloc.ip_address)

            if self._get_port_extra_dhcp_opts(port):
                client_id = self._get_client_id(port)
                if client_id and len(port.extra_dhcp_opts) > 1:
                    buf.write('%s,%s%s,%s,%s,%s%s\n' %
                              (port.mac_address, self._ID, client_id, name,
                               ip_address, 'set:', port.id))
                elif client_id and len(port.extra_dhcp_opts) == 1:
                    buf.write('%s,%s%s,%s,%s\n' %
                          (port.mac_address, self._ID, client_id, name,
                           ip_address))
                else:
                    buf.write('%s,%s,%s,%s%s\n' %
                              (port.mac_address, name, ip_address,
                               'set:', port.id))
            else:
                buf.write('%s,%s,%s\n' %
                          (port.mac_address, name, ip_address))

        file_utils.replace_file(filename, buf.getvalue())
        LOG.debug('Done building host file %s', filename)
        return filename

    def _get_client_id(self, port):
        if self._get_port_extra_dhcp_opts(port):
            for opt in port.extra_dhcp_opts:
                if opt.opt_name == edo_ext.DHCP_OPT_CLIENT_ID:
                    return opt.opt_value

    def _read_hosts_file_leases(self, filename):
        leases = set()
        try:
            with open(filename) as f:
                for l in f.readlines():
                    host = l.strip().split(',')
                    mac = host[0]
                    client_id = None
                    if host[1].startswith('set:'):
                        continue
                    if host[1].startswith(self._ID):
                        ip = host[3].strip('[]')
                        client_id = host[1][len(self._ID):]
                    else:
                        ip = host[2].strip('[]')
                    leases.add((ip, mac, client_id))
        except (OSError, IOError):
            LOG.debug('Error while reading hosts file %s', filename)
        return leases

    def _read_v6_leases_file_leases(self, filename):
        """
        reading information from leases file which is needed to pass to
        dhcp_release6 command line utility if some of these leases are not
        needed anymore

        in this method  ipv4 entries in leases file are ignored, as info in
        hosts file is enough

        each line in dnsmasq leases file is one of the following
          * duid entry: duid server_duid
          There MUST be single duid entry per file
          * ipv4 entry: space separated list
            - The expiration time (seconds since unix epoch) or duration
              (if dnsmasq is compiled with HAVE_BROKEN_RTC) of the lease.
              0 means infinite.
            - The link address, in format XX-YY:YY:YY[...], where XX is the ARP
              hardware type.  "XX-" may be omitted for Ethernet.
            - The IPv4 address
            - The hostname (sent by the client or assigned by dnsmasq)
              or '*' for none.
            - The client identifier (colon-separated hex bytes)
              or '*' for none.

          *  ipv6 entry: space separated list
            - The expiration time or duration
            - The IAID as a Big Endian decimal number, prefixed by T for
              IA_TAs (temporary addresses).
            - The IPv6 address
            - The hostname or '*'
            - The client DUID (colon-separated hex bytes) or '*' if unknown

        original discussion is in dnsmasq mailing list
        http://lists.thekelleys.org.uk/pipermail/\
        dnsmasq-discuss/2016q2/010595.html

        :param filename: leases file
        :return: dict, keys are IPv6 addresses, values are dicts containing
                iaid, client_id and server_id
        """
        leases = {}
        server_id = None
        if os.path.exists(filename):
            with open(filename) as f:
                for l in f.readlines():
                    if l.startswith('duid'):
                        if not server_id:
                            server_id = l.strip().split()[1]
                            continue
                        else:
                            LOG.warning('Multiple DUID entries in %s '
                                        'lease file, dnsmasq is possibly '
                                        'not functioning properly',
                                        filename)
                            continue
                    parts = l.strip().split()
                    (iaid, ip, client_id) = parts[1], parts[2], parts[4]
                    ip = ip.strip('[]')
                    if netaddr.IPAddress(ip).version == constants.IP_VERSION_4:
                        continue
                    leases[ip] = {'iaid': iaid,
                                  'client_id': client_id,
                                  'server_id': server_id
                                  }
        return leases

    def _release_unused_leases(self):
        filename = self.get_conf_file_name('host')
        old_leases = self._read_hosts_file_leases(filename)
        leases_filename = self.get_conf_file_name('leases')
        # here is dhcpv6 stuff needed to craft dhcpv6 packet
        v6_leases = self._read_v6_leases_file_leases(leases_filename)
        new_leases = set()
        for port in self.network.ports:
            client_id = self._get_client_id(port)
            for alloc in port.fixed_ips:
                new_leases.add((alloc.ip_address, port.mac_address, client_id))

        for ip, mac, client_id in old_leases - new_leases:
            entry = v6_leases.get(ip, None)
            version = netaddr.IPAddress(ip).version
            if entry:
                # must release IPv6 lease
                self._release_lease(mac, ip, entry['client_id'],
                                    entry['server_id'], entry['iaid'])
            # must release only if v4 lease. If we have ipv6 address missing
            # in old_leases, that means it's released already and nothing to do
            # here
            elif version == constants.IP_VERSION_4:
                self._release_lease(mac, ip, client_id)

    def _output_addn_hosts_file(self):
        """Writes a dnsmasq compatible additional hosts file.

        The generated file is sent to the --addn-hosts option of dnsmasq,
        and lists the hosts on the network which should be resolved even if
        the dnsmasq instance did not give a lease to the host (see the
        `_output_hosts_file` method).
        Each line in this file is in the same form as a standard /etc/hosts
        file.
        """
        buf = six.StringIO()
        for host_tuple in self._iter_hosts():
            port, alloc, hostname, fqdn, no_dhcp, no_opts = host_tuple
            # It is compulsory to write the `fqdn` before the `hostname` in
            # order to obtain it in PTR responses.
            if alloc:
                buf.write('%s\t%s %s\n' % (alloc.ip_address, fqdn, hostname))
        addn_hosts = self.get_conf_file_name('addn_hosts')
        file_utils.replace_file(addn_hosts, buf.getvalue())
        return addn_hosts

    def _output_opts_file(self):
        """Write a dnsmasq compatible options file."""
        options, subnet_index_map = self._generate_opts_per_subnet()
        options += self._generate_opts_per_port(subnet_index_map)

        name = self.get_conf_file_name('opts')
        file_utils.replace_file(name, '\n'.join(options))
        return name

    def _generate_opts_per_subnet(self):
        options = []
        subnet_index_map = {}
        if self.conf.enable_isolated_metadata or self.conf.force_metadata:
            subnet_to_interface_ip = self._make_subnet_interface_ip_map()
        isolated_subnets = self.get_isolated_subnets(self.network)
        for i, subnet in enumerate(self._get_all_subnets(self.network)):
            addr_mode = getattr(subnet, 'ipv6_address_mode', None)
            segment_id = getattr(subnet, 'segment_id', None)
            if (not subnet.enable_dhcp or
                (subnet.ip_version == 6 and
                 addr_mode == constants.IPV6_SLAAC)):
                continue
            if subnet.dns_nameservers:
                if ((subnet.ip_version == 4 and
                     subnet.dns_nameservers == ['0.0.0.0']) or
                    (subnet.ip_version == 6 and
                     subnet.dns_nameservers == ['::'])):
                    # Special case: Do not announce DNS servers
                    options.append(
                        self._format_option(
                            subnet.ip_version, i, 'dns-server'))
                else:
                    options.append(
                        self._format_option(
                            subnet.ip_version, i, 'dns-server',
                            ','.join(
                                Dnsmasq._convert_to_literal_addrs(
                                    subnet.ip_version,
                                    subnet.dns_nameservers))))
            else:
                # use the dnsmasq ip as nameservers only if there is no
                # dns-server submitted by the server
                subnet_index_map[subnet.id] = i

            if self.conf.dns_domain and subnet.ip_version == 6:
                options.append('tag:tag%s,option6:domain-search,%s' %
                               (i, ''.join(self.conf.dns_domain)))

            gateway = subnet.gateway_ip
            host_routes = []
            for hr in subnet.host_routes:
                if hr.destination == constants.IPv4_ANY:
                    if not gateway:
                        gateway = hr.nexthop
                else:
                    host_routes.append("%s,%s" % (hr.destination, hr.nexthop))

            # Add host routes for isolated network segments

            if ((self.conf.force_metadata or
                 (isolated_subnets[subnet.id] and
                     self.conf.enable_isolated_metadata)) and
                    subnet.ip_version == 4):
                subnet_dhcp_ip = subnet_to_interface_ip[subnet.id]
                host_routes.append(
                    '%s/32,%s' % (METADATA_DEFAULT_IP, subnet_dhcp_ip)
                )
            elif not isolated_subnets[subnet.id] and gateway:
                host_routes.append(
                    '%s/32,%s' % (METADATA_DEFAULT_IP, gateway)
                )

            if subnet.ip_version == 4:
                for s in self._get_all_subnets(self.network):
                    sub_segment_id = getattr(s, 'segment_id', None)
                    if (s.ip_version == 4 and
                            s.cidr != subnet.cidr and
                            sub_segment_id == segment_id):
                        host_routes.append("%s,0.0.0.0" % s.cidr)

                if host_routes:
                    if gateway:
                        host_routes.append("%s,%s" % (constants.IPv4_ANY,
                                                      gateway))
                    options.append(
                        self._format_option(subnet.ip_version, i,
                                            'classless-static-route',
                                            ','.join(host_routes)))
                    options.append(
                        self._format_option(subnet.ip_version, i,
                                            WIN2k3_STATIC_DNS,
                                            ','.join(host_routes)))

                if gateway:
                    options.append(self._format_option(subnet.ip_version,
                                                       i, 'router',
                                                       gateway))
                else:
                    options.append(self._format_option(subnet.ip_version,
                                                       i, 'router'))
        return options, subnet_index_map

    def _generate_opts_per_port(self, subnet_index_map):
        options = []
        dhcp_ips = collections.defaultdict(list)
        for port in self.network.ports:
            if self._get_port_extra_dhcp_opts(port):
                port_ip_versions = set(
                    [netaddr.IPAddress(ip.ip_address).version
                     for ip in port.fixed_ips])
                for opt in port.extra_dhcp_opts:
                    if opt.opt_name == edo_ext.DHCP_OPT_CLIENT_ID:
                        continue
                    opt_ip_version = opt.ip_version
                    if opt_ip_version in port_ip_versions:
                        options.append(
                            self._format_option(opt_ip_version, port.id,
                                                opt.opt_name, opt.opt_value))
                    else:
                        LOG.info("Cannot apply dhcp option %(opt)s "
                                 "because it's ip_version %(version)d "
                                 "is not in port's address IP versions",
                                 {'opt': opt.opt_name,
                                  'version': opt_ip_version})

            # provides all dnsmasq ip as dns-server if there is more than
            # one dnsmasq for a subnet and there is no dns-server submitted
            # by the server
            if port.device_owner == constants.DEVICE_OWNER_DHCP:
                for ip in port.fixed_ips:
                    i = subnet_index_map.get(ip.subnet_id)
                    if i is None:
                        continue
                    dhcp_ips[i].append(ip.ip_address)

        for i, ips in dhcp_ips.items():
            for ip_version in (4, 6):
                vx_ips = [ip for ip in ips
                          if netaddr.IPAddress(ip).version == ip_version]
                if len(vx_ips) > 1:
                    options.append(
                        self._format_option(
                            ip_version, i, 'dns-server',
                            ','.join(
                                Dnsmasq._convert_to_literal_addrs(ip_version,
                                                                  vx_ips))))
        return options

    def _make_subnet_interface_ip_map(self):
        ip_dev = ip_lib.IPDevice(self.interface_name,
                                 namespace=self.network.namespace)

        subnet_lookup = dict(
            (netaddr.IPNetwork(subnet.cidr), subnet.id)
            for subnet in self.network.subnets
        )

        retval = {}

        for addr in ip_dev.addr.list():
            ip_net = netaddr.IPNetwork(addr['cidr'])

            if ip_net in subnet_lookup:
                retval[subnet_lookup[ip_net]] = addr['cidr'].split('/')[0]

        return retval

    def _format_option(self, ip_version, tag, option, *args):
        """Format DHCP option by option name or code."""
        option = str(option)
        pattern = "(tag:(.*),)?(.*)$"
        matches = re.match(pattern, option)
        extra_tag = matches.groups()[0]
        option = matches.groups()[2]

        if isinstance(tag, int):
            tag = self._TAG_PREFIX % tag

        if not option.isdigit():
            if ip_version == 4:
                option = 'option:%s' % option
            else:
                option = 'option6:%s' % option
        if extra_tag:
            tags = ('tag:' + tag, extra_tag[:-1], '%s' % option)
        else:
            tags = ('tag:' + tag, '%s' % option)
        return ','.join(tags + args)

    @staticmethod
    def _convert_to_literal_addrs(ip_version, ips):
        if ip_version == 4:
            return ips
        return ['[' + ip + ']' for ip in ips]

    @classmethod
    def get_isolated_subnets(cls, network):
        """Returns a dict indicating whether or not a subnet is isolated

        A subnet is considered non-isolated if there is a port connected to
        the subnet, and the port's ip address matches that of the subnet's
        gateway. The port must be owned by a neutron router.
        """
        isolated_subnets = collections.defaultdict(lambda: True)
        all_subnets = cls._get_all_subnets(network)
        subnets = dict((subnet.id, subnet) for subnet in all_subnets)

        for port in network.ports:
            if port.device_owner not in constants.ROUTER_INTERFACE_OWNERS:
                continue
            for alloc in port.fixed_ips:
                if (alloc.subnet_id in subnets and
                    subnets[alloc.subnet_id].gateway_ip == alloc.ip_address):
                    isolated_subnets[alloc.subnet_id] = False

        return isolated_subnets

    @staticmethod
    def has_metadata_subnet(subnets):
        """Check if the subnets has a metadata subnet."""
        meta_cidr = netaddr.IPNetwork(METADATA_DEFAULT_CIDR)
        if any(netaddr.IPNetwork(s.cidr) in meta_cidr
               for s in subnets):
            return True
        return False

    @classmethod
    def should_enable_metadata(cls, conf, network):
        """Determine whether the metadata proxy is needed for a network

        This method returns True for truly isolated networks (ie: not attached
        to a router) when enable_isolated_metadata is True, or for all the
        networks when the force_metadata flags is True.

        This method also returns True when enable_metadata_network is True,
        and the network passed as a parameter has a subnet in the link-local
        CIDR, thus characterizing it as a "metadata" network. The metadata
        network is used by solutions which do not leverage the l3 agent for
        providing access to the metadata service via logical routers built
        with 3rd party backends.
        """
        # Only IPv4 subnets, with dhcp enabled, will use the metadata proxy.
        all_subnets = cls._get_all_subnets(network)
        v4_dhcp_subnets = [s for s in all_subnets
                           if s.ip_version == 4 and s.enable_dhcp]
        if not v4_dhcp_subnets:
            return False

        if conf.force_metadata:
            return True

        if not conf.enable_isolated_metadata:
            return False

        if (conf.enable_metadata_network and
            cls.has_metadata_subnet(all_subnets)):
            return True

        isolated_subnets = cls.get_isolated_subnets(network)
        return any(isolated_subnets[s.id] for s in v4_dhcp_subnets)


class DeviceManager(object):

    def __init__(self, conf, plugin):
        self.conf = conf
        self.plugin = plugin
        self.driver = agent_common_utils.load_interface_driver(conf)

    def get_interface_name(self, network, port):
        """Return interface(device) name for use by the DHCP process."""
        return self.driver.get_device_name(port)

    def get_device_id(self, network):
        """Return a unique DHCP device ID for this host on the network."""
        # There could be more than one dhcp server per network, so create
        # a device id that combines host and network ids
        return common_utils.get_dhcp_agent_device_id(network.id,
                                                     self.conf.host)

    def _set_default_route_ip_version(self, network, device_name, ip_version):
        device = ip_lib.IPDevice(device_name, namespace=network.namespace)
        gateway = device.route.get_gateway(ip_version=ip_version)
        if gateway:
            gateway = gateway.get('gateway')

        for subnet in network.subnets:
            skip_subnet = (
                subnet.ip_version != ip_version
                or not subnet.enable_dhcp
                or subnet.gateway_ip is None)

            if skip_subnet:
                continue

            if subnet.ip_version == constants.IP_VERSION_6:
                # This is duplicating some of the API checks already done,
                # but some of the functional tests call directly
                prefixlen = netaddr.IPNetwork(subnet.cidr).prefixlen
                if prefixlen == 0 or prefixlen > 126:
                    continue
                modes = [constants.IPV6_SLAAC, constants.DHCPV6_STATELESS]
                addr_mode = getattr(subnet, 'ipv6_address_mode', None)
                ra_mode = getattr(subnet, 'ipv6_ra_mode', None)
                if (prefixlen != 64 and
                        (addr_mode in modes or ra_mode in modes)):
                    continue

            if gateway != subnet.gateway_ip:
                LOG.debug('Setting IPv%(version)s gateway for dhcp netns '
                          'on net %(n)s to %(ip)s',
                          {'n': network.id, 'ip': subnet.gateway_ip,
                           'version': ip_version})

                # Check for and remove the on-link route for the old
                # gateway being replaced, if it is outside the subnet
                is_old_gateway_not_in_subnet = (gateway and
                                                not ipam_utils.check_subnet_ip(
                                                        subnet.cidr, gateway))
                if is_old_gateway_not_in_subnet:
                    onlink = device.route.list_onlink_routes(ip_version)
                    existing_onlink_routes = set(r['cidr'] for r in onlink)
                    if gateway in existing_onlink_routes:
                        device.route.delete_route(gateway, scope='link')

                is_new_gateway_not_in_subnet = (subnet.gateway_ip and
                                                not ipam_utils.check_subnet_ip(
                                                        subnet.cidr,
                                                        subnet.gateway_ip))
                if is_new_gateway_not_in_subnet:
                    device.route.add_route(subnet.gateway_ip, scope='link')
                device.route.add_gateway(subnet.gateway_ip)

            return

        # No subnets on the network have a valid gateway.  Clean it up to avoid
        # confusion from seeing an invalid gateway here.
        if gateway is not None:
            LOG.debug('Removing IPv%(version)s gateway for dhcp netns on '
                      'net %(n)s',
                      {'n': network.id, 'version': ip_version})

            device.route.delete_gateway(gateway)

    def _set_default_route(self, network, device_name):
        """Sets the default gateway for this dhcp namespace.

        This method is idempotent and will only adjust the route if adjusting
        it would change it from what it already is.  This makes it safe to call
        and avoids unnecessary perturbation of the system.
        """
        for ip_version in (constants.IP_VERSION_4, constants.IP_VERSION_6):
            self._set_default_route_ip_version(network, device_name,
                                               ip_version)

    def _setup_existing_dhcp_port(self, network, device_id, dhcp_subnets):
        """Set up the existing DHCP port, if there is one."""

        # To avoid pylint thinking that port might be undefined after
        # the following loop...
        port = None

        # Look for an existing DHCP port for this network.
        for port in network.ports:
            port_device_id = getattr(port, 'device_id', None)
            if port_device_id == device_id:
                # If using gateway IPs on this port, we can skip the
                # following code, whose purpose is just to review and
                # update the Neutron-allocated IP addresses for the
                # port.
                if self.driver.use_gateway_ips:
                    return port
                # Otherwise break out, as we now have the DHCP port
                # whose subnets and addresses we need to review.
                break
        else:
            return None

        # Compare what the subnets should be against what is already
        # on the port.
        dhcp_enabled_subnet_ids = set(dhcp_subnets)
        port_subnet_ids = set(ip.subnet_id for ip in port.fixed_ips)

        # If those differ, we need to call update.
        if dhcp_enabled_subnet_ids != port_subnet_ids:
            # Collect the subnets and fixed IPs that the port already
            # has, for subnets that are still in the DHCP-enabled set.
            wanted_fixed_ips = []
            for fixed_ip in port.fixed_ips:
                if fixed_ip.subnet_id in dhcp_enabled_subnet_ids:
                    wanted_fixed_ips.append(
                        {'subnet_id': fixed_ip.subnet_id,
                         'ip_address': fixed_ip.ip_address})

            # Add subnet IDs for new DHCP-enabled subnets.
            wanted_fixed_ips.extend(
                dict(subnet_id=s)
                for s in dhcp_enabled_subnet_ids - port_subnet_ids)

            # Update the port to have the calculated subnets and fixed
            # IPs.  The Neutron server will allocate a fresh IP for
            # each subnet that doesn't already have one.
            port = self.plugin.update_dhcp_port(
                port.id,
                {'port': {'network_id': network.id,
                          'fixed_ips': wanted_fixed_ips}})
            if not port:
                raise exceptions.Conflict()

        return port

    def _setup_reserved_dhcp_port(self, network, device_id, dhcp_subnets):
        """Setup the reserved DHCP port, if there is one."""
        LOG.debug('DHCP port %(device_id)s on network %(network_id)s'
                  ' does not yet exist. Checking for a reserved port.',
                  {'device_id': device_id, 'network_id': network.id})
        for port in network.ports:
            port_device_id = getattr(port, 'device_id', None)
            if port_device_id == constants.DEVICE_ID_RESERVED_DHCP_PORT:
                try:
                    port = self.plugin.update_dhcp_port(
                        port.id, {'port': {'network_id': network.id,
                                           'device_id': device_id}})
                except oslo_messaging.RemoteError as e:
                    if e.exc_type == 'DhcpPortInUse':
                        LOG.info("Skipping DHCP port %s as it is "
                                 "already in use", port.id)
                        continue
                    raise
                if port:
                    return port

    def _setup_new_dhcp_port(self, network, device_id, dhcp_subnets):
        """Create and set up new DHCP port for the specified network."""
        LOG.debug('DHCP port %(device_id)s on network %(network_id)s'
                  ' does not yet exist. Creating new one.',
                  {'device_id': device_id, 'network_id': network.id})

        # Make a list of the subnets that need a unique IP address for
        # this DHCP port.
        if self.driver.use_gateway_ips:
            unique_ip_subnets = []
        else:
            unique_ip_subnets = [dict(subnet_id=s) for s in dhcp_subnets]

        port_dict = dict(
            name='',
            admin_state_up=True,
            device_id=device_id,
            network_id=network.id,
            tenant_id=network.tenant_id,
            fixed_ips=unique_ip_subnets)
        return self.plugin.create_dhcp_port({'port': port_dict})

    def setup_dhcp_port(self, network):
        """Create/update DHCP port for the host if needed and return port."""

        # The ID that the DHCP port will have (or already has).
        device_id = self.get_device_id(network)

        # Get the set of DHCP-enabled local subnets on this network.
        dhcp_subnets = {subnet.id: subnet for subnet in network.subnets
                        if subnet.enable_dhcp}

        # There are 3 cases: either the DHCP port already exists (but
        # might need to be updated for a changed set of subnets); or
        # some other code has already prepared a 'reserved' DHCP port,
        # and we just need to adopt that; or we need to create a new
        # DHCP port.  Try each of those in turn until we have a DHCP
        # port.
        for setup_method in (self._setup_existing_dhcp_port,
                             self._setup_reserved_dhcp_port,
                             self._setup_new_dhcp_port):
            dhcp_port = setup_method(network, device_id, dhcp_subnets)
            if dhcp_port:
                break
        else:
            raise exceptions.Conflict()

        # FIXME(kevinbenton): ensure we have the IPs we actually need.
        # can be removed once bug/1627480 is fixed
        if not self.driver.use_gateway_ips:
            expected = set(dhcp_subnets)
            actual = {fip.subnet_id for fip in dhcp_port.fixed_ips}
            missing = expected - actual
            if missing:
                LOG.debug("Requested DHCP port with IPs on subnets "
                          "%(expected)s but only got IPs on subnets "
                          "%(actual)s.", {'expected': expected,
                                          'actual': actual})
                raise exceptions.SubnetMismatchForPort(
                    port_id=dhcp_port.id, subnet_id=list(missing)[0])
        # Convert subnet_id to subnet dict
        fixed_ips = [dict(subnet_id=fixed_ip.subnet_id,
                          ip_address=fixed_ip.ip_address,
                          subnet=dhcp_subnets[fixed_ip.subnet_id])
                     for fixed_ip in dhcp_port.fixed_ips
                     # we don't care about any ips on subnets irrelevant
                     # to us (e.g. auto ipv6 addresses)
                     if fixed_ip.subnet_id in dhcp_subnets]

        ips = [DictModel(item) if isinstance(item, dict) else item
               for item in fixed_ips]
        dhcp_port.fixed_ips = ips

        return dhcp_port

    def _update_dhcp_port(self, network, port):
        for index in range(len(network.ports)):
            if network.ports[index].id == port.id:
                network.ports[index] = port
                break
        else:
            network.ports.append(port)

    def _cleanup_stale_devices(self, network, dhcp_port):
        """Unplug any devices found in the namespace except for dhcp_port."""
        LOG.debug("Cleaning stale devices for network %s", network.id)
        skip_dev_name = (self.driver.get_device_name(dhcp_port)
                         if dhcp_port else None)
        ns_ip = ip_lib.IPWrapper(namespace=network.namespace)
        if not ns_ip.netns.exists(network.namespace):
            return
        for d in ns_ip.get_devices():
            # delete all devices except current active DHCP port device
            if d.name != skip_dev_name:
                LOG.debug("Found stale device %s, deleting", d.name)
                try:
                    self.unplug(d.name, network)
                except Exception:
                    LOG.exception("Exception during stale "
                                  "dhcp device cleanup")

    def plug(self, network, port, interface_name):
        """Plug device settings for the network's DHCP on this host."""
        self.driver.plug(network.id,
                         port.id,
                         interface_name,
                         port.mac_address,
                         namespace=network.namespace,
                         mtu=network.get('mtu'))

    def setup(self, network):
        """Create and initialize a device for network's DHCP on this host."""
        try:
            port = self.setup_dhcp_port(network)
        except Exception:
            with excutils.save_and_reraise_exception():
                # clear everything out so we don't leave dangling interfaces
                # if setup never succeeds in the future.
                self._cleanup_stale_devices(network, dhcp_port=None)
        self._update_dhcp_port(network, port)
        interface_name = self.get_interface_name(network, port)

        # Disable acceptance of RAs in the namespace so we don't
        # auto-configure an IPv6 address since we explicitly configure
        # them on the device.  This must be done before any interfaces
        # are plugged since it could receive an RA by the time
        # plug() returns, so we have to create the namespace first.
        # It must also be done in the case there is an existing IPv6
        # address here created via SLAAC, since it will be deleted
        # and added back statically in the call to init_l3() below.
        if network.namespace:
            ip_lib.IPWrapper().ensure_namespace(network.namespace)
        if ipv6_utils.is_enabled_and_bind_by_default():
            self.driver.configure_ipv6_ra(network.namespace, 'default',
                                          n_const.ACCEPT_RA_DISABLED)

        if ip_lib.ensure_device_is_ready(interface_name,
                                         namespace=network.namespace):
            LOG.debug('Reusing existing device: %s.', interface_name)
            # force mtu on the port for in case it was changed for the network
            mtu = getattr(network, 'mtu', 0)
            if mtu:
                self.driver.set_mtu(interface_name, mtu,
                                    namespace=network.namespace)
        else:
            try:
                self.plug(network, port, interface_name)
            except Exception:
                with excutils.save_and_reraise_exception():
                    LOG.exception('Unable to plug DHCP port for '
                                  'network %s. Releasing port.',
                                  network.id)
                    # We should unplug the interface in bridge side.
                    self.unplug(interface_name, network)
                    self.plugin.release_dhcp_port(network.id, port.device_id)

            self.fill_dhcp_udp_checksums(namespace=network.namespace)
        ip_cidrs = []
        for fixed_ip in port.fixed_ips:
            subnet = fixed_ip.subnet
            net = netaddr.IPNetwork(subnet.cidr)
            ip_cidr = '%s/%s' % (fixed_ip.ip_address, net.prefixlen)
            ip_cidrs.append(ip_cidr)

        if self.driver.use_gateway_ips:
            # For each DHCP-enabled subnet, add that subnet's gateway
            # IP address to the Linux device for the DHCP port.
            for subnet in network.subnets:
                if not subnet.enable_dhcp:
                    continue
                gateway = subnet.gateway_ip
                if gateway:
                    net = netaddr.IPNetwork(subnet.cidr)
                    ip_cidrs.append('%s/%s' % (gateway, net.prefixlen))

        if self.conf.force_metadata or self.conf.enable_isolated_metadata:
            ip_cidrs.append(METADATA_DEFAULT_CIDR)

        self.driver.init_l3(interface_name, ip_cidrs,
                            namespace=network.namespace)

        self._set_default_route(network, interface_name)
        self._cleanup_stale_devices(network, port)

        return interface_name

    def update(self, network, device_name):
        """Update device settings for the network's DHCP on this host."""
        self._set_default_route(network, device_name)

    def unplug(self, device_name, network):
        """Unplug device settings for the network's DHCP on this host."""
        self.driver.unplug(device_name, namespace=network.namespace)

    def destroy(self, network, device_name):
        """Destroy the device used for the network's DHCP on this host."""
        if device_name:
            self.unplug(device_name, network)
        else:
            LOG.debug('No interface exists for network %s', network.id)

        self.plugin.release_dhcp_port(network.id,
                                      self.get_device_id(network))

    def fill_dhcp_udp_checksums(self, namespace):
        """Ensure DHCP reply packets always have correct UDP checksums."""
        iptables_mgr = iptables_manager.IptablesManager(use_ipv6=False,
                                                        namespace=namespace)
        ipv4_rule = ('-p udp -m udp --dport %d -j CHECKSUM --checksum-fill'
                     % constants.DHCP_RESPONSE_PORT)
        iptables_mgr.ipv4['mangle'].add_rule('POSTROUTING', ipv4_rule)
        iptables_mgr.apply()
