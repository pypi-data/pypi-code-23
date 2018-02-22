# Copyright (C) 2017 Red Hat, Inc.
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

"""vdo.py: Module to manipulate functionality (deduplication and compression) provided by VDO."""

__author__ = "Jakub Krysl"
__copyright__ = "Copyright (c) 2017 Red Hat, Inc. All rights reserved."

import re
import sys, os
import stat
from libsan.host.cmdline import run
from libsan.host.linux import dist_release, package_version


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


class WrongCommandException(Exception):
    def __init__(self, cmd):
        self.command = cmd

    def __str__(self):
        return repr(WrongCommandException.__name__ + ", caused by " + repr(self.command))


class WrongArgumentException(Exception):
    def __init__(self, arg, cmd=None, args=None):
        self.argument = arg
        self.command = cmd
        self.arguments = args

    def __str__(self):
        return repr(WrongArgumentException.__name__ + ", caused by " + repr(self.argument))


class FailedCheckException(Exception):
    def __init__(self, arg=None):
        self.argument = arg

    def __str__(self):
        message = repr(FailedCheckException.__name__)
        if self.argument:
            message += ", caused by " + repr(self.argument)
        return message


class VDO:
    def __init__(self, disable_check=False):
        self.disable_check = disable_check
        try:
            vdo_version = [int(x) for x in package_version("vdo").split(".")]
        except Exception as e:
            _print("FATAL: Could not get VDO version, got error: %s" % e)

        # camelCase of commands and arguments will change sometime
        if vdo_version[0] == 6 and vdo_version[1] > 0:
            self.commands = {"create": "create",
                             "remove": "remove",
                             "start": "start",
                             "stop": "stop",
                             "activate": "activate",
                             "deactivate": "deactivate",
                             "status": "status",
                             "list": "list",
                             "modify": "modify",
                             "change_write_policy": "changeWritePolicy",
                             "enable_deduplication": "enableDeduplication",
                             "disable_deduplication": "disableDeduplication",
                             "enable_compression": "enableCompression",
                             "disable_compression": "disableCompression",
                             "grow_logical": "growLogical",
                             "grow_physical": "growPhysical",
                             "print_config_file": "printConfigFile"}
            self.commands["all"] = self.commands.keys()

            self.arguments = {"all": [self.commands["all"], " --all"],
                              "conf_file": [self.commands["all"], " --confFile="],
                              "log_file": [self.commands["all"], " --logfile="],
                              "name": [self.commands["all"], " --name="],
                              "no_run": [self.commands["all"], " --noRun"],
                              "verbose": [self.commands["all"], " --verbose"],
                              "activate": [["create"], " --activate="],
                              "compression": [["create"], " --compression="],
                              "deduplication": [["create"], " --deduplication="],
                              "device": [["create"], " --device="],
                              "emulate512": [["create"], " --emulate512="],
                              "index_mem": [["create"], " --indexMem="],
                              "sparse_index": [["create"], " --sparseIndex="],
                              "logical_size": [["create", "grow_logical"], " --vdoLogicalSize="],
                              "log_level": [["create"], " --vdoLogLevel="],
                              "slab_size": [["create"], " --vdoSlabSize="],
                              "block_map_cache_size": [["create", "modify"], " --blockMapCacheSize="],
                              "block_map_period": [["create", "modify"], " --blockMapPeriod="],
                              "read_cache": [["create", "modify"], " --readCache="],
                              "read_cache_size": [["create", "modify"], " --readCacheSize="],
                              "ack_threads": [["create", "modify"], " --vdoAckThreads="],
                              "bio_rotation_interval": [["create", "modify"], " --vdoBioRotationInterval="],
                              "bio_threads": [["create", "modify"], " --vdoBioThreads="],
                              "cpu_threads": [["create", "modify"], " --vdoCpuThreads="],
                              "hash_zone_threads": [["create", "modify"], " --vdoHashZoneThreads="],
                              "logical_threads": [["create", "modify"], " --vdoLogicalThreads="],
                              "physical_threads": [["create", "modify"], " --vdoPhysicalThreads="],
                              "write_policy": [["create", "modify", "change_write_policy"], " --writePolicy="],
                              "force_rebuild": [["start"], " --forceRebuild"],
                              "force": [["stop", "remove", "create"], " --force"]}
        else:
            _print("FATAL: VDO commands and arguments for VDO version %s are not known yet!" % ".".join(vdo_version))

    def _add_command(self, cmd):
        # Checks if given command is provided by VDO and returns its correct syntax
        if cmd in self.commands:
            return self.commands[cmd]
        raise WrongCommandException(cmd)

    def _get_arg(self, name):
        if not self.disable_check:
            if name in self.arguments:
                return self.arguments[name][1]
            raise WrongArgumentException(name)
        return self.arguments[name][1]

    def _get_cmd(self, name):
        if self.disable_check:
            return self.commands["all"]
        if name in self.arguments:
            return self.arguments[name][0]
        raise WrongCommandException(name)

    @staticmethod
    def _get_value(string, command, return_type=str):
        _value = string.split(command)[1].split()[0]
        try:
            value = return_type(_value)
        except ValueError as e:
            _print("WARN: Got ValueError: %s." % e)
            return None
        return value

    def _get_possible_arguments(self, command=None):
        # Returns possible arguments for said command if specified
        args = []
        if command:
            for key in self.arguments.keys():
                if self.commands.keys()[self.commands.values().index(command)] in self._get_cmd(key):
                    args.append(key)
        else:
            args = self.arguments.keys()
        return args

    def _add_argument(self, arg, value, command):
        # Checks if given argument is allowed for given command and adds it to cmd string
        if arg not in self.arguments and not self.disable_check:
            raise WrongArgumentException(arg)
        cmd = command.split()[0]
        args = self._get_possible_arguments(cmd)
        if arg not in args:
            raise WrongArgumentException(arg, cmd, args)
        argument = self._get_arg(arg)
        if argument[-1:] == "=":
            command += argument + str(value)
        else:
            command += argument
        return command

    def _add_arguments(self, cmd, **kwargs):
        command = cmd
        for kwarg in kwargs:
            command = self._add_argument(kwarg, kwargs[kwarg], command)
        return command

    @staticmethod
    def _check_size_format(size, return_size=False):
        # check if requested size format is in supported formats and the rest is numbers
        # FIXME: Is KiB and KB valid too?
        try:
            if size[-3:] in ["KiB", "MiB", "GiB", "TiB"] and isinstance(int(size[:-3]), int):
                if return_size:
                    return True, [size[:-3], size[-3:-2]]
                return True
            elif size[-2:] in ["KB", "MB", "GB", "TB"] and isinstance(int(size[:-2]), int):
                if return_size:
                    return True, [size[:-2], size[-2:-1]]
                return True
            elif size[-1:].upper() in ["K", "M", "G", "T"] and isinstance(int(size[:-1]), int):
                if return_size:
                    return True, [size[:-1], size[-1:]]
                return True
            elif int(size):
                if return_size:
                    # default size is megabytes
                    return True, [size, "M"]
                return True
        except ValueError:
            pass
        return False, []

    @staticmethod
    def _is_positive_int(value):
        try:
            port = int(value)
            if port < 1:
                raise ValueError
        except:
            return False
        return True

    def _check(self, cmd):
        if self.disable_check:
            # Do not check if checking is disabled
            _print("DEBUG: Checking disabled.")
            return True

        if self._get_arg("all") in cmd and self._get_arg("name") in cmd:
            _print("WARN: Use either 'name' or 'all', not both.")
            raise FailedCheckException()

        if self._get_arg("conf_file") in cmd:
            _file = self._get_value(cmd, self._get_arg("conf_file"))
            if not os.path.isfile(_file):
                _print("WARN: Config file %s is not a regular file." % _file)
                raise FailedCheckException(self._get_arg("conf_file"))

        if self._get_arg("log_file") in cmd:
            _file = self._get_value(cmd, self._get_arg("log_file"))
            if not os.path.isfile(_file) and stat.S_ISBLK(os.stat(_file).st_mode):
                _print("WARN: Path %s exists and is not a regular file." % _file)
                raise FailedCheckException(self._get_arg("log_file"))

        if self._get_arg("name") in cmd:
            _name = self._get_value(cmd, self._get_arg("name"))
            # FIXME: Check if VDO already exists
            if False:
                raise FailedCheckException(self._get_arg("name"))

        for arg in ["activate", "compression", "deduplication", "emulate512", "sparse_index", "read_cache"]:
            if self._get_arg(arg) in cmd:
                _value = self._get_value(cmd, self._get_arg(arg))
                if _value not in ["enabled", "disabled"]:
                    _print("WARN: %s value must be either 'enabled' or 'disabled'." % arg)
                    raise FailedCheckException(self._get_arg(arg))

        for arg in ["logical_size", "slab_size", "block_map_cache_size", "read_cache_size"]:
            if self._get_arg(arg) in cmd:
                _value = self._get_value(cmd, self._get_arg(arg))
                ret, size = self._check_size_format(_value, return_size=True)
                if not ret:
                    _print("WARN: VDO %s value %s is in unknown format." % (" ".join(arg.split("_")), _value))
                    raise FailedCheckException(self._get_arg(arg))
                if arg == "slab_size":
                    pass
                    # FIXME: Check if size is power of 2 between 128M and 32G
                elif arg == "block_map_cache_size":
                    pass
                    # FIXME: Check if size is multiple of 4096

        if self._get_arg("index_mem") in cmd:
            _value = self._get_value(cmd, self._get_arg("index_mem"), return_type=float)
            if not (_value in [0, 0.25, 0.5, 0.75] or self._is_positive_int(_value)):
                _print("WARN: Albireo mem value %s is not a 0, 0.25, 0.5, 0.75 or positive int." % _value)
                raise FailedCheckException(self._get_arg("index_mem"))

        if self._get_arg("log_level") in cmd:
            _value = self._get_value(cmd, self._get_arg("log_level"))
            possible_values = ["critical", "error", "warning", "notice", "info", "debug"]
            if _value not in possible_values:
                _print("WARN: Unknown vdo log level value, must be one of %s." % possible_values)
                raise FailedCheckException(self._get_arg("log_level"))

        if self._get_arg("device") in cmd:
            _value = self._get_value(cmd, self._get_arg("device"))
            # FIXME: Check if device exists
            if False:
                raise FailedCheckException(self._get_arg("device"))

        if self._get_arg("block_map_period") in cmd:
            _value = self._get_value(cmd, self._get_arg("block_map_period"))
            if not self._is_positive_int(_value):
                _print("WARN: Block map period value must be a positive integer.")
                raise FailedCheckException(self._get_arg("block_map_period"))
            # FIXME: Can this be higher than 16380?

        for arg in ["ack_threads", "bio_rotation_interval", "bio_threads", "cpu_threads", "hash_zone_threads",
                    "logical_threads", "physical_threads"]:
            if self._get_arg(arg) in cmd:
                _value = self._get_value(cmd, self._get_arg(arg))
                if not self._is_positive_int(_value):
                    _print("WARN: VDO %s value must be a positive integer." % " ".join(arg.split("_")))
                    raise FailedCheckException(self._get_arg(arg))
                    # FIXME: Is 0 valid?

        if self._get_arg("write_policy") in cmd:
            _value = self._get_value(cmd, self._get_arg("write_policy"))
            if _value not in ["sync", "async"]:
                _print("WARN: VDO read cache value must be either 'sync' or 'async'.")
                raise FailedCheckException(self._get_arg("write_policy"))

        if self._get_arg("force_rebuild") in cmd and self._get_arg("upgrade") in cmd:
            _print("WARN: Cannot use both force_rebuild and upgrade when starting VDO volume.")
            raise FailedCheckException()

        return True

    def _run(self, cmd, verbosity=True, return_output=False, **kwargs):
        # Constructs the command to run and runs it

        ret_fail = False
        if return_output:
            ret_fail = (False, None)

        try:
            command = self._add_command(cmd)
            command = self._add_arguments(command, **kwargs)

        except WrongCommandException as e:
            _print("WARN: Given command '%s' is not allowed in this VDO version." % e.command)
            return ret_fail
        except WrongArgumentException as e:
            message = "WARN: Given argument '%s' is not allowed for given command." % e.argument
            if e.command:
                message = message[:-1] + " '" + e.command + "'."
            if e.arguments:
                message += "\nPlease use only these: %s." % ", ".join(e.arguments)
            _print(message)
            return ret_fail

        cmd = "vdo " + command

        try:
            self._check(cmd)
        except WrongArgumentException:
            pass
        except FailedCheckException as e:
            _print("WARN: Failed checking on argument %s" % e.argument)
            return ret_fail

        if return_output:
            ret, data = run(cmd, verbose=verbosity, return_output=True)
            if ret != 0:
                _print("WARN: Running command: '%s' failed. Return with output." % cmd)
                return ret_fail[0], data
            return True, data
        if run(cmd, verbose=verbosity) != 0:
            _print("WARN: Running command: '%s' failed." % cmd)
            return ret_fail
        return True

    @staticmethod
    def help():
        if run("vdo --help", verbose=True) != 0:
            _print("WARN: Running command: 'vdo --help' failed.")
            return False
        return True

    def create(self, **kwargs):
        return self._run("create", **kwargs)

    def remove(self, force=True, **kwargs):
        return self._run("remove", force=force, **kwargs)

    def start(self, **kwargs):
        return self._run("start", **kwargs)

    def stop(self, force=True, **kwargs):
        return self._run("stop", force=force, **kwargs)

    def activate(self, **kwargs):
        return self._run("activate", **kwargs)

    def deactivate(self, **kwargs):
        return self._run("deactivate", **kwargs)

    def status(self, **kwargs):
        return self._run("status", **kwargs)

    def list(self, **kwargs):
        return self._run("list", **kwargs)

    def modify(self, **kwargs):
        return self._run("modify", **kwargs)

    def change_write_policy(self, **kwargs):
        return self._run("change_write_policy", **kwargs)

    def deduplication(self, enable=True, **kwargs):
        if enable:
            ret = self._run("enable_deduplication", **kwargs)
        else:
            ret = self._run("disable_deduplication", **kwargs)
        return ret

    def compression(self, enable=True, **kwargs):
        if enable:
            ret = self._run("enable_compression", **kwargs)
        else:
            ret = self._run("disable_compression", **kwargs)
        return ret

    def grow(self, type=None, **kwargs):
        if type.upper() not in ["LOGICAL", "PHYSICAL"]:
            _print("WARN: Please specify either 'logical' or 'physical' type for growing VDO.")
            if kwargs['return_output']:
                return False, None
            return False

        if type.upper() == "LOGICAL":
            ret = self._run("grow_logical", **kwargs)
        else:
            ret = self._run("grow_physical", **kwargs)
        return ret

    def print_config_file(self, **kwargs):
        return self._run("print_config_file", **kwargs)

