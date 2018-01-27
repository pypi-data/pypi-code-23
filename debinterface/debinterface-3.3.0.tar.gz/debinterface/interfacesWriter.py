# -*- coding: utf-8 -*-
# Write interface
from __future__ import print_function, with_statement, absolute_import
import shutil
import os
from string import Template

from . import toolutils


class InterfacesWriter(object):
    """ Short lived class to write interfaces file """

    # Define templetes for blocks used in /etc/network/interfaces.
    _auto = Template('auto $name\n')
    _hotplug = Template('allow-hotplug $name\n')
    _iface = Template('iface $name $addrFam $source\n')
    _cmd = Template('\t$varient $value\n')
    _comment = Template('# $line\n')

    _addressFields = [
        'address', 'network', 'netmask', 'broadcast',
        'gateway', 'dns-nameservers', 'dns-search'
    ]
    _prepFields = ['pre-up', 'up', 'down', 'pre-down', 'post-down']
    _bridgeFields = ['ports', 'fd', 'hello', 'maxage', 'stp', 'maxwait']
    _plugins = ['hostapd', 'wpa-conf']

    def __init__(self, adapters, interfaces_path, backup_path=None,
                 header_comment=None):
        """ if backup_path is None => no backup """
        self._adapters = adapters
        self._interfaces_path = interfaces_path
        self._backup_path = backup_path
        try:
            is_str = isinstance(header_comment, basestring)
        except NameError:
            is_str = isinstance(header_comment, str)

        if is_str:
            self._header_comment = header_comment
        else:
            self._header_comment = None

    @property
    def adapters(self):
        return self._adapters

    @adapters.setter
    def adapters(self, value):
        self._adapters = value

    def write_interfaces(self):
        # Back up the old interfaces file.
        self._backup_interfaces()

        try:
            # Prepare to write the new interfaces file.
            with toolutils.atomic_write(self._interfaces_path) as interfaces:
                # Write any header comments.
                self._write_header_comment(interfaces)
                # Loop through the provided networkAdaprers and
                # write the new file.
                for adapter in self._adapters:
                    # Get dict of details about the adapter.
                    self._write_adapter(interfaces, adapter)
            self._check_interfaces(self._interfaces_path)
        except Exception:
            # Any error, let's roll back
            self._restore_interfaces()
            raise

    def _check_interfaces(self, interfaces_path):
        """Uses ifup to check interfaces file. If it is not in the
            default place, each interface must be checked one by one.

            Args:
                interfaces_path (string) : the path to interfaces file

            Raises:
                ValueError : if invalid network interfaces
        """
        ret = False
        output = ""
        if not self._adapters:
            return

        if interfaces_path == "/etc/network/interfaces":
            ret, output = toolutils.safe_subprocess([
                "/sbin/ifup", "-a", "--no-act"
            ])
        else:
            for adapter in self._adapters:
                ret, output = toolutils.safe_subprocess([
                    "/sbin/ifup", "--no-act",
                    "--interfaces={0}".format(interfaces_path),
                    adapter.attributes["name"]
                ])
                if not ret:
                    break
        if not ret:
            raise ValueError("Invalid network interfaces file "
                             "written to disk, restoring to previous "
                             "one : {0}".format(output))

    def _write_header_comment(self, interfaces):
        if self._header_comment:
            for line in self._header_comment.split('\n'):
                # Check the beginning of the line for a comment field
                # if it does not exist, add it.
                if line[:2] != "# ":
                    line = self._comment.substitute(line=line)
                else:
                    # split strips the newline, add it back
                    line = line + '\n'
                interfaces.write(line)

            # Create a blank line between comment and start of interfaces
            interfaces.write('\n')

    def _write_adapter(self, interfaces, adapter):
        try:
            adapter.validateAll()
        except ValueError as e:
            print(repr(e))
            raise

        ifAttributes = adapter.export()

        self._write_auto(interfaces, adapter, ifAttributes)
        self._write_hotplug(interfaces, adapter, ifAttributes)
        self._write_addrFam(interfaces, adapter, ifAttributes)
        self._write_addressing(interfaces, adapter, ifAttributes)
        self._write_bridge(interfaces, adapter, ifAttributes)
        self._write_plugins(interfaces, adapter, ifAttributes)
        self._write_callbacks(interfaces, adapter, ifAttributes)
        self._write_unknown(interfaces, adapter, ifAttributes)
        interfaces.write("\n")

    def _write_auto(self, interfaces, adapter, ifAttributes):
        """ Write if applicable """
        try:
            if adapter.attributes['auto'] is True:
                d = dict(name=ifAttributes['name'])
                interfaces.write(self._auto.substitute(d))
        except KeyError:
            pass

    def _write_hotplug(self, interfaces, adapter, ifAttributes):
        """ Write if applicable """
        try:
            if ifAttributes['hotplug'] is True:
                d = dict(name=ifAttributes['name'])
                interfaces.write(self._hotplug.substitute(d))
        except KeyError:
            pass

    def _write_addrFam(self, interfaces, adapter, ifAttributes):
        """ Construct and write the iface declaration.
            The addrFam clause needs a little more processing.
        """
        # Write the source clause.
        # Will not error if omitted. Maybe not the best plan.
        try:
            if (not ifAttributes["name"]
                    or not ifAttributes["addrFam"]
                    or not ifAttributes["source"]):
                raise ValueError("Invalid field content")
            d = dict(name=ifAttributes['name'],
                     addrFam=ifAttributes['addrFam'],
                     source=ifAttributes['source'])
            interfaces.write(self._iface.substitute(d))
        except KeyError:
            pass

    def _write_addressing(self, interfaces, adapter, ifAttributes):
        for field in self._addressFields:
            try:
                value = ifAttributes[field]
                if value and value != 'None':
                    if isinstance(value, list):
                        d = dict(varient=field,
                                 value=" ".join(ifAttributes[field]))
                    else:
                        d = dict(varient=field, value=ifAttributes[field])
                    interfaces.write(self._cmd.substitute(d))
            # Keep going if a field isn't provided.
            except KeyError:
                pass

    def _write_bridge(self, interfaces, adapter, ifAttributes):
        """ Write the bridge information. """
        for field in self._bridgeFields:
            try:
                value = ifAttributes['bridge-opts'][field]
                if value and value != 'None':
                    d = dict(varient="bridge_" + field, value=value)
                    interfaces.write(self._cmd.substitute(d))
            # Keep going if a field isn't provided.
            except KeyError:
                pass

    def _write_callbacks(self, interfaces, adapter, ifAttributes):
        """ Write the up, down, pre-up, and post-down clauses. """
        for field in self._prepFields:
            try:
                for item in ifAttributes[field]:
                    if item and item != 'None':
                        d = dict(varient=field, value=item)
                        interfaces.write(self._cmd.substitute(d))
            except KeyError:
                # Keep going if a field isn't provided.
                pass

    def _write_plugins(self, interfaces, adapter, ifAttributes):
        """ Write plugins options, currently hostapd. """
        for field in self._plugins:
            try:
                if field in ifAttributes and ifAttributes[field] != 'None':
                    d = dict(varient=field, value=ifAttributes[field])
                    interfaces.write(self._cmd.substitute(d))
            # Keep going if a field isn't provided.
            except KeyError:
                pass

    def _write_unknown(self, interfaces, adapter, ifAttributes):
        """ Write unknowns options """
        try:
            for k, v in ifAttributes['unknown'].items():
                if v:
                    d = dict(varient=k, value=str(v))
                    interfaces.write(self._cmd.substitute(d))
        except (KeyError, ValueError):
            pass

    def _backup_interfaces(self):
        """Backup interfaces file is the file exists

            Returns:
                True/False, command output

            Raises:
                IOError : if the copy fails and the source file exists
        """

        try:
            if self._backup_path:
                shutil.copy(self._interfaces_path, self._backup_path)
        except IOError as ex:
            # Only raise if source actually exists
            if os.path.exists(self._interfaces_path):
                raise ex

    def _restore_interfaces(self):
        """Restore interfaces file is the file exists

            Returns:
                True/False, command output

            Raises:
                IOError : if the copy fails and the source file exists
        """

        try:
            if self._backup_path:
                shutil.copy(self._backup_path, self._interfaces_path)
        except IOError as ex:
            # Only raise if source actually exists
            if os.path.exists(self._backup_path):
                raise ex
