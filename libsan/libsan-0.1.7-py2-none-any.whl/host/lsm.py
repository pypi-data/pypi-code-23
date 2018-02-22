# Copyright (C) 2016 Red Hat, Inc.
# This file is part of libsan.
#
# libsan is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# libsan is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with libsan.  If not, see <http://www.gnu.org/licenses/>.

"""lsm.py: Module to manipulate libstoragemgmt userspace package."""

__author__ = "Jakub Krysl"
__copyright__ = "Copyright (c) 2017 Red Hat, Inc. All rights reserved."

import re  # regex
import os
import stat
from libsan.host.cmdline import run
from libsan.host.linux import dist_ver, install_package
from types import FunctionType

def _print(string):
    module_name = __name__
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    string = re.sub("DEBUG:", "DEBUG:(" + module_name + ") ", string)
    print(string)
    if "FATAL:" in string:
        raise RuntimeError(string)
    return


class LibStorageMgmt:
    def __init__(self, username=None, password=None, target=None, protocol=None):
        if dist_ver() < 7:
            _print("FATAL: libstoragemgmt is not supported on RHEL < 7.")

        self.username = None
        self.password = None
        self.target = None
        self.protocol = None
        self.port = None
        self.query_params = None
        self.timeout = None

        # persistent previous values
        self.previous_sys_read_pct = {}
        self.previous_phy_disk_cache_policy = {}
        self.previous_read_cache_policy = {}
        self.previous_write_cache_policy = {}
        self.previous_local_disk_ident_led = {}
        self.previous_local_disk_fault_led = {}

        # local target does not require anything of this and megaraid/sim needs only protocol
        if username and password and target and protocol:
            self.username = username
            self.password = password
            self.target = target
            self.protocol = protocol
        elif protocol and "megaraid" in protocol or "sim" in protocol:
            self.protocol = protocol

        if self.password:
            os.environ["LSMCLI_PASSWORD"] = self.password
            _print("INFO: Password set")
        else:
            if os.environ.get("LSMCLI_PASSWORD"):
                del os.environ["LSMCLI_PASSWORD"]
                _print("INFO: Password cleaned")

        # stop if can't install lsm package
        if not install_package("libstoragemgmt"):
            _print("FATAL: Could not install libstoragemgmt package")

        if self.protocol == "smispy":
            self.port = "5988"
            self.query_params = "?namespace=root/emc"
        if self.protocol == "smispy+ssl":
            # ssl uses different port
            self.port = "5989"
            # ignore missing ssl certificate
            self.query_params = "&no_ssl_verify=yes"

        # install protocol specific packages
        if self.protocol:
            if "ontap" in self.protocol:
                if not install_package("libstoragemgmt-netapp-plugin"):
                    _print("FATAL: Could not install LSM NetApp plugin")
            elif "smispy" in self.protocol:
                if not install_package("libstoragemgmt-smis-plugin"):
                    _print("FATAL: Could not install LSM SMIS plugin")
            elif "targetd" in self.protocol:
                if not install_package("libstoragemgmt-targetd-plugin"):
                    _print("FATAL: Could not install LSM targetd plugin")
            elif "megaraid" in self.protocol:
                if not install_package("libstoragemgmt-megaraid-plugin"):
                    _print("FATAL: Could not install LSM megaraid plugin")
                # needs to install 3rd party tool
                if not install_package("storcli"):
                    _print("FATAL: Could not install storcli")

        if run("service libstoragemgmt restart", verbose=True) != 0:
            _print("FATAL: Could not restart libstoragemgmt service")

        _print("INFO: LSM configured")

    def _run_cmd(self, cmd, return_output=False, verbose=True, force_flush=False):
        # construct the run command with right target
        run_cmd = "lsmcli "
        if self.timeout:
            run_cmd += "-w %s " % self.timeout
        if self.protocol:
            run_cmd += "-u \"%s://" % self.protocol
            if self.username and self.target:
                run_cmd += "%s@%s" % (self.username, self.target)
            if self.port:
                run_cmd += ":%s" % self.port
            if self.query_params:
                run_cmd += "%s" % self.query_params
            run_cmd += "\" "
        run_cmd += cmd
        _print("INFO: Running %s" % run_cmd)
        if return_output:
            retcode, data = run(cmd=run_cmd, return_output=True, verbose=verbose, force_flush=force_flush)
        else:
            retcode = run(cmd=run_cmd, return_output=False, verbose=verbose, force_flush=force_flush)
        if return_output:
            return retcode, data
        return retcode

    @staticmethod
    def _parse_data(data):
        # parse data to dict by ID (0th column)
        ids = []
        headers = []
        for i, line in enumerate(data.splitlines()):
            # remove 2nd line
            if i == 1:
                continue
            block = [x.strip() for x in line.split("|")]
            if i == 0:
                headers.extend(block)
                continue
            ids.append({})
            for j, x in enumerate(block):
                ids[i - 2][headers[j]] = block[j]
        return ids

    @staticmethod
    def _parse_data_script(data):
        ids = []
        disks = data.split(re.search(r"\S-+", data).group(0))[1:-1]
        for i, disk in enumerate(disks):
            lines = disk.splitlines()
            ids.append([])
            j = -1
            for line in lines:
                block = [x.strip() for x in line.split("|")]
                if block == ['']:
                    continue
                ids[i].append([])
                if block[0] == '':
                    if isinstance(ids[i][j][1], basestring):
                        ids[i][j][1] = [ids[i][j][1]]
                    ids[i][j][1].append(block[1])
                    continue
                else:
                    j += 1
                ids[i][j].append(block[0])
                ids[i][j].append(block[1])
            while [] in ids[i]:
                del ids[i][ids[i].index([])]
            ids[i] = dict(ids[i])
        return ids

    def _get_data(self, cmd, **kwargs):
        # return dict of {{data_ID1}, {data_ID2}}
        ret, data = cmd(return_output=True, **kwargs)
        if 'script' in kwargs and kwargs['script']:
            return self._parse_data_script(data)
        return self._parse_data(data)

    @staticmethod
    def _get_fields(data, *fields):
        ret = [[] for x in range(len(data))]
        for field in fields:
            for i, dat in enumerate(data):
                if field in dat.keys():
                    if isinstance(dat[field], list):
                        for x in range(len(dat[field])):
                            ret[i].append(dat[field][x])
                    else:
                        ret[i].append(dat[field])
                else:
                    print("FAIL: Unknown field \'%s\'." % field)
                    return []
        return ret

    def _get_id(self, possible_id, dict, id="ID", name="Name"):
        # returns ID if supplied ID or name
        fields = self._get_fields(dict, id, name)
        for field in fields:
            if field[1] == possible_id:
                return field[0]
        return possible_id

    def _is_value(self, keys, dict, *fields):
        # checks if key is a value in dict, if supplied more keys, check if they are in the same list
        data = self._get_fields(dict, *fields)
        if not isinstance(keys, list):
            for dat in data:
                if keys in dat:
                    return True
        else:
            index = []
            for i, key in enumerate(keys):
                index.append(-1)
                for j, dat in enumerate(data):
                    if key in dat:
                        index[i] = j
            if not len(set(index)) > 1:
                return True
        return False

    @staticmethod
    def _check_size_format(size, return_size=False):
        # check if requested size format is in supported formats and the rest is numbers
        try:
            if size[-3:] in ["KiB", "MiB", "GiB", "TiB", "PiB", "EiB"] and float(size[:-3]):
                if return_size:
                    return True, [size[:-3], size[-3:-2]]
                return True
            elif size[-2:] in ["KB", "MB", "GB", "TB", "PB", "EB"] and float(size[:-2]):
                if return_size:
                    return True, [size[:-2], size[-2:-1]]
                return True
            elif size[-1:].upper() in ["B", "K", "M", "G", "T", "P", "E"] and float(size[:-1]):
                if return_size:
                    return True, [size[:-1], size[-1:]]
                return True
        except ValueError:
            pass
        return False, []

    def _get_size_in_bytes(self, size):
        ret, split_size = self._check_size_format(size, return_size=True)
        multipliers = ["B", "K", "M", "G", "T", "P", "E"]
        return split_size[0] * multipliers.index(split_size[1]) * 1024

    def _get_raid_types_and_sizes(self, systems):
        max_types = ["RAID0", "RAID1", "RAID5", "RAID6", "RAID10", "RAID50", "RAID60"]
        capabilities = []
        for i, system in enumerate(systems):
            ret, data = self.volume_raid_create_cap(sys=system, return_output=True)
            capabilities.append([[],[]])
            for j, line in enumerate(data.splitlines()):
                # remove first 2 lines
                if j < 2:
                    continue
                block = line.split()
                if block[2]:
                    capabilities[i][0].append(block[2])
                if block[4]:
                    capabilities[i][1].append(block[4])
        for i, cap in enumerate(capabilities):
            min_types = [i for i in capabilities[i][0] if i.upper() in max_types]
            if i == 0:
                max_sizes = capabilities[i][1]
            else:
                max_sizes = capabilities[i][1] + max_sizes
        return tuple(min_types), tuple(max_sizes)

    def _get_systems_by_disks(self, disks):
        disk_ids = self._get_data(cmd=self.list, type="DISKS")
        systems = []
        for disk in disk_ids:
            if disk in disks:
                systems.append(disk_ids[disk]["System ID"])
        return list(set(systems))

    @staticmethod
    def _get_file_from_path(path):
        return path.split("/").pop()

    def _get_cache_info(self, vol):
        ret, data = self.volume_cache_info(vol, return_output=True)
        return self._parse_data(data)

    @staticmethod
    def _translate_write_cache_policy(policy):
        dictionary = {"Write Back": "WB",
                      "Write Through": "WT",
                      "Auto": "AUTO"}
        return dictionary[policy]

    def _get_local_disk_info(self, type):
        if type not in ["SCSI VPD 0x83", "Revolutions Per Minute", "Link Type", "Serial Number", "LED Status", "Link Speed"]:
            _print("FAIL: Unknown type requested for local disk info.")
            return {}
        disk_infos = []
        ret, data = self.local_disk_list(return_output=True, script=True)
        disks = data.split("-------------------------------------------------------------")[1:-1]
        for i, disk in enumerate(disks):
            lines = disk.splitlines()
            disk_infos.append([])
            for line in lines:
                block = [x.strip() for x in line.split("|")]
                if block[0] == "Path":
                    disk_infos[i].append(block[1])
                elif block[0] == type:
                    disk_infos[i].append(block[1])
        return dict(disk_infos)

    def _get_local_disks(self):
        ret, data = run(cmd="lsblk -o NAME -nl -d", return_output=True)
        if ret != 0:
            _print("FAIL: Could not query local disks using lsblk.")
            return []
        return data.splitlines()

    @classmethod
    def _get_methods(cls):
        methods = [x for x, y in cls.__dict__.items() if type(y) == FunctionType]
        for method in ["help", "version"]:
            methods.remove(method)
        for method in methods[:]:
            if method.startswith("_"):
                methods.remove(method)
            if method.startswith("local_disk_") and method.endswith("led"):
                methods[methods.index(method)] += "_on"
                methods.append(method + "_off")
            if method.startswith("volume_ident_") and method.endswith("led"):
                methods[methods.index(method)] += "_on"
                methods.append(method + "_off")
        return methods

    def help(self, cmd=""):
        """Retrieve help.
        The arguments are:
        \tcmd - optional | get help on this command
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        commands = self._get_methods()
        if cmd and cmd not in commands:
            _print("FAIL: Unknown command %s." % cmd)
            return False

        command = "%s -h" % cmd.replace("_", "-")
        if run(command, verbose=True) != 0:
            if cmd == "":
                cmd = "lsmcli"
            _print("FAIL: Could not get help for %s." % cmd)
            return False
        return True

    def version(self, cmd=""):
        """Retrieve plugin version.
        The arguments are:
        \tcmd - optional | get version of this command
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        commands = self._get_methods()
        if cmd and cmd not in commands:
            _print("FAIL: Unknown command %s." % cmd)
            return False

        command = "%s -v" % cmd.replace("_", "-")
        if run(command, verbose=True) != 0:
            if cmd == "":
                cmd = "lsmcli"
            _print("FAIL: Could not get version of %s." % cmd)
            return False
        return True

    def list(self, type, fs_id=None, search_by=None, return_output=False, script=False):
        """Lists info about specified type on target.
        The arguments are:
        \ttype
        \tfs_id needed only when using SNAPSHOTS type
        \tsearch_by is a list, eg: [SYS_ID, 0151753773]
        \tscript - if set to True, prints out in "script friendly way"
        Returns:
        \tTrue if success
        \tFalse in case of failure
        """
        if return_output:
            ret_fail = (False, None)
        else:
            ret_fail = False

        types = ["VOLUMES", "POOLS", "FS", "SNAPSHOTS", "EXPORTS", "NFS_CLIENT_AUTH",
                 "ACCESS_GROUPS", "SYSTEMS", "DISKS", "PLUGINS", "TARGET_PORTS", "BATTERIES"]
        if type.upper() not in types:
            _print("FAIL: Unknown type %s. Must be one of %s." % (type, ", ".join(types)))
            return ret_fail

        cmd = "list --type %s " % type.upper()

        if type.upper() == "SNAPSHOTS" and not fs_id:
            _print("FAIL: FS_ID is required when listing SNAPSHOTS.")
            return ret_fail
        elif type.upper() != "SNAPSHOTS" and fs_id:
            _print("FAIL: FS_ID can only be used when listing type SNAPSHOTS.")
            return ret_fail
        elif fs_id:
            cmd += "--fs=%s " % fs_id

        if search_by:
            if not isinstance(search_by, list) and len(search_by) != 2:
                _print("FAIL: search_by must be list of 2 elements, got %s." % search_by)
                return ret_fail
            if search_by[0].upper() == "SYS_ID":
                search_by_types = ["VOLUMES", "POOLS", "FS", "SNAPSHOTS", "DISKS", "ACCESS_GROUPS"]
                if type.upper() not in search_by_types:
                    _print("FAIL: When using search by SYS_ID, type must be one of %s." % ", "
                           .join(search_by_types))
                    return ret_fail
                cmd += "--sys %s " % search_by[1]
            elif search_by[0].upper() == "POOL_ID":
                search_by_types = ["VOLUMES", "POOLS", "FS"]
                if type.upper() not in search_by_types:
                    _print("FAIL: When using search by POOL_ID, type must be one of %s." % ", "
                           .join(search_by_types))
                    return ret_fail
                cmd += "--pool %s " % search_by[1]
            elif search_by[0].upper() == "VOL_ID":
                search_by_types = ["VOLUMES", "ACCESS_GROUPS"]
                if type.upper() not in search_by_types:
                    _print("FAIL: When using search by VOL_ID, type must be one of %s." % ", "
                           .join(search_by_types))
                    return ret_fail
                cmd += "--vol %s " % search_by[1]
            elif search_by[0].upper() == "DISK_ID":
                search_by_types = ["DISKS"]
                if type.upper() not in search_by_types:
                    _print("FAIL: When using search by DISK_ID, type must be one of %s." % ", "
                           .join(search_by_types))
                    return ret_fail
                cmd += "--disk %s " % search_by[1]
            elif search_by[0].upper() == "AG_ID":
                search_by_types = ["ACCESS_GROUPS", "VOLUMES"]
                if type.upper() not in search_by_types:
                    _print("FAIL: When using search by AG_ID, type must be one of %s." % ", "
                           .join(search_by_types))
                    return ret_fail
                cmd += "--ag %s " % search_by[1]
            elif search_by[0].upper() == "FS_ID":
                search_by_types = ["FS"]
                if type.upper() not in search_by_types:
                    _print("FAIL: When using search by FS_ID, type must be one of %s." % ", "
                           .join(search_by_types))
                    return ret_fail
                cmd += "--fs %s " % search_by[1]
            elif search_by[0].upper() == "NFS_EXPORT_ID":
                search_by_types = ["EXPORTS"]
                if type.upper() not in search_by_types:
                    _print("FAIL: When using search by NFS_EXPORT_ID, type must be one of %s." % ", "
                           .join(search_by_types))
                    return ret_fail
                cmd += "--nfs-export %s " % search_by[1]
            elif search_by[0].upper() == "TGT_ID":
                search_by_types = ["TARGET_PORTS"]
                if type.upper() not in search_by_types:
                    _print("FAIL: When using search by TGT_ID, type must be one of %s." % ", "
                           .join(search_by_types))
                    return ret_fail
                cmd += "--tgt %s " % search_by[1]
            else:
                _print("FAIL: Unknown first element in search_by. Must be one of %s." % ", "
                       .join(["SYS_ID", "POOL_ID", "VOL_ID", "DISK_ID", "AG_ID", "FS_ID", "NFS_EXPORT_ID", "TGT_ID"]))
                return ret_fail

        if script:
            cmd += "-s "

        if return_output:
            retcode, data = self._run_cmd(cmd, return_output=True)
        else:
            retcode = self._run_cmd(cmd)
        if retcode != 0:
            _print("FAIL: Could not list %s" % type)
            return ret_fail

        if return_output:
            return True, data
        return True

    def job_status(self, job_id):
        """Retrieve information about a job.  Please see user guide on how to use.
        The arguments are:
        \tjob_id - ID of job to get information about
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "job_status --job=%s" % job_id
        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not get status on job %s" % job_id)
            return False
        return True

    def capabilities(self, sys):
        """Retrieves array capabilities.
        The arguments are:
        \tsys - ID/name of system to query for capabilities
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        sys_data = self._get_data(cmd=self.list, type="SYSTEMS")
        if not self._is_value(sys, sys_data, "ID", "Name"):
            _print("FAIL: Could not find specified sys %s." % sys)
            return False

        sys_id = self._get_id(sys, sys_data)

        cmd = "capabilities --sys=%s" % sys_id
        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not get get capabilities of system %s" % sys)
            return False
        return True

    def plugin_info(self, return_output=False):
        """Retrieves plugin description and version for current URI.
        The arguments are:
        \treturn_output - if set True, returns output from console
        Returns:
        \tOnly Boolean if return_output False:
        \t\tTrue if success
        \t\tFalse in case of failure
        \tBoolean and data if return_output True
        """
        if return_output:
            ret_fail = (False, None)
        else:
            ret_fail = False
        cmd = "plugin-info"

        if return_output:
            retcode, data = self._run_cmd(cmd, return_output=True)
        else:
            retcode = self._run_cmd(cmd)
        if retcode != 0:
            _print("FAIL: Could not get plugin info.")
            return ret_fail

        if return_output:
            return True, data
        return True

    def volume_create(self, name, size, pool, provisioning=None):
        """Creates a volume.
        The arguments are:
        \tname - name of new volume
        \tsize - new size, use as INT+UNIT e.g. 100MiB, 10G...
        \tpool - ID/name of pool to create volume in
        \tprovisioning - optional | provisioning  type, one of [DEFAULT, THIN, FULL]
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "volume-create "

        vol_data = self._get_data(cmd=self.list, type="VOLUMES")
        if self._is_value(name, vol_data, "Name"):
            _print("FAIL: Volume with name %s already exists." % name)
            return False
        cmd += "--name=%s " % name

        if not self._check_size_format(size):
            _print("FAIL: Unsupported size format of size %s." % size)
            return False
        cmd += "--size=%s " % size

        pool_data = self._get_data(cmd=self.list, type="POOLS")
        if not self._is_value(pool, pool_data, "ID", "Name"):
            _print("FAIL: Could not find specified pool %s." % pool)
            return False
        cmd += "--pool=%s " % self._get_id(pool, pool_data)

        if provisioning:
            allowed_provisioning = ["DEFAULT", "THIN", "FULL"]
            if provisioning.upper() not in allowed_provisioning:
                _print("FAIL: Provisioning must be one of %s." % ", ".join(allowed_provisioning))
                return False
            cmd += "--provisioning=%s" % provisioning.upper()
        # FIXME Check if the pool is thin when using THIN and if it is full when usin FULL (lvs flag)

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not create volume %s." % name)
            return False
        return True

    def volume_raid_create(self, name, raid_type, disks, strip_size):
        """Creates a volume on hardware RAID on given disks.
        The arguments are:
        \tname - name of new RAID volume
        \traid_type - must be one of [RAID0, RAID1, RAID5, RAID6, RAID10, RAID50, RAID60] and also supported
        \tdisks - list of IDs/names of disks
        \tstrip_size - optional | the  size  in  bytes of strip on each disks, must be supported by system
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "volume-raid-create "

        vol_data = self._get_data(cmd=self.list, type="VOLUMES")
        if self._is_value(name, vol_data, "Name"):
            _print("FAIL: Volume with name %s already exists." % name)
            return False
        cmd += "--name=%s " % name

        # FIXME check if system has enough free disks and also check if given disk from disks list is in free disks

        # always get a list
        if not isinstance(disks, list):
            disks = [disks]
        disk_data = self._get_data(cmd=self.list, type="DISKS")
        disk_checked_ids = []
        for disk in disks:
            if not self._is_value(disk, disk_data, "ID", "Name"):
                _print("FAIL: Could not find specified disk %s." % disk)
                return False
            disk_checked_ids.append(self._get_id(disk, disk_data))
        for disk in disk_checked_ids:
            cmd += "--disk=%s " % disk

        systems = self._get_systems_by_disks(disk_checked_ids)
        raid_capabilities, strip_sizes = self._get_raid_types_and_sizes(systems)

        if raid_type not in raid_capabilities:
            _print("FAIL: Specified raid type %s is not supported by system(s)." % raid_type)
            return False
        cmd += "--raid-type=%s " % raid_type

        if strip_size:
            if strip_size not in strip_sizes:
                _print("FAIL: Specified strip_size %s is not supported by system(s)." % strip_size)
                return False
            cmd += "--strip-size=%s" % strip_size

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not create raid volume %s." % name)
            return False
        return True

    def volume_raid_create_cap(self, sys, return_output=False):
        """Query support status of volume-raid-create command for current hardware RAID card.
        The arguments are:
        \tsys - ID/name of system
        \treturn_output - if set True, returns output from console
        Returns:
        \tOnly Boolean if return_output False:
        \t\tTrue if success
        \t\tFalse in case of failure
        \tBoolean and data if return_output True
        """
        if return_output:
            ret_fail = (False, None)
        else:
            ret_fail = False

        cmd = "volume-raid-create-cap "

        sys_data = self._get_data(cmd=self.list, type="SYSTEMS")
        if not self._is_value(sys, sys_data, "ID", "Name"):
            _print("FAIL: Could not find specified sys %s." % sys)
            return ret_fail
        sys_id = self._get_id(sys, sys_data)
        cmd += "--sys=%s " % sys_id

        if return_output:
            retcode, data = self._run_cmd(cmd, return_output=True)
        else:
            retcode = self._run_cmd(cmd)
        if retcode != 0:
            _print("FAIL: Could not get raid capabilities of system %s." % sys)
            return ret_fail

        if return_output:
            return True, data
        return True

    # FIXME: Find a way to query and safe LED previous state
    def volume_ident_led(self, vol, state):
        """Enable / disable the IDENT LEDs for all physical disks that compose a logical volume.
        The arguments are:
        \tvol - ID/name of volume
        \tstate - desired state of identification LED; could be 0/1, True/False, On/Off
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        if str(state).upper() not in ["0", "1", "FALSE", "TRUE", "OFF", "ON"]:
            _print("FAIL: State must be either 0/1, True/False or On/Off; got %s." % state)
            return False
        if str(state).upper() in ["1", "TRUE", "ON"]:
            cmd = "volume-ident-led-on "
        else:
            cmd = "volume-ident-led-off "

        vol_data = self._get_data(cmd=self.list, type="VOLUMES")
        if not self._is_value(vol, vol_data, "ID", "Name"):
            _print("FAIL: Could not find specified volume %s." % vol)
            return False
        cmd += "--vol=%s " % self._get_id(vol, vol_data)

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not turn volume ident LEDs ON on volume %s." % vol)
            return False
        return True

    def volume_delete(self, vol):
        """Deletes a volume.
        The arguments are:
        \tvol - ID/name of volume to delete
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "volume-delete -f "

        vol_data = self._get_data(cmd=self.list, type="VOLUMES")
        if not self._is_value(vol, vol_data, "ID", "Name"):
            _print("FAIL: Could not find specified volume %s." % vol)
            return False
        cmd += "--vol=%s " % self._get_id(vol, vol_data)

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not delete volume %s." % vol)
            return False
        return True

    def volume_resize(self, vol, size):
        """Re-sizes a volume.
        The arguments are:
        \tvol - ID/name of volume to resize
        \tsize - new size, use as INT+UNIT e.g. 100MiB, 10G...
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "volume-resize -f "

        vol_data = self._get_data(cmd=self.list, type="VOLUMES")
        if not self._is_value(vol, vol_data, "ID", "Name"):
            _print("FAIL: Could not find specified volume %s." % vol)
            return False
        vol_id = self._get_id(vol, vol_data)
        cmd += "--vol=%s " % vol_id

        if not self._check_size_format(size):
            _print("FAIL: Unsupported size format of size %s." % size)
            return False
        cmd += "--size=%s" % size

        pool_data = self._get_data(cmd=self.list, type="POOLS", script=True)
        vol_fields = self._get_fields(vol_data, "ID", "Pool ID", "Size")
        pool_id = [x[1] for x in vol_fields if x[0] == vol][0]
        old_size = [x[2] for x in vol_fields if x[0] == vol][0]
        new_size = self._get_size_in_bytes(size)
        if old_size == new_size:
            # this works in lsmcli, so returning True
            _print("INFO: New size is the same as old size, aborting volume resize.")
            return True
        elif old_size < new_size:
            key = "Volume Grow"
        else:
            key = "Volume Shrink"
        support_fields = self._get_fields(pool_data, "ID", "Does not support")
        if key in [x[1] for x in support_fields if x[0] == vol]:
            _print("Fail: Selected volume %s on pool %s does not support %sing." % (vol, pool_id, key))
            return False

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not resize volume %s." % vol)
            return False
        return True

    def volume_replicate(self, vol, name, rep_type, pool=None):
        """Creates a new volume and replicates provided volume to it.
        The arguments are:
        \tvol - ID/name of volume to replicate
        \tname - name of new volume to replicate to
        \trep_type - replication type, could be one of [CLONE, COPY, MIRROR, MIRROR_ASYNC].
        \tpool - optional | ID/name of the pool where the new volume should be created from
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "volume-replicate "

        vol_data = self._get_data(cmd=self.list, type="VOLUMES")
        if not self._is_value(vol, vol_data, "Name", "ID"):
            _print("FAIL: Could not find specified volume %s." % vol)
            return False
        cmd += "--vol=%s " % self._get_id(vol, vol_data)

        if self._is_value(name, vol_data, "Name"):
            _print("FAIL: Specified new volume name %s already in use." % vol)
            return False
        cmd += "--name=%s " % name

        if rep_type not in ["CLONE", "COPY", "MIRROR_ASYNC", "MIRROR_SYNC"]:
            _print("FAIL: Specified replication type %s unknown or unsupported." % rep_type)
            return False
        cmd += "--rep-type=%s " % rep_type.upper()

        if pool:
            pool_data = self._get_data(cmd=self.list, type="POOLS")
            if not self._is_value(pool, pool_data, "ID", "Name"):
                _print("FAIL: Could not find specified pool %s." % pool)
                return False
            cmd += "--pool=%s " % self._get_id(pool, pool_data)

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not replicate volume %s." % vol)
            return False
        return True

    def volume_replicate_range(self, src_vol, dst_vol, rep_type, src_start, dst_start, count):
        """Replicates a portion of a volume to the same volume or to a different volume.
        The arguments are:
        \tsrc_vol - ID/name of source volume
        \tdst_vol - ID/name of destination volume
        \trep_type - replication type, could be either CLONE or COPY.
        \tsrc_start - replication source volume start block number. Must be in pair with count and src_start
        \tdst_start - replication source volume start block number. Must be in pair with count and dst_start
        \tcount - the count of replicated block starting from src_start.  Must be in pair with src_start and dst_start.
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "volume-replicate-range -f "

        vol_ids = self._get_data(cmd=self.list, type="VOLUMES")
        if not self._is_value(src_vol, vol_ids, "ID", "Name"):
            _print("FAIL: Could not find specified source volume %s." % src_vol)
            return False
        cmd += "--src-vol=%s " % self._get_id(src_vol, vol_ids)

        if not self._is_value(dst_vol, vol_ids, "ID", "Name"):
            _print("FAIL: Could not find specified destination volume %s." % dst_vol)
            return False
        cmd += "--dst-vol=%s " % self._get_id(dst_vol, vol_ids)

        if rep_type not in ["CLONE", "COPY", "MIRROR_ASYNC", "MIRROR_SYNC"]:
            _print("FAIL: Specified replication %s type unknown or unsupported." % rep_type)
            return False
        cmd += "--rep-type=%s " % rep_type.upper()

        # always get lists
        if not isinstance(src_start, list):
            src_start = [src_start]
        if not isinstance(dst_start, list):
            dst_start = [dst_start]
        if not isinstance(count, list):
            count = [count]
        if len(src_start) != len(dst_start) != len(count):
            _print("FAIL: Got different number of start blocks (%s), distance blocks (%s)"
                   " and number of blocks to replicate (%s)."
                   % (len(src_start), len(dst_start), len(count)))
        for i in range(len(count)):
            cmd += "--src-start=%s " % src_start[i]
            cmd += "--dst-start=%s " % dst_start[i]
            cmd += "--count=%s " % count[i]

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not replicate volume %s to volume %s." % (src_vol, dst_vol))
            return False
        return True

    def volume_replicate_range_block_size(self, sys, return_output=False):
        """Size of each replicated block on a system in bytes.
        The arguments are:
        \tsys - ID/name of system
        \treturn_output - if set True, returns output from console
        Returns:
        \tOnly Boolean if return_output False:
        \t\tTrue if success
        \t\tFalse in case of failure
        \tBoolean and data if return_output True
        """
        if return_output:
            ret_fail = (False, None)
        else:
            ret_fail = False
        cmd = "volume-replicate-range-block-size "

        sys_data = self._get_data(cmd=self.list, type="SYSTEMS")
        if not self._is_value(sys, sys_data, "ID", "Name"):
            _print("FAIL: Could not find specified sys %s." % sys)
            return ret_fail
        cmd += "--sys=%s " % self._get_id(sys, sys_data)

        if return_output:
            retcode, data = self._run_cmd(cmd, return_output=True)
        else:
            retcode = self._run_cmd(cmd)
        if retcode != 0:
            _print("FAIL: Could not get replicate block sizes on system %s." % sys)
            return ret_fail

        if return_output:
            return True, data
        return True

    def volume_dependants(self, vol):
        """Checks if volume has a dependant child (like replication).
        The arguments are:
        \tvol - ID/name of volume
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "volume-dependants "

        vol_data = self._get_data(cmd=self.list, type="VOLUMES")
        if not self._is_value(vol, vol_data, "ID", "Name"):
            _print("FAIL: Could not find specified volume %s." % vol)
            return False, None
        cmd += "--vol=%s " % self._get_id(vol, vol_data)

        ret, data = self._run_cmd(cmd, return_output=True)
        if ret != 0:
            _print("FAIL: Could not get dependants for volume %s." % vol)
            return False, None
        return True, data

    def volume_dependants_rm(self, vol):
        """Removes volume dependencies (like replication).
        The arguments are:
        \tvol - ID/name of volume
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "volume-dependants-rm "

        vol_data = self._get_data(cmd=self.list, type="VOLUMES")
        if not self._is_value(vol, vol_data, "ID", "Name"):
            _print("FAIL: Could not find specified volume %s." % vol)
            return False
        cmd += "--vol=%s " % self._get_id(vol, vol_data)

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not remove dependants for volume %s." % vol)
            return False
        return True

    def volume_access_group(self, vol, return_output=False):
        """Lists the access group(s) that have access to the provided volume.
        The arguments are:
        \tvol - ID/name of volume
        \treturn_output - if set True, returns output from console
        Returns:
        \tOnly Boolean if return_output False:
        \t\tTrue if success
        \t\tFalse in case of failure
        \tBoolean and data if return_output True
        """
        if return_output:
            ret_fail = (False, None)
        else:
            ret_fail = False
        cmd = "volume-access-group "

        vol_data = self._get_data(cmd=self.list, type="VOLUMES")
        if not self._is_value(vol, vol_data, "ID", "Name"):
            _print("FAIL: Could not find specified volume %s." % vol)
            return ret_fail
        cmd += "--vol=%s " % self._get_id(vol, vol_data)

        if return_output:
            retcode, data = self._run_cmd(cmd, return_output=True)
        else:
            retcode = self._run_cmd(cmd)
        if retcode != 0:
            _print("FAIL: Could not get access groups with access to volume %s." % vol)
            return ret_fail

        if return_output:
            return True, data
        return True

    def volume_mask(self, vol, ag):
        """Grant access group RW access to certain volume.
        The arguments are:
        \tvol - ID/name of volume
        \tag - ID/name of access group
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "volume-mask "

        vol_data = self._get_data(cmd=self.list, type="VOLUMES")
        if not self._is_value(vol, vol_data, "ID", "Name"):
            _print("FAIL: Could not find specified volume %s." % vol)
            return False
        cmd += "--vol=%s " % self._get_id(vol, vol_data)

        ag_data = self._get_data(cmd=self.list, type="ACCESS_GROUPS")
        if not self._is_value(ag, ag_data, "ID", "Name"):
            _print("FAIL: Could not find specified access group %s." % ag)
            return False
        cmd += "--ag=%s " % self._get_id(ag, ag_data)

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not mask volume %s to access group %s." % (vol, ag))
            return False
        return True

    def volume_unmask(self, vol, ag):
        """Revoke access group RW access to specified volume.
        The arguments are:
        \tvol - ID/name of volume
        \tag - ID/name of access group
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "volume-unmask -f "

        vol_data = self._get_data(cmd=self.list, type="VOLUMES")
        if not self._is_value(vol, vol_data, "ID", "Name"):
            _print("FAIL: Could not find specified volume %s." % vol)
            return False
        cmd += "--vol=%s " % self._get_id(vol, vol_data, "ID", "Name")

        ag_data = self._get_data(cmd=self.list, type="ACCESS_GROUPS")
        if not self._is_value(ag, ag_data, "ID", "Name"):
            _print("FAIL: Could not find specified access group %s." % ag)
            return False
        ret, ags = self.volume_access_group(vol, return_output=True)
        ag_id = self._get_id(ag, ag_data)
        if not self._is_value([vol, ag], self._parse_data(ags), "ID", "Initiator IDs"):
            _print("FAIL: Specified access group %s does not have access to specified volume %s." % (ag, vol))
            return False
        cmd += "--ag=%s " % ag_id

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not unmask volume %s to access group %s." % (vol, ag))
            return False
        return True

    def volume_enable(self, vol):
        """Enables specified volume.
        The arguments are:
        \tvol - ID/name of volume
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "volume-enable "

        vol_data = self._get_data(cmd=self.list, type="VOLUMES")
        if not self._is_value(vol, vol_data, "ID", "Name"):
            _print("FAIL: Could not find specified volume %s." % vol)
            return False
        cmd += "--vol=%s " % self._get_id(vol, vol_data, "ID", "Name")

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not enable volume %s." % vol)
            return False
        return True

    def volume_disable(self, vol):
        """Disables specified volume.
        The arguments are:
        \tvol - ID/name of volume
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "volume-disable -f "

        vol_data = self._get_data(cmd=self.list, type="VOLUMES")
        if not self._is_value(vol, vol_data, "ID", "Name"):
            _print("FAIL: Could not find specified volume %s." % vol)
            return False
        cmd += "--vol=%s " % self._get_id(vol, vol_data, "ID", "Name")

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not disable volume %s." % vol)
            return False
        return True

    def volume_raid_info(self, vol, return_output=False):
        """Query RAID information for given volume.
        The arguments are:
        \tvol - ID/name of volume
        \treturn_output - if set True, returns output from console
        Returns:
        \tOnly Boolean if return_output False:
        \t\tTrue if success
        \t\tFalse in case of failure
        \tBoolean and data if return_output True
        """
        if return_output:
            ret_fail = (False, None)
        else:
            ret_fail = False
        cmd = "volume-raid-info "

        vol_data = self._get_data(cmd=self.list, type="VOLUMES")
        if not self._is_value(vol, vol_data, "ID", "Name"):
            _print("FAIL: Could not find specified volume %s." % vol)
            return ret_fail
        cmd += "--vol=%s " % self._get_id(vol, vol_data)

        if return_output:
            retcode, data = self._run_cmd(cmd, return_output=True)
        else:
            retcode = self._run_cmd(cmd)
        if retcode != 0:
            _print("FAIL: Could not get raid info for volume %s." % vol)
            return ret_fail

        if return_output:
            return True, data
        return True

    def pool_member_info(self, pool, return_output=False):
        """Query RAID information for given pool.
        The arguments are:
        \tpool - ID/name of pool
        \treturn_output - if set True, returns output from console
        Returns:
        \tOnly Boolean if return_output False:
        \t\tTrue if success
        \t\tFalse in case of failure
        \tBoolean and data if return_output True
        """
        if return_output:
            ret_fail = (False, None)
        else:
            ret_fail = False
        cmd = "pool-member-info "

        pool_data = self._get_data(cmd=self.list, type="POOLS")
        if not self._is_value(pool, pool_data, "ID", "Name"):
            _print("FAIL: Could not find specified pool %s." % pool)
            return ret_fail
        cmd += "--pool=%s " % self._get_id(pool, pool_data)

        if return_output:
            retcode, data = self._run_cmd(cmd, return_output=True)
        else:
            retcode = self._run_cmd(cmd)
        if retcode != 0:
            _print("FAIL: Could not get member info for pool %s." % pool)
            return ret_fail

        if return_output:
            return True, data
        return True

    def access_group_create(self, name, init, sys):
        """Creates and access group.
        The arguments are:
        \tname - name of new access group
        \tinit - ID/name of initiator
        \tsys - ID/name of system
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "access-group-create "

        ag_data = self._get_data(cmd=self.list, type="ACCESS_GROUPS")
        if self._is_value(name, ag_data, "ID", "Name"):
            _print("FAIL: Could not find specified access group %s." % name)
            return False
        cmd += "--name=%s " % name

        init_data = self._get_data(cmd=self.list, type="TARGET_PORTS")
        if not self._is_value(init, init_data, "Address", "Network Address"):
            _print("FAIL: Could not find specified initiator %s." % init)
            return False
        cmd += "--init=%s " % self._get_id(init, init_data, id="Address", name="Network Address")

        sys_data = self._get_data(cmd=self.list, type="SYSTEMS")
        if not self._is_value(sys, sys_data, "ID", "Name"):
            _print("FAIL: Could not find specified sys %s." % sys)
            return False
        cmd += "--sys=%s " % self._get_id(sys, sys_data)

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not create access group %s." % name)
            return False
        return True

    def access_group_add(self, ag, init):
        """Adds an initiator to an access group.
        The arguments are:
        \tag - ID/name of access group
        \tinit - ID/name of initiator
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "access-group-add "

        ag_data = self._get_data(cmd=self.list, type="ACCESS_GROUPS")
        if not self._is_value(ag, ag_data, "ID", "Name"):
            _print("FAIL: Could not find specified access group %s." % ag)
            return False
        cmd += "--ag=%s " % self._get_id(ag, ag_data)

        init_data = self._get_data(cmd=self.list, type="TARGET_PORTS")
        if not self._is_value(init, init_data, "Address", "Network Address"):
            _print("FAIL: Could not find specified initiator %s." % init)
            return False
        ag_id = self._get_id(ag, ag_data)
        ags_inits = self._get_data(cmd=self.list, type="ACCESS_GROUPS", script=True)
        if self._is_value(init, ags_inits, "Initiator IDs"):
            _print("FAIL: Specified initiator %s is already defined in access group %s." % (init, ag))
            return False
        cmd += "--init=%s " % init

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not add initiator %s to access group %s." % (init, ag))
            return False
        return True

    def access_group_remove(self, ag, init):
        """Removes an initiator from an access group.
        The arguments are:
        \tag - ID/name of access group
        \tinit - ID/name of initiator
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "access-group-remove -f "

        ag_data = self._get_data(cmd=self.list, type="ACCESS_GROUPS")
        if not self._is_value(ag, ag_data, "ID", "Name"):
            _print("FAIL: Could not find specified access group %s." % ag)
            return False
        cmd += "--ag=%s " % self._get_id(ag, ag_data)

        init_data = self._get_data(cmd=self.list, type="TARGET_PORTS")
        if not self._is_value(init, init_data, "Address", "Network Address"):
            _print("FAIL: Could not find specified initiator %s." % init)
            return False
        ag_id = self._get_id(ag, ag_data)
        ags_inits = self._get_data(cmd=self.list, type="ACCESS_GROUPS", script=True)
        if not self._is_value(init, ags_inits, "Initiator IDs"):
            _print("FAIL: Specified initiator %s is not defined in access group %s." % (init, ag))
            return False
        cmd += "--init=%s " % init

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not remove initiatotr %s from access group %s." % (init, ag))
            return False
        return True

    def access_group_delete(self, ag):
        """Delete an access group.
        The arguments are:
        \tag - ID/name of access group
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "access-group-delete -f "

        ag_data = self._get_data(cmd=self.list, type="ACCESS_GROUPS")
        if not self._is_value(ag, ag_data, "ID", "Name"):
            _print("FAIL: Could not find specified access group %s." % ag)
            return False
        cmd += "--ag=%s " % self._get_id(ag, ag_data)

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not delete access group %s." % ag)
            return False
        return True

    def access_group_volumes(self, ag, return_output=False):
        """Lists the volumes that the access group has been granted access to.
        The arguments are:
        \tag - ID/name of access group
        \treturn_output - if set True, returns output from console
        Returns:
        \tOnly Boolean if return_output False:
        \t\tTrue if success
        \t\tFalse in case of failure
        \tBoolean and data if return_output True
        """
        if return_output:
            ret_fail = (False, None)
        else:
            ret_fail = False
        cmd = "access-group-volumes "

        ag_data = self._get_data(cmd=self.list, type="ACCESS_GROUPS")
        if not self._is_value(ag, ag_data, "ID", "Name"):
            _print("FAIL: Could not find specified access group %s." % ag)
            return ret_fail
        cmd += "--ag=%s " % self._get_id(ag, ag_data)

        if return_output:
            retcode, data = self._run_cmd(cmd, return_output=True)
        else:
            retcode = self._run_cmd(cmd)
        if retcode != 0:
            _print("FAIL: Could not get volumes with access granted from access group %s." % ag)
            return ret_fail

        if return_output:
            return True, data
        return True

    def iscsi_chap(self, init, in_user=None, in_pass=None, out_user=None, out_pass=None):
        """Configures iSCSI inbound/outbound CHAP authentication.
        The arguments are:
        \tinit - ID/name of iSCSI initiator
        \tin_user - Optional | inbound CHAP user name
        \tin_pass - Optional | inbound CHAP user password
        \tout_user - Optional | outbound CHAP user name
        \tout_pass - Optional | outbound CHAP user password
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "iscsi-chap "

        init_data = self._get_data(cmd=self.list, type="TARGET_PORTS")
        if not self._is_value(init, init_data, "Address", "Network Address"):
            _print("FAIL: Could not find specified initiator %s." % init)
            return False
        init_id = self._get_id(init, init_data, id="Address", name="Network Address")
        init_types = self._get_fields(self._get_data(cmd=self.list, type="TARGET_PORTS"), "Type", "Address")
        if init_types[0] != "iSCSI" and init_types[1] == init_id:
            _print("FAIL: Specified initiator %s is not iSCSI but %s" % (init, init_types[0]))
        cmd += "--init=%s " % init_id

        if in_user and not in_pass or not in_user and in_pass:
            _print("FAIL: Please specify both in_user and in_pass when using them.")
            return False
        if in_user:
            cmd += "--in-user=%s" % in_user
            cmd += "--in-pass=%s" % in_pass

        if out_user and not out_pass or not out_user and out_pass:
            _print("FAIL: Please specify both out_user and out_pass when using them.")
            return False
        if out_user:
            cmd += "--out-user=%s" % out_user
            cmd += "--out-pass=%s" % out_pass

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not configure inbound/outbound CHAP authentication")
            return False
        return True

    def fs_create(self, name, size, pool):
        """Creates a filesystem.
        The arguments are:
        \tname - name of new filesystem
        \tsize - new size, use as INT+UNIT e.g. 100MiB, 10G...
        \pool - ID/name of pool
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "fs-create "

        fs_data = self._get_data(cmd=self.list, type="FS")
        if self._is_value(name, fs_data, "Name"):
            _print("FAIL: Specified fs name %s already in use." % name)
            return False
        cmd += "--name=%s " % name

        pool_data = self._get_data(cmd=self.list, type="POOLS")
        if not self._is_value(pool, pool_data, "ID", "Name"):
            _print("FAIL: Could not find specified pool %s." % pool)
            return False
        cmd += "--pool=%s " % self._get_id(pool, pool_data)

        if not self._check_size_format(size):
            _print("FAIL: Unsupported size format of size %s." % size)
            return False
        cmd += "--size=%s" % size

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not create fs %s." % name)
            return False
        return True

    def fs_delete(self, fs):
        """Deletes a filesystem.
        The arguments are:
        \tfs - ID/name of filesystem
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "fs-delete -f "

        fs_data = self._get_data(cmd=self.list, type="FS")
        if not self._is_value(fs, fs_data, "ID", "Name"):
            _print("FAIL: Could not find specified fs %s." % fs)
            return False
        fs_id = self._get_id(fs, fs_data)
        cmd += "--fs=%s " % fs_id

        export_data = self._get_data(cmd=self.list, type="EXPORTS")
        if self._is_value(fs, export_data, "Filesystem ID"):
            _print("FAIL: Specified fs %s is exported via NFS." % fs)
            return False

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not delete fs %s." % fs)
            return False
        return True

    def fs_resize(self, fs, size):
        """Resizes a filesystem.
        The arguments are:
        \tfs - ID/name of filesystem
        \tsize - new size, use as INT+UNIT e.g. 100MiB, 10G...
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "fs-resize -f "

        fs_data = self._get_data(cmd=self.list, type="FS")
        if not self._is_value(fs, fs_data, "ID", "Name"):
            _print("FAIL: Could not find specified fs %s." % fs)
            return False
        cmd += "--fs=%s " % self._get_id(fs, fs_data)

        if not self._check_size_format(size):
            _print("FAIL: Unsupported size format of size %s." % size)
            return False
        cmd += "--size=%s" % size

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not resize fs %s." % fs)
            return False
        return True

    def fs_export(self, fs, export_path=None, anonuid=None, anongid=None, auth_type=None, root_host=None, ro_host=None, rw_host=None):
        """Export a filesystem via NFS.
        The arguments are:
        \tfs - ID/name of filesystem to export
        \texport_path - Optional | NFS server export path. e.g. '/foo/bar'
        \tanonuid - Optional | the UID(User ID) to map to anonymous user
        \tanongid - Optional | the GID(Group ID) to map to anonymous user
        \tauth_type - Optional | NFS client authentication type. This is just a place holder, not supported yet
        \troot_host - Optional | the host/IP has root access, repeatable as [hostA, hostB]
        \tro_host - Optional | the host/IP has read only access, repeatable as [hostA, hostB]
        \trw_host - Optional | the host/IP has read/write access, repeatable as [hostA, hostB]
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "fs-export "

        fs_data = self._get_data(cmd=self.list, type="FS")
        if not self._is_value(fs, fs_data, "ID", "Name"):
            _print("FAIL: Could not find specified fs %s." % fs)
            return False
        cmd += "--fs=%s " % self._get_id(fs, fs_data)

        if not (ro_host or rw_host):
            _print("FAIL: Please specify ro_host or rw_host.")
            return False

        if export_path:
            cmd += "--exportpath=%s " % export_path

        if anonuid:
            if not isinstance(anonuid, int):
                _print("FAIL: anonuid must be an Int.")
                return False
            cmd += "--anonuid=%s " % anonuid

        if anongid:
            if not isinstance(anongid, int):
                _print("FAIL: anongid must be an Int.")
                return False
            cmd += "--anongid=%s " % anongid

        if auth_type:
            _print("FAIL: 'auth_type' is just a placeholder, not implemented in LSM yet.")
            return False

        if root_host:
            if not isinstance(root_host, list):
                root_host = [root_host]
            for host in root_host:
                cmd += "--root-host=%s " % host

        if ro_host:
            if not isinstance(ro_host, list):
                ro_host = [ro_host]
            for host in ro_host:
                cmd += "--ro-host=%s " % host

        if rw_host:
            if not isinstance(rw_host, list):
                rw_host = [rw_host]
            for host in rw_host:
                cmd += "--rw-host=%s " % host

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not export fs %s." % fs)
            return False
        return True

    def fs_unexport(self, export):
        """Removes an NFS export.
        The arguments are:
        \texport - ID of exported filesystem
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "fs-unexport "

        export_data = self._get_data(cmd=self.list, type="EXPORTS")
        if not self._is_value(export, export_data, "ID"):
            _print("FAIL: Could not find specified export ID %s." % export)
            return False
        cmd += "--export=%s " % export

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not unexport exported fs with export ID %s." % export)
            return False
        return True

    def fs_clone(self, src_fs, dst_name, backing_snapshot=None):
        """Creates a file system clone AKA. read-writable snapshot.
        The arguments are:
        \tname - name of the new snapshot
        \tfs - ID/name of filesystem
        \tbacking_snapshot - optional | ID/name of backing snapshot
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "fs-clone "

        fs_data = self._get_data(cmd=self.list, type="FS")
        if not self._is_value(src_fs, fs_data, "ID", "Name"):
            _print("FAIL: Could not find specified fs %s." % src_fs)
            return False
        fs_id = self._get_id(src_fs, fs_data)
        cmd += "--src-fs=%s " % fs_id

        if self._is_value(dst_name, fs_data, "Name"):
            _print("FAIL: Specified fs name %s already in use." % dst_name)
            return False
        cmd += "--dst-name=%s " % dst_name

        if backing_snapshot:
            snapshot_data = self._get_data(cmd=self.list, type="SNAPSHOTS", fs_id=fs_id)
            if not self._is_value(backing_snapshot, snapshot_data, "ID", "Name"):
                _print("FAIL: Could not find specified backing snapshot %s." % backing_snapshot)
                return False
            cmd += "--backing-snapshot=%s " % self._get_id(backing_snapshot, snapshot_data)

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not clone fs %s." % src_fs)
            return False
        return True

    def fs_snap_create(self, name, fs):
        """Creates a snapshot on filesystem.
        The arguments are:
        \tname - name of the new snapshot
        \tfs - ID/name of filesystem
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "fs-snap-create -f "

        fs_data = self._get_data(cmd=self.list, type="FS")
        if not self._is_value(fs, fs_data, "ID", "Name"):
            _print("FAIL: Could not find specified fs %s." % fs)
            return False
        fs_id = self._get_id(fs, fs_data)
        cmd += "--fs=%s " % fs_id

        snapshot_data = self._get_data(cmd=self.list, type="SNAPSHOTS", fs_id=fs_id)
        if self._is_value(name, snapshot_data, "Name"):
            _print("FAIL: Specified snapshot name %s already in use." % name)
            return False
        cmd += "--name=%s " % name

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not create snapshot %s." % name)
            return False
        return True

    def fs_snap_delete(self, snap, fs):
        """Deletes a snapshot from filesystem.
        The arguments are:
        \tsnap - ID/name of snapshot
        \tfs - ID/name of filesystem
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "fs-snap-delete -f "

        fs_data = self._get_data(cmd=self.list, type="FS")
        if not self._is_value(fs, fs_data, "ID", "Name"):
            _print("FAIL: Could not find specified fs %s." % fs)
            return False
        fs_id = self._get_id(fs, fs_data)
        cmd += "--fs=%s " % fs_id

        snapshot_data = self._get_data(cmd=self.list, type="SNAPSHOTS", fs_id=fs_id)
        if not self._is_value(snap, snapshot_data, "ID", "Name"):
            _print("FAIL: Could not find specified snapshot %s." % snap)
            return False
        cmd += "--snap=%s " % self._get_id(snap, snapshot_data)

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not delete snapshot %s." % snap)
            return False
        return True

    def fs_snap_restore(self, fs, snap, file=None, fileas=None):
        """Restores a FS or specified files to previous snapshot state.
        The arguments are:
        \tfs - ID/name of filesystem
        \tsnap - ID/name of snapshot
        \tfile - optional | only restore this file, repeatable as [fileA, fileB]
        \tfileas - optional | restored files will be saved to this file/path, repeatable as [fileA, fileB]
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "fs-snap-restore -f "

        fs_data = self._get_data(cmd=self.list, type="FS")
        if not self._is_value(fs, fs_data, "ID", "Name"):
            _print("FAIL: Could not find specified fs %s." % fs)
            return False
        fs_id = self._get_id(fs, fs_data)
        cmd += "--fs=%s " % fs_id

        snapshot_data = self._get_data(cmd=self.list, type="SNAPSHOTS", fs_id=fs_id)
        if not self._is_value(snap, snapshot_data, "ID", "Name"):
            _print("FAIL: Could not find specified snapshot %s." % snap)
            return False
        cmd += "--snap=%s " % self._get_id(snap, snapshot_data)

        # FIXME: Do these need to be the same length?
        if file:
            if not isinstance(file, list):
                file = [file]
            for f in file:
                cmd += "--file=%s " % f

        if fileas:
            if not isinstance(fileas, list):
                fileas = [fileas]
            for f in fileas:
                cmd += "--fileas=%s " % f

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not restore from snapshot %s." % snap)
            return False
        return True

    def fs_dependants(self, fs, file=None):
        """Checks if a child dependency (snapshot or clone) exists for filesystem.
        The arguments are:
        \tfs - ID/name of filesystem
        \tfile - optional | only check dependencies for this file, repeatable as [fileA, fileB]
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "fs-dependants "

        fs_data = self._get_data(cmd=self.list, type="FS")
        if not self._is_value(fs, fs_data, "ID", "Name"):
            _print("FAIL: Could not find specified fs %s." % fs)
            return False
        cmd += "--fs=%s " % self._get_id(fs, fs_data)

        if file:
            if not isinstance(file, list):
                file = [file]
            for f in file:
                cmd += "--file=%s " % f

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not get dependants of fs %s." % fs)
            return False
        return True

    def fs_dependants_rm(self, fs, file=None):
        """Removes filesystem dependencies(snapshot or clone).
        The arguments are:
        \tfs - ID/name of filesystem
        \tfile - optional | only remove dependencies for this file, repeatable as [fileA, fileB]
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "fs-dependants-rm "

        fs_data = self._get_data(cmd=self.list, type="FS")
        if not self._is_value(fs, fs_data, "ID", "Name"):
            _print("FAIL: Could not find specified fs %s." % fs)
            return False
        cmd += "--fs=%s " % self._get_id(fs, fs_data)

        if file:
            if not isinstance(file, list):
                file = [file]
            for f in file:
                cmd += "--file=%s " % f

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not remove dependants from fs %s." % fs)
            return False
        return True

    def file_clone(self, fs, src, dst, backing_snapshot=None):
        """Creates a clone of a file (thin provisioned).
        The arguments are:
        \tfs - ID/name of filesystem
        \tsrc - source file to clone from, repeatable as [fileA, fileB]
        \tdst - destination file to clone to, repeatable as [fileA, fileB]
        \tbacking_snapshot - optional | ID/name of backing snapshot
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "fs-dependants-rm "

        fs_data = self._get_data(cmd=self.list, type="FS")
        if not self._is_value(fs, fs_data, "ID", "Name"):
            _print("FAIL: Could not find specified fs %s." % fs)
            return False
        fs_id = self._get_id(fs, fs_data)
        cmd += "--fs=%s " % fs_id

        if not isinstance(src, list):
            src = [src]
        if not isinstance(dst, list):
            dst = [dst]

        if len(src) != len(dst):
            _print("FAIL: Got different number of source files (%s) and distance files (%s)."
                   % (len(src), len(dst)))
        for i in range(len(src)):
            if self._get_file_from_path(src[i]) != self._get_file_from_path(dst[i]):
                _print("FAIL: Source and destination files must be paired.")
                return False
            cmd += "--src=%s " % src[i]
            cmd += "--dst=%s " % dst[i]

        if backing_snapshot:
            snapshot_data = self._get_data(cmd=self.list, type="SNAPSHOTS", fs_id=fs_id)
            if not self._is_value(backing_snapshot, snapshot_data, "ID", "Name"):
                _print("FAIL: Could not find specified snapshot %s." % backing_snapshot)
                return False
            cmd += "--backing-snapshot=%s " % self._get_id(backing_snapshot, snapshot_data)

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not remove dependants from fs %s." % fs)
            return False
        return True

    def system_read_cache_pct_update(self, sys, percentage=None, return_to_previous=False):
        """Change the read cache percentage for a system.
        The arguments are:
        \tsys - ID/name of system
        \tpercentage - new read cache percentage
        \treturn_to_previous - if set True, returns system read cache percentage to previous one
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "system-read-cache-pct-update "

        sys_data = self._get_data(cmd=self.list, type="SYSTEMS")
        if not self._is_value(sys, sys_data, "ID", "Name"):
            _print("FAIL: Could not find specified system %s." % sys)
            return False
        sys_id = self._get_id(sys, sys_data)
        cmd += "--sys=%s " % sys_id

        if percentage:
            if percentage not in range(101):
                _print("FAIL: Percentage must be Int between 0 and 100, got %s." % percentage)
                return False
            sys_read_pcts = self._get_fields(self._get_data(cmd=self.list, type="SYSTEMS"), "ID", "Read Cache Percentage")
            for field in sys_read_pcts:
                if field[0] == sys_id:
                    self.previous_sys_read_pct[sys_id] = field[1]
            cmd += "--read-pct=%s " % percentage
        elif return_to_previous:
            if sys_id not in self.previous_sys_read_pct:
                _print("FAIL: Unknown previous system read cache.")
                return False
            cmd += "--read-pct=%s " % self.previous_sys_read_pct[sys_id]
        else:
            _print("FAIL: Please use either percentage or return_to_previous.")
            return False

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not update system read cache percentage for system %s." % sys)
            return False
        return True

    def local_disk_list(self, return_output=False, script=False):
        """List all disks found on current local operating system.  Require permission to open /dev/sdX as read-only.
        The arguments are:
        \treturn_output - if set True, returns output from console
        \tscript - if set to True, prints out in "script friendly way"
        Returns:
        \tOnly Boolean if return_output False:
        \t\tTrue if success
        \t\tFalse in case of failure
        \tBoolean and data if return_output True
        """
        if return_output:
            ret_fail = (False, None)
        else:
            ret_fail = False
        cmd = "local-disk-list "

        # check if we have read-write access to /dev/DISK
        disks = self._get_local_disks()
        if not disks:
            return ret_fail
        path = "/dev/" + disks[0]
        if not os.access(path, os.R_OK) and not os.access(path, os.W_OK):
            _print("FAIL: Does not have read-write access to %s." % path)
            return ret_fail

        if script:
            cmd += "-s "

        if return_output:
            retcode, data = self._run_cmd(cmd, return_output=True)
        else:
            retcode = self._run_cmd(cmd)
        if retcode != 0:
            _print("FAIL: Could not list local disks.")
            return ret_fail

        if return_output:
            return True, data
        return True

    def volume_cache_info(self, vol, return_output=False):
        """Query RAM cache information for the desired volume.
        The arguments are:
        \tvol - name/ID of volume
        \treturn_output - if set True, returns output from console
        Returns:
        \tOnly Boolean if return_output False:
        \t\tTrue if success
        \t\tFalse in case of failure
        \tBoolean and data if return_output True
        """
        if return_output:
            ret_fail = (False, None)
        else:
            ret_fail = False
        cmd = "volume-cache-info "

        vol_data = self._get_data(cmd=self.list, type="VOLUMES")
        if not self._is_value(vol, vol_data, "ID", "Name"):
            _print("FAIL: Could not find specified volume %s." % vol)
            return ret_fail
        cmd += "--vol=%s " % self._get_id(vol, vol_data)

        if return_output:
            retcode, data = self._run_cmd(cmd, return_output=True)
        else:
            retcode = self._run_cmd(cmd)
        if retcode != 0:
            _print("FAIL: Could not get cache info for volume %s." % vol)
            return ret_fail

        if return_output:
            return True, data
        return True

    def volume_phy_disk_cache_update(self, vol, policy=None, return_to_previous=False):
        """Disable or enable RAM physical disk cache of certain volume.
        The arguments are:
        \tvol - name/ID of volume
        \tpolicy - new policy, could be either ENABLED or DISABLED
        \treturn_to_previous - if set True, returns RAM physical cache policy to previous one
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "volume-phy-disk-cache-update "

        vol_data = self._get_data(cmd=self.list, type="VOLUMES")
        if not self._is_value(vol, vol_data, "ID", "Name"):
            _print("FAIL: Could not find specified volume %s." % vol)
            return False
        vol_id =self._get_id(vol, vol_data)
        cmd += "--vol=%s " % vol_id

        if policy:
            if policy.upper() not in ["ENABLE", "DISABLE"]:
                _print("FAIL: Policy must be either ENABLE or DISABLE, got %s." % policy.upper())
                return False
            phy_disk_cache_policy = self._get_fields(self._get_cache_info(vol), "Volume ID", "Physical Disk Cache")
            self.previous_phy_disk_cache_policy[vol_id] = phy_disk_cache_policy[0][1][:-1].upper()
            cmd += "--policy=%s " % policy
        elif return_to_previous:
            if vol_id not in self.previous_phy_disk_cache_policy:
                _print("FAIL: Unknown previous RAM physical disk cache policy for vol %s." % vol)
                return False
            cmd += "--policy=%s " % self.previous_phy_disk_cache_policy[vol_id]
        else:
            _print("FAIL: Please use either policy or return_to_previous.")
            return False

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not %s RAM physical disk cache policy for volume %s." % (policy.lower(), vol))
            return False
        return True

    def volume_read_cache_policy_update(self, vol, policy=None, return_to_previous=False):
        """Disable or enable RAM read cache of certain volume.
        The arguments are:
        \tvol - name/ID of volume
        \tpolicy - new policy, could be either ENABLED or DISABLED
        \treturn_to_previous - if set True, returns RAM read cache policy to previous one
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "volume-read-cache-policy-update "

        vol_data = self._get_data(cmd=self.list, type="VOLUMES")
        if not self._is_value(vol, vol_data, "ID", "Name"):
            _print("FAIL: Could not find specified volume %s." % vol)
            return False
        vol_id = self._get_id(vol, vol_data)
        cmd += "--vol=%s " % vol_id

        if policy:
            if policy.upper() not in ["ENABLE", "DISABLE"]:
                _print("FAIL: Policy must be either ENABLE or DISABLE, got %s." % policy.upper())
                return False
            read_cache_policy = self._get_fields(self._get_cache_info(vol), "Volume ID", "Read Cache Policy")
            self.previous_read_cache_policy[vol_id] = read_cache_policy[0][1][:-1].upper()
            cmd += "--policy=%s " % policy
        elif return_to_previous:
            if vol_id not in self.previous_read_cache_policy:
                _print("FAIL: Unknown previous RAM read cache policy for vol %s." % vol)
                return False
            cmd += "--policy=%s " % self.previous_read_cache_policy[vol_id]
        else:
            _print("FAIL: Please use either policy or return_to_previous.")
            return False

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not %s RAM read cache policy for volume %s." % (policy.lower(), vol))
            return False
        return True

    def volume_write_cache_policy_update(self, vol, policy=None, return_to_previous=False):
        """Change volume write cache policy.
        The arguments are:
        \tvol - name/ID of volume
        \tpolicy - new policy, could be one of WB, WT or AUTO
        \treturn_to_previous - if set True, returns write cache policy to previous one
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        cmd = "volume-write-cache-policy-update "

        vol_data = self._get_data(cmd=self.list, type="VOLUMES")
        if not self._is_value(vol, vol_data, "ID", "Name"):
            _print("FAIL: Could not find specified volume %s." % vol)
            return False
        vol_id =self._get_id(vol, vol_data)
        cmd += "--vol=%s " % vol_id

        if policy:
            if policy.upper() not in ["WB", "WT", "AUTO"]:
                _print("FAIL: Policy must be either WB, WT or AUTO; got %s." % policy.upper())
                return False
            write_cache_policy = self._get_fields(self._get_cache_info(vol), "Volume ID", "Write Cache Policy")
            self.previous_write_cache_policy[vol_id] = self._translate_write_cache_policy(write_cache_policy[0][1])
            cmd += "--policy=%s " % policy
        elif return_to_previous:
            if vol_id not in self.previous_write_cache_policy:
                _print("FAIL: Unknown previous RAM write cache policy for vol %s." % vol)
                return False
            cmd += "--policy=%s " % self.previous_write_cache_policy[vol_id]
        else:
            _print("FAIL: Please use either policy or return_to_previous.")
            return False

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not set RAM write cache policy to %s for volume %s." % (policy.lower(), vol))
            return False
        return True

    def local_disk_ident_led(self, path, state=None, return_to_previous=False):
        """Turn on/off the identification LED for specified disk path.  Require permission to open disk path as read-write.
        The arguments are:
        \tpath - path to a local disk
        \tstate - desired state of identification LED; could be 0/1, True/False, On/Off
        \treturn_to_previous - if set True, returns identification LED to previous state
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        if not stat.S_ISBLK(os.stat(path).st_mode):
            _print("FAIL: Path %s is not a block device." % path)
            return False

        # check if have RW access to path
        if not os.access(path, os.R_OK) and not os.access(path, os.W_OK):
            _print("FAIL: Does not have read-write access to %s." % path)
            return False

        if state:
            if str(state).upper() not in ["0", "1", "FALSE", "TRUE", "OFF", "ON"]:
                _print("FAIL: State must be either 0/1, True/False or On/Off; got %s." % state)
                return False
            if str(state).upper() in ["1", "TRUE", "ON"]:
                cmd = "local-disk-ident-led-on "
            else:
                cmd = "local-disk-ident-led-off "
            disk_led_status = self._get_local_disk_info(type="LED Status")
            if disk_led_status == "Unknown":
                _print("FAIL: Given disk %s does not support changing LED status." % path)
                return False
            self.previous_local_disk_ident_led[path] = disk_led_status[path].upper()
        elif return_to_previous:
            if path not in self.previous_local_disk_ident_led:
                _print("FAIL: Unknown previous local disk ident LED status for disk %s." % path)
                return False
            if self.previous_local_disk_ident_led[path] == "ON":
                cmd = "local-disk-ident-led-on "
            else:
                cmd = "local-disk-ident-led-off "
        else:
            _print("Fail: Please use either state or return_to_previous.")
            return False

        cmd += "--path=%s " % path

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not set local disk ident led to %s for disk %s." % (cmd[21:24].upper(), path))
            return False
        return True

    def local_disk_fault_led(self, path, state=None, return_to_previous=False):
        """Turn on/off the fault LED for specified disk path.  Require permission to open disk path as read-write.
        The arguments are:
        \tpath - path to a local disk
        \tstate - desired state of fault LED; could be 0/1, True/False, On/Off
        \treturn_to_previous - if set True, returns fault LED to previous state
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        if not stat.S_ISBLK(os.stat(path).st_mode):
            _print("FAIL: Path %s is not a block device." % path)
            return False

        # check if have RW access to path
        if not os.access(path, os.R_OK) and not os.access(path, os.W_OK):
            _print("FAIL: Does not have read-write access to %s." % path)
            return False

        if state:
            if str(state).upper() not in ["0", "1", "FALSE", "TRUE", "OFF", "ON"]:
                _print("FAIL: State must be either 0/1, True/False or On/Off; got %s." % state)
                return False
            if str(state).upper() in ["1", "TRUE", "ON"]:
                cmd = "local-disk-fault-led-on "
            else:
                cmd = "local-disk-fault-led-off "
            disk_led_status = self._get_local_disk_info(type="LED Status")
            if disk_led_status == "Unknown":
                _print("FAIL: Given disk %s does not support changing LED status." % path)
                return False
            self.previous_local_disk_fault_led[path] = disk_led_status[path].upper()
        elif return_to_previous:
            if path not in self.previous_local_disk_fault_led:
                _print("FAIL: Unknown previous local disk fault LED status for disk %s." % path)
                return False
            if self.previous_local_disk_fault_led[path] == "ON":
                cmd = "local-disk-fault-led-on "
            else:
                cmd = "local-disk-fault-led-off "
        else:
            _print("Fail: Please use either state or return_to_previous.")
            return False

        cmd += "--path=%s " % path

        if self._run_cmd(cmd) != 0:
            _print("FAIL: Could not set local disk fault led to %s for disk %s." % (cmd[21:24].upper(), path))
            return False
        return True