class VDOStats:
    def __init__(self, disable_check=False):
        self.disable_check = disable_check
        release = None
        try:
            release = float(dist_release())
        except Exception as e:
            _print("FATAL: Could not change release to float, got: %s" % e)

        # camelCase of commands and arguments will change in RHEL 8
        if 7.0 < release < 8.0:
            self.command = "vdostats"
            self.arguments = {"help": " --help",
                              "all": " --all",
                              "human_readable": " --human-readable",
                              "si": " --si",
                              "verbose": " --verbose",
                              "version": " --version"}
        else:
            _print("FATAL: vdostats commands and arguments for RHEL %s are not known yet!" % release)

    def _get_arg(self, name):
        return self.arguments[name]

    def _get_possible_arguments(self):
        # Returns possible arguments
        return self.arguments.keys()

    def _add_argument(self, arg, command):
        # Checks if given argument is allowed and adds it to cmd string
        if arg not in self.arguments:
            return None
        argument = self._get_arg(arg)
        command += argument
        return command

    def _add_arguments(self, cmd, **kwargs):
        command = cmd
        for kwarg in kwargs:
            command = self._add_argument(kwarg, command)
            if command is None:
                args = self._get_possible_arguments()
                _print("WARN: Unknown argument '%s', please use only these: %s." % (kwarg, args))
                return None
        return command

    def _check(self, cmd):
        if self.disable_check:
            # Do not check if checking is disabled
            _print("DEBUG: Checking disabled.")
            return True

        # check if specified devices are block devices
        for block in cmd.split():
            if block not in self.arguments.values() and block != self.command:
                if os.path.exists(block) and not stat.S_ISBLK(os.stat(block).st_mode):
                    _print("WARN: Device %s is not a block device." % block)
                    return False

        return True

    def _run(self, **kwargs):
        # Constructs the command to run and runs it
        cmd = self.command

        if "devices" in kwargs:
            devices = kwargs.pop("devices")
            if isinstance(devices, list):
                for device in devices:
                    cmd += " " + str(device)
            else:
                cmd += " " + str(devices)

        cmd = self._add_arguments(cmd, **kwargs)
        if cmd is None:
            return False

        if not self._check(cmd):
            # Requested command did not pass checking, reason was already written by _check()
            return False

        if run(cmd, verbose=True) != 0:
            _print("WARN: Running command: '%s' failed." % cmd)
            return False
        return True

    def help(self):
        if not self._run(help=True):
            return False
        return True

    def version(self):
        if not self._run(version=True):
            return False
        return True

    def stats(self, **kwargs):
        if not self._run(**kwargs):
            return False
        return True