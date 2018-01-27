# -*- coding: utf-8 -*-
# A class representing the contents of /etc/network/interfaces
from __future__ import print_function, with_statement, absolute_import
from .adapter import NetworkAdapter


class InterfacesReader(object):
    """ Short lived class to read interfaces file """

    def __init__(self, interfaces_path):
        self._interfaces_path = interfaces_path
        self._reset()
        self._header_comments = ''

    @property
    def adapters(self):
        return self._adapters

    @property
    def header_comments(self):
        return self._header_comments

    def parse_interfaces(self, read_comments=False):
        """ Read /etc/network/interfaces (or specified file).
            Save adapters
            Return an array of networkAdapter instances.
        """
        self._reset()
        self._read_lines()

        for entry in self._auto_list:
            for adapter in self._adapters:
                if adapter.attributes['name'] == entry:
                    adapter.setAuto(True)

        for entry in self._hotplug_list:
            for adapter in self._adapters:
                if adapter.attributes['name'] == entry:
                    adapter.setHotplug(True)

        return self._adapters

    def _read_lines(self):
        # Open up the interfaces file. Read only.
        with open(self._interfaces_path, "r") as interfaces:
            # When the first non-comment line is parsed, header
            # comments have been read in.
            header_parsed = False
            # Loop through the interfaces file.
            for line in interfaces:
                # 1. Identify the clauses by analyzing the first
                # word of each line.
                # 2. Go to the next line if the current line is a comment.
                # line = line.strip().replace("\n", "")
                if not line:
                    pass
                elif line.strip().startswith("#") is True:
                    if not header_parsed:
                        self._header_comments += line
                else:
                    # Header comments can no longer
                    # be parsed in when the first interfaces
                    # line is parsed in.
                    header_parsed = True
                    self._parse_iface(line)
                    # Ignore blank lines.
                    if line.isspace() is True:
                        pass
                    else:
                        self._parse_details(line)
                    self._read_auto(line)
                    self._read_hotplug(line)

    def _parse_iface(self, line):
        if line.startswith('iface'):
            sline = line.split()
            # Update the self._context when an iface clause is encountered.
            self._context += 1
            self._adapters.append(NetworkAdapter(sline[1].strip()))
            self._adapters[self._context].setAddressSource(sline[-1].strip())
            self._adapters[self._context].setAddrFam(sline[2].strip())

    def _parse_details(self, line):
        if line[0].isspace() is True:
            sline = [x.strip() for x in line.split()]

            if sline[0] == 'address':
                self._adapters[self._context].setAddress(sline[1])
            elif sline[0] == 'netmask':
                self._adapters[self._context].setNetmask(sline[1])
            elif sline[0] == 'gateway':
                self._adapters[self._context].setGateway(sline[1])
            elif sline[0] == 'broadcast':
                self._adapters[self._context].setBroadcast(sline[1])
            elif sline[0] == 'network':
                self._adapters[self._context].setNetwork(sline[1])
            elif sline[0] == 'hostapd':
                self._adapters[self._context].setHostapd(sline[1])
            elif sline[0] == 'wpa-conf':
                self._adapters[self._context].setWpaConf(sline[1])
            elif sline[0] == 'dns-nameservers':
                nameservers = sline
                del nameservers[0]
                if len(nameservers) == 1:
                    nameservers = nameservers[0]
                self._adapters[self._context].setDnsNameservers(nameservers)
            elif sline[0] == 'dns-search':
                searchUri = sline
                del searchUri[0]
                self._adapters[self._context].setDnsSearch(searchUri)
            elif sline[0].startswith('bridge') is True:
                opt = sline[0].split('_')
                sline.pop(0)
                ifs = " ".join(sline)
                self._adapters[self._context].replaceBropt(opt[1], ifs)
            elif (sline[0] == 'up'
                  or sline[0] == 'down'
                  or sline[0] == 'pre-up'
                  or sline[0] == 'pre-down'
                  or sline[0] == 'post-down'):
                ud = sline.pop(0)
                cmd = ' '.join(sline)
                if ud == 'up':
                    self._adapters[self._context].appendUp(cmd)
                elif ud == 'down':
                    self._adapters[self._context].appendDown(cmd)
                elif ud == 'pre-up':
                    self._adapters[self._context].appendPreUp(cmd)
                elif ud == 'pre-down':
                    self._adapters[self._context].appendPreDown(cmd)
                elif ud == 'post-down':
                    self._adapters[self._context].appendPostDown(cmd)
            else:
                # store as if so as not to loose it
                self._adapters[self._context].setUnknown(sline[0], sline[1])

    def _read_auto(self, line):
        """ Identify which adapters are flagged auto. """
        if line.startswith('auto'):
            sline = [x.strip() for x in line.split()]
            for word in sline:
                if word == 'auto':
                    pass
                else:
                    self._auto_list.append(word)

    def _read_hotplug(self, line):
        """ Identify which adapters are flagged allow-hotplug. """
        if line.startswith('allow-hotplug'):
            sline = [x.strip() for x in line.split()]
            for word in sline:
                if word == 'allow-hotplug':
                    pass
                else:
                    self._hotplug_list.append(word)

    def _reset(self):
        # Initialize a place to store created networkAdapter objects.
        self._adapters = []

        # Keep a list of adapters that have the auto or
        # allow-hotplug flags set.
        self._auto_list = []
        self._hotplug_list = []

        # Store the interface context.
        # This is the index of the adapters collection.
        self._context = -1
