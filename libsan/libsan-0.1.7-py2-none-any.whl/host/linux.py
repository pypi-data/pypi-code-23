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

"""linux.py: Module to get information from Linux servers."""

__author__      = "Bruno Goncalves"
__copyright__   = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

from libsan.host.cmdline import run
from os import listdir
import os.path
import sys, signal, errno
import time, subprocess
from datetime import datetime
import re #regex
import libsan.host.mp
import platform


def _print(string):
    module_name = __name__
    string = re.sub("DEBUG:", "DEBUG:("+ module_name + ") ", string)
    string = re.sub("FAIL:", "FAIL:("+ module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:("+ module_name + ") ", string)
    string = re.sub("WARN:", "WARN:("+ module_name + ") ", string)
    print string
    return

def hostname():
    """
    """
    ret, host = run("hostname", verbose=False, return_output=True)
    if ret != 0:
        _print("FAIL: hostname() - could not run command")
        print host
        return None
    return host

def dist_release():
    """
    Find out the release number of Linux distribution.
    """
    #We are base on output of lsb_release -r -s' which is shiped by redhat-lsb rpm.
    #ret, release = run("lsb_release --release --short", verbose=False, return_output=True)
    #if ret == 0:
    #    return release
    dist = platform.linux_distribution()
    if not dist or dist[1] == "":
        _print("FAIL: dist_release() - Could not determine dist release")
        return None
    return dist[1]

def dist_ver():
    """
    Check the Linux distribution version.
    """
    release = dist_release()
    if not release:
        return None
    m = re.match("(\d+).\d+", release)
    if m:
        return int(m.group(1))

    #See if it is only digits, in that case return it
    m = re.match("(\d+)", release)
    if m:
        return int(m.group(1))

    _print("FAIL: dist_ver() - Invalid release output %s" % release)
    return None

def dist_ver_minor():
    """
    Check the Linux distribution minor version.
    For example: RHEL-7.4 returns 4
    """
    release = dist_release()
    if not release:
        return None
    m = re.match("\d+.(\d+)", release)
    if m:
        return int(m.group(1))

    _print("FAIL: dist_ver_minor() - Release does not seem to have minor version: %s" % release)
    return None

def dist_name():
    """
    Find out the name of Linux distribution.
    """
    #We are base on output of lsb_release -r -s' which is shiped by redhat-lsb rpm.
    #ret, release = run("lsb_release --release --short", verbose=False, return_output=True)
    #if ret == 0:
    #    return release
    dist = platform.linux_distribution()
    if not dist or dist[0] == "":
        _print("FAIL: dist_name() - Could not determine Linux dist name")
        return None

    dist_name_2_alias = {}
    dist_name_2_alias["Red Hat Enterprise Linux Server"] = "RHEL"

    if dist[0] in dist_name_2_alias.keys():
        return dist_name_2_alias[dist[0]]

    return dist[0]


def dist_id():
    """
    Find out the id of Linux distribution.
    """
    dist = platform.linux_distribution()
    if not dist or dist[2] == "":
        _print("FAIL: dist_id() - Could not determine Linux id")
        return None

    return dist[2]



def service_start(service_name):
    """Start service
    The arguments are:
    \tNone
    Returns:
    \tTrue: Service started
    \tFalse: There was some problem
    """
    cmd = "systemctl start %s" % service_name
    has_systemctl = True

    if  run("which systemctl", verbose=False) != 0:
        has_systemctl = False
    if not has_systemctl:
        cmd = "service %s start" % service_name

    retcode = run(cmd, return_output=False, verbose=True)
    if (retcode != 0):
        _print ("FAIL: Could not start %s" % service_name)
        if has_systemctl:
            run("systemctl status %s" % service_name)
            run("journalctl -xn")
        return False
    return True

def service_stop(service_name):
    """
    Stop service
    The arguments are:
    \tName of the service
    Returns:
    \tTrue: Service stopped
    \tFalse: There was some problem
    """
    cmd = "systemctl stop %s" % service_name
    has_systemctl = True

    if  run("which systemctl", verbose=False) != 0:
        has_systemctl = False
    if not has_systemctl:
        cmd = "service %s stop" % service_name

    retcode = run(cmd, return_output=False, verbose=True)
    if (retcode != 0):
        _print ("FAIL: Could not stop %s" % service_name)
        if has_systemctl:
            run("systemctl status %s" % service_name)
            run("journalctl -xn")
        return False
    return True

def service_restart(service_name):
    """
    Restart service
    The arguments are:
    \tName of the service
    Returns:
    \tTrue: Service restarted
    \tFalse: There was some problem
    """
    cmd = "systemctl restart %s" % service_name
    has_systemctl = True

    if  run("which systemctl", verbose=False) != 0:
        has_systemctl = False
    if not has_systemctl:
        cmd = "service %s restart" % service_name

    retcode = run(cmd, return_output=False, verbose=True)
    if (retcode != 0):
        _print ("FAIL: Could not restart %s" % service_name)
        if has_systemctl:
            run("systemctl status %s" % service_name)
            run("journalctl -xn")
        return False
    return True


def service_status(service_name):
    """
    Check service status
    The arguments are:
    \tName of service
    Returns:
    \t 0 - service is running and OK
    \t 1 - service is dead and /run pid file exists
    \t 2 - service is dead and /lock lock file exists
    \t 3 - service is not running
    \t 4 - service could not be found.
    \t False - something went wrong.
    """
    cmd = "systemctl status %s" % service_name
    has_systemctl = True

    if run("which systemctl", verbose=False) != 0:
        has_systemctl = False
    if not has_systemctl:
        cmd = "service %s status" % service_name

    retcode = run(cmd, return_output=False, verbose=True)
    if retcode == 0:
        _print("INFO: Service %s is running." % service_name)
    elif retcode == 1:
        _print("INFO: Service %s is dead and /run pid file exists." % service_name)
    elif retcode == 2:
        _print("INFO: Service %s is dead and /lock lock file exists." % service_name)
    elif retcode == 3:
        _print("INFO: Service %s is not running." % service_name)
    elif retcode == 4:
        _print("INFO: Service %s could not be found." % service_name)
    else:
        return False
    return retcode


def is_service_running(service_name):
    """
    Check if service is running
    The arguments are:
    \tName of service
    Returns:
    \t True: service is running
    \t False: service is not running
    """

    if (service_status(service_name) == 0):
        return True
    else:
        return False

def os_arch():
    ret, arch = run("uname -m", verbose=False, return_output=True)
    if ret != 0:
        _print("FAIL: could not get OS arch")
        return None

    return arch

def is_installed(pack):
    """
    Checks if package is installed
    """
    ret, ver = run("rpm -q %s" % pack, verbose=False, return_output=True)
    if ret == 0:
        print("INFO: %s is installed (%s)" % (pack, ver))
        return True

    print "INFO: %s is not installed " % pack
    return False

def install_package(pack, check=True):
    """
    Install a package "pack" via `yum install -y`
    """
    #Check if package is already installed
    if check and is_installed(pack):
        return True

    if run("yum install -y %s" % pack) != 0:
        msg = "FAIL: Could not install %s" % pack
        _print(msg)
        return False

    print "INFO: %s was successfully installed" % pack
    return True

def package_version(pkg):
    """
    Get the version of specific package
    """
    if not pkg:
        _print("FAIL: package_version requires package name as parameter")
        return None

    release = dist_name()
    if release == "RHEL" or release == "Fedora":
        ret, output = run("rpm -qa --qf='%%{version}.%%{release}' %s" % pkg,
                          return_output=True, verbose=False)
        if ret != 0:
            _print("FAIL: Could not get version for package: %s" % pkg)
            print output
            return None
        return output

    _print("FAIL: package_version() - Unsupported release: %s" % release)
    return None

def wait_udev(sleeptime=15):
    """
    Wait udev to finish. Often used after scsi rescan.
    """
    _print("INFO: Waiting udev to finish storage scan")
    #For example, on RHEL 7 scsi_wait_scan module is deprecated
    if run("modinfo scsi_wait_scan", verbose=False) == 0:
        run("modprobe -q scsi_wait_scan")
        run("modprobe -r -q scsi_wait_scan")

    run("udevadm settle")
    sleep(sleeptime)

    return True

def get_all_loaded_modules():
    """
    Check /proc/modules and return a list of all modules that are loaded
    """
    cmd = "cat /proc/modules | cut -d \" \" -f 1"
    ret, output = run(cmd, return_output=True, verbose=False)
    if ret != 0:
        _print("FAIL: load_module() - Could not execute: %s" % cmd)
        print output
        return None

    modules = output.split("\n")
    return modules


def load_module(module):
    """
    Run modprobe using module with parameters given as input
    Parameters:
    \tmodule:       module name and it's parameters
    """
    if not module:
        _print("FAIL: load_module() - requires module parameter")
        return False
    cmd = "modprobe %s" % module
    if run(cmd) != 0:
        _print("FAIL: load_module() - Could not execute: %s" % module)
        return False
    return True

def unload_module(module_name):
    """
    Run rmmod to unload module
    Parameters:
    \tmodule_name:       module name
    """
    if not module_name:
        _print("FAIL: unload_module() - requires module parameter")
        return False
    cmd = "rmmod %s" % module_name
    if run(cmd) != 0:
        _print("FAIL: unload_module() - Could not unload: %s" % module_name)
        return False
    return True

def is_module_loaded(module_name):
    """
    Check if given module is loaded
    Parameters:
    \tmodule_name:      module_name
    """
    if module_name in get_all_loaded_modules():
        return True
    return False

def sleep(duration):
    """
    It basically call sys.sleep, but as stdout and stderr can be buffered
    We flush them before sleep
    """
    sys.stdout.flush()
    sys.stderr.flush()
    time.sleep(duration)
    return

def mount(device=None, mountpoint=None, fs=None, options=None):
    cmd = "mount"
    if fs:
        cmd += " -t %s" % fs
    if options:
        cmd += " -o %s" % options
    if device:
        cmd += " %s" % device
    if mountpoint:
        cmd += " %s" % mountpoint
    if run(cmd) != 0:
        _print("FAIL: Could not mount partition")
        return False

    return True

def umount(device = None, mountpoint = None):
    cmd = "umount"
    if device:
        cmd += " %s" % device
        if run("mount | grep %s" % device, verbose=False) != 0:
            #Device is not mounted
            return True

    if mountpoint:
        cmd += " %s" % mountpoint
        if run("mount | grep %s" % mountpoint, verbose=False) != 0:
            #Device is not mounted
            return True

    if run(cmd) != 0:
        _print("FAIL: Could not umount partition")
        return False

    return True

def get_default_fs():
    """Return the default FileSystem for this release"""
    if dist_name() == "RHEL" and dist_ver() > 6:
        return "xfs"

    return "ext4"

def run_cmd_background(cmd, verbose=False):
    """
    Run Command on background
    Returns:
        subprocess.
            PID is on process.pid
            Exit code is on process.returncode (after run process.communicate())
        Wait for process to finish
            while process.poll() is None:
                linux.sleep(1)
        Get stdout and stderr
            (stdout, stderr) = process.communicate()
    """

    #newpid = os.fork()
    #if newpid == 0:
    #    rt = run(cmd, verbose=verbose)
    #    if not rt:
    #        sys.exit(1)
    #    sys.exit(0)
    #else:
    #    _print("INFO: running %s on background" % cmd)
    #    return newpid
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if not process:
        _print("FAIL: Could not run '%s' on background" % cmd)
        return None
    _print("INFO: running %s on background. PID is %d" % (cmd, process.pid))
    return process

def kill_pid(pid):
    os.kill(pid, signal.SIGTERM)
    sleep(1)
    if check_pid(pid):
        os.kill(pid, signal.SIGKILL)
        sleep(1)
        if check_pid(pid):
            return False
    return True

def kill_all(process_name):
    ret = run("killall %s" % process_name, verbose=None)
    #Wait few seconds for process to finish
    sleep(3)
    return ret

def check_pid(pid):
    """ Check there is a process running with this PID"""
    #try:
        ##0 is the signal, it does not kill the process
        #os.kill(int(pid), 0)
    #except OSError:
        #return False
    #else:
        #return True
    try:
        return os.waitpid(pid, os.WNOHANG) == (0, 0)
    except OSError, e:
        if e.errno != errno.ECHILD:
            raise

def time_stamp(in_seconds=False):
    now = datetime.now()

    #ts = "%s%s%s%s%s%s" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
    ts = now.strftime('%Y%m%d%H%M%S')
    if in_seconds:
        ts = now.strftime('%s')
    return ts

def kernel_command_line():
    """
    Return the kernel command line used to boot
    """
    retcode, output = run("cat /proc/cmdline", return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: could not get kernel command line")
        print output
        return None
    return output


def kernel_version():
    """
    Usage
        kernel_version()
    Purpose
        Check out running kernel version. The same as output of `uname -r`
    Parameter
        N/A
    Returns
        kernel_version
    """
    retcode, output = run("uname -r", return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: could not get kernel version")
        print output
        return None
    #remove arch detail and kernel type
    output = re.sub("\.%s.*" % os_arch(),"", output)
    return output

def kernel_type():
    """
    Usage
        kernel_type()
    Purpose
        Check the kernel type. Current we support detection of these types:
            1. default kernel.
            2. debug kernel.
            3. rt kernel.
    Parameter
        N/A
    Returns
        kernel_type        # 'debug|rt|default'
    """
    retcode, version = run("uname -r", return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: kernel_type() - could not get kernel version")
        print version
        return None

    if re.match(".*\.debug$", version):
        return "debug"

    if re.match(".*\.rt$", version):
        return "rt"

    return "default"

def kmem_leak_start():
    """
    Usage
        kmem_leak_start()
    Purpose
        Start and clear kernel memory leak detection.
    Parameter
        N/A
    Returns
        True
          or
        False       # not debug kernel or failure found
    """
    k_type = kernel_type()

    if not k_type or k_type != "debug":
        _print("WARN: Not debug kernel, will not enable kernel memory leak check")
        return False

    arch = os_arch()
    if arch == "i386" or arch == "i686":
        print "INFO: Not enabling kmemleak on 32 bits server."
        return False

    k_commandline = kernel_command_line()
    if not re.search("kmemleak=on", k_commandline):
        _print("WARN: kmem_leak_start(): need 'kmemleak=on' kernel_option " +
               "to enable kernel memory leak detection")

    check_debugfs_mount_cmd = "mount | grep \"/sys/kernel/debug type debugfs\""
    retcode = run(check_debugfs_mount_cmd, verbose=False)
    if retcode != 0:
        # debugfs is not mounted
        mount_debugfs_cli_cmd = "mount -t debugfs nodev /sys/kernel/debug"
        run(mount_debugfs_cli_cmd, verbose=True)
        check_debugfs_mount_cmd = "mount | grep \"/sys/kernel/debug type debugfs\""
        retcode, output = run(check_debugfs_mount_cmd, return_output=True, verbose=False)
        if retcode != 0:
            _print("WARN: Failed to mount debugfs to /sys/kernel/debug")
            print output
            return False

    # enable kmemleak and clear
    _print("INFO: Begin kernel memory leak check")
    if (run("echo scan=on > /sys/kernel/debug/kmemleak") != 0):
        return False
    if (run("echo stack=on > /sys/kernel/debug/kmemleak") != 0):
        return False
    if (run("echo clear > /sys/kernel/debug/kmemleak") != 0):
        return False
    return True

def kmem_leak_check():
    """
    Usage
        kmem_leak_check()
    Purpose
        Read out kernel memory leak check log and then clear it up.
    Parameter
        N/A
    Returns
        kmemleak_log
          or
        None       # when file '/sys/kernel/debug/kmemleak' not exists
                  # or no leak found
    """
    sysfs_kmemleak = "/sys/kernel/debug/kmemleak"
    if not os.path.isfile(sysfs_kmemleak):
        return None

    f = open(sysfs_kmemleak)
    if not f:
        _print("FAIL: Could not read %s" % sysfs_kmemleak)
        return None

    kmemleak_log = f.read()
    f.close()
    if kmemleak_log:
        _print("WARN: Found kernel memory leak:\n%s" % kmemleak_log)
        _print("INFO: Clearing memory leak for next check")
        run("echo 'clear' > %s" % sysfs_kmemleak)
        return kmemleak_log

    _print("INFO: No kernel memory leak found")
    return None

def kmem_leak_disable():
    """
    Usage
        kmem_leak_disable()
    Purpose
        Disable kmemleak by 'scan=off' and 'stack=off' to
        '/sys/kernel/debug/kmemleak'.
    Parameter
        N/A
    Returns
        True           # disabled or not enabled yet
          or
        False       # failed to run 'echo' command
    """
    sysfs_kmemleak = "/sys/kernel/debug/kmemleak"
    if not os.path.isfile(sysfs_kmemleak):
        return True

    _print("INFO: kmem_leak_disable(): Disabling kernel memory leak detection")
    ok1, ok1_output = run("echo scan=off > %s" % sysfs_kmemleak, return_output=True)
    ok2, ok2_output = run("echo stack=off > %s" % sysfs_kmemleak, return_output=True)
    if ok1 != 0 or ok2 != 0:
        print("FAIL: kmem_leak_disable(): Failed to disable "
              + " kernel memory leak detection")
        print ok1_output
        print ok2_output
        return False

    _print("INFO: kmem_leak_disable(): Kernel memory leak detection "
      + "disabled")
    return True

def query_os_info():
    """
    query_os_info()
    Purpose
        Query OS informations and set a reference below:
        os_info = {
            dist_name       = dist_name,
            dist_release    = dist_release,
            kernel_version  = kernel_version,
            os_arch         = os_arch,
            arch            = os_arch,
            pkg_arch        = pkg_arch, #as, for example, rpm on i386 could return different arch then uname -m

        }
    Parameter
        N/A
    Returns
        os_info_dict
            or
        None       # got error
    """

    os_info_dict = {}
    os_info_dict["dist_name"] = dist_name()
    os_info_dict["dist_version"] = dist_ver()
    os_info_dict["dist_release"] = dist_release()
    os_info_dict["os_arch"] = os_arch()
    os_info_dict["arch"] = os_arch()
    os_info_dict["pkg_arch"] = os_arch()
    os_info_dict["kernel_version"] = kernel_version()
    os_info_dict["kernel_type"] = kernel_type()
    return os_info_dict

def get_driver_info(driver):
    """
    """
    if not driver:
        _print("FAIL: get_driver_info() - requires driver parameter")
        return None

    sys_fs_path = "/sys/module"
    if not os.path.isdir(sys_fs_path):
        _print("FAIL: get_driver_info() - %s is not a valid directory" % sys_fs_path)
        return None

    sysfs_driver_folder = "%s/%s" % (sys_fs_path, driver)
    if not os.path.isdir(sysfs_driver_folder):
        _print("FAIL: get_driver_info() - module %s is not loaded" % driver)
        return None

    driver_info = {}
    infos = ["srcversion", "version", "taint"]
    for info in infos:
        info_path = "%s/%s" % (sysfs_driver_folder, info)
        if not os.path.isfile(info_path):
            continue
        ret, output = run("cat %s/%s" % (sysfs_driver_folder, info), return_output=True, verbose=False)
        driver_info[info] = output

    sys_driver_parameter = "%s/parameters/" % sysfs_driver_folder
    if os.path.isdir(sys_driver_parameter):
        #Need to add driver parameters
        param_files = [f for f in listdir(sys_driver_parameter) if os.path.isfile(os.path.join(sys_driver_parameter, f))]
        for param in param_files:
            ret, output = run("cat %s/%s" % (sys_driver_parameter, param), return_output=True, verbose=False)
            if "parameters" not in driver_info:
                driver_info["parameters"] = {}
            driver_info["parameters"][param] = output
    return driver_info


def mkdir(new_dir):
    """
    """
    if os.path.isdir(new_dir):
        _print("INFO: %s already exist" % new_dir)
        return True
    cmd = "mkdir -p %s" % new_dir
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: could create directory %s" % new_dir)
        print output
        return False
    return True

def rmdir(dir_name):
    """
    Remove directory and all content from it
    """
    if not os.path.isdir(dir_name):
        _print("INFO: %s does not exist" % dir_name)
        return True
    cmd = "rm -rf %s" % dir_name
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: could remove directory %s" % dir_name)
        print output
        return False
    return True

def mkfs(device_name, fs_type, force=False):
    """
    Create a Filesystem on device
    """
    if not device_name or not fs_type:
        _print("INFO: mkfs() requires device_name and fs_type")
        return False

    force_option = "-F"
    if fs_type == "xfs":
        force_option = "-f"

    cmd = "mkfs.%s " % fs_type
    if force:
        cmd += "%s " % force_option
    cmd += device_name
    retcode, output = run(cmd, return_output=True, verbose=True)
    if retcode != 0:
        _print("FAIL: could create filesystem %s on %s" % (fs_type, device_name))
        print output
        return False
    return True

def sync(directory=None):
    """
    """
    cmd = "sync"
    if directory:
        cmd += " %s" % directory
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: could not sync")
        print output
        return False
    return True


def get_free_space(path):
    """
    Get free space of a path.
    Path could be:
    \t/dev/sda
    \t/root
    \t./
    """
    if not path:
        return None

    cmd = "df -B 1 %s" % (path)
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: get_free_space() - could not run %s" % (cmd))
        print output
        return None
    fs_list = output.split("\n")
    # delete the header info
    del fs_list[0]

    if len(fs_list) > 1:
        #Could be the information was too long and splited in lines
        tmp_info = "".join(fs_list)
        fs_list[0] = tmp_info

    #expected order
    #Filesystem    1B-blocks       Used   Available Use% Mounted on
    free_space_regex = re.compile("\S+\s+\d+\s+\d+\s+(\d+)")
    m = free_space_regex.search(fs_list[0])
    if m:
        return int(m.group(1))
    return None

def get_boot_device():
    """
    Return:
    \tboot dev:     eg. sda or mapper/mpatha
    """
    cmd = "df /boot | grep /dev | awk '{print $1}'"
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: run %s" % cmd)
        print output
        return None

    if not output:
        _print("FAIL: Could not find /boot mounted")
        return None

    #Check if it is a multipath device
    device_name = libsan.host.mp.mpath_device_2_mpath_name(output)
    if device_name:
        return device_name
    else:
        output = output.replace("/dev/","")
        output = re.sub("(\S+)\d+", r"\1", output)
        #Could not use method from scsi module due recursive import issue
        #if libsan.host.scsi.is_scsi_device(output):
        if re.match("^sd[a-z]+$", output):
            return output
    #Boot device is not multipath nor SCSI device, just return it
    #_print("FAIL: get_boot_device() - Does not understand %s" % output)
    return output

def get_device_wwid(device):
    """
    Given a SCSI and multiapth device, returns its WWID
    """
    if libsan.host.scsi.is_scsi_device(device):
        return libsan.host.scsi.wwid_of_disk(device)
    else:
        all_mp_info = libsan.host.mp.multipath_query_all()
        if all_mp_info and device in all_mp_info["by_mpath_name"].keys():
            return all_mp_info["by_mpath_name"][device]["wwid"]
    _print("FAIL: get_device_wwid() - Could not find WWID for %s" % device)
    return None


def remove_device_wwid(wwid):
    if not wwid:
        _print("FAIL: remove_device_wwid() - requires wwid as parameter")
        return False

    mpath_wwid =  libsan.host.mp.mpath_name_of_wwid(wwid)
    if mpath_wwid:
        libsan.host.mp.remove_mpath(mpath_wwid)

    scsi_ids_wwid = libsan.host.scsi.scsi_ids_of_wwid(wwid)
    if scsi_ids_wwid:
        for scsi_id in scsi_ids_wwid:
            scsi_name = libsan.host.scsi.get_scsi_disk_name(scsi_id)
            if not scsi_name:
                continue
            _print("INFO: detaching SCSI disk %s" % scsi_name)
            libsan.host.scsi.delete_disk(scsi_name)
    return True

def clear_dmesg():
    """
    """
    cmd = "dmesg --clear"
    if dist_ver() < 7:
        cmd = "dmesg -c"
    run(cmd, verbose=False)
    return True


def get_regex_pci_id():
    regex_pci_id = "(?:([0-0a-f]{4}):){0,1}"    # domain id (optional)
    regex_pci_id += "([0-9a-f]{2})"             # bus id
    regex_pci_id += ":"
    regex_pci_id += "([0-9a-f]{2})"             # slot id
    regex_pci_id += "\."
    regex_pci_id += "(\d+)"                     # function id
    return regex_pci_id

def get_partitions(device):
    """
    Return a list of all parition numbers from the device
    """
    if not device:
        _print("FAIL: get_partitions() - requires device as parameter")
        return None

    cmd = "parted -s %s print" % device
    ret, output = run(cmd, verbose=False, return_output=True)
    if ret !=0:
        #_print("FAIL: get_partitions() - Could not read partition information from %s" % device)
        #print output
        return None

    lines = output.split("\n")
    if not lines:
        return None

    header_regex = re.compile("Number  Start   End     Size    Type")
    partition_regex = re.compile("\s(\d+)\s+\S+")
    partitions = []
    found_header = False
    for line in lines:
        if header_regex.match(line):
            found_header = True
            continue
        if found_header:
            m = partition_regex.match(line)
            if m:
                partitions.append(m.group(1))

    return partitions

def delete_partition(device, partition):
    """
    Delete specific partition from the device
    """
    if not device or not partition:
        _print("FAIL: delete_partition() - requires device and partition as argument")
        return False

    cmd = "parted -s %s rm %s" % (device, partition)
    ret, output = run(cmd, verbose=False, return_output=True)
    if ret !=0:
        _print("FAIL: delete_partition() - Could not delete partition %d from %s" % (partition, device))
        print output
        return False

    return True

def add_repo(name, address):
    """
    Adds yum repository to /etc/yum.repos.d/NAME.repo
    """
    repo = "/etc/yum.repos.d/%s.repo" % name.lower()
    if os.path.isfile(repo):
        _print("INFO: Repo %s already exists." % repo)
        return True

    with open(repo, 'w') as _file:
        _file.write("[%s]\n" % name + "name=%s\n" % name + "baseurl=%s\n" % address + "enabled=1\n" + "gpgcheck=0\n" +
                    "skip_if_unavailable=1\n")

    return True

def del_repo(name):
    """
    Removes yum repository
    """
    repo = '/etc/yum.repos.d/%s.repo' % name.lower()
    if os.path.isfile(repo) and os.remove(repo) is not None:
        _print("WARN: Removing repository %s failed." % repo)
        return False
    return True