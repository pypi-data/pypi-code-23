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

"""ssh.py: Module to handle ssh session."""

__author__      = "Bruno Goncalves"
__copyright__   = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import re #regex
import sys, os, select, socket
import time

def _print(string):
    module_name = __name__
    string = re.sub("DEBUG:", "DEBUG:("+ module_name + ") ", string)
    string = re.sub("FAIL:", "FAIL:("+ module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:("+ module_name + ") ", string)
    string = re.sub("WARN:", "WARN:("+ module_name + ") ", string)
    print string
    if "FATAL:" in string:
        raise RuntimeError(string)
    return

def connect(host, port = 22, user = None, passwd = None, max_attempt = 5):
    """
    Connect to a host using ssh
    The arguments are:
    \thost:                         Hostname
    \tport:                         Port number used to connect
    \tuser:                         username
    \tpasswd:                       Paswword
    \tmax_attempt                   Maximum attempt to connect (default:5)
    Returns:
    \tssh:                  ssh session
    \tNone:                         If there was some problem
    """
    if not user:
        _print("FAIL: connect() needs \"user\" parameter")
        return None
    if not user:
        _print("FAIL: connect() needs \"passwd\" parameter")
        return None

    i = 1
    ssh_session = None
    #Note: paramiko might cause leak descriptor on /dev/urandom, just include when it is necessary
    #https://github.com/paramiko/paramiko/issues/59
    import paramiko
    #Set log location to avoid: http://stackoverflow.com/questions/19152578/no-handlers-could-be-found-for-logger-paramiko
    paramiko.util.log_to_file("/tmp/paramiko.log")
    while True:
        #print "Trying to connect to %s (%i/%i)" % (host, i, max_attempt)
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, 22, user, passwd)
            #print "Connected to %s" % host
            break
        except paramiko.AuthenticationException:
            print "Authentication failed when connecting to %s" % host
            return None
        except:
            print "Could not SSH to %s, waiting for it to start" % host
            i += 1
            time.sleep(2)

        # If we could not connect within time limit
        if i == max_attempt:
            print "Could not connect to %s. Giving up" % host
            return None
    return ssh

def disconnect(ssh_session):
    """
    Disconnect from a ssh session
    The arguments are:
    \tssh_session:                  ssh session, it is return by connect()
    Returns:
    \tTrue:                         If session is disconnected
    \tFalse:                        If there was some problem
    """
    ssh_session.close()
    return True

def run_cmd(ssh_session, cmd, verbose = True, return_output = False, invoke_shell = False, timeout=None, cr="\n", expect=None):
    """
    Run a command to an specific ssh session
    The arguments are:
    \tssh_session:                  ssh session, it is return by connect()
    \\tcmd:                         command to be executed
    \\texpect:                      if invoke_shell is true we try to read until find expect pattern
    Returns:
    \texit status:                  command status code
    \tNone:                         If there was some problem
    """
    error = 0
    stdout_buf = ""
    #by default we use exec_commnad to run a command as it has better control
    #when reading the buffers and supports exit code
    if not invoke_shell:
        for c in cmd if not isinstance(cmd, basestring) else [cmd]:
            chan = ssh_session.get_transport().open_session()
            if not chan:
                _print("FAIL: Could not create a chan")
                if return_output:
                    return 127, None
                return 127

            if timeout:
                #_print("DEBUG: ssh - TODO - set chan timeout to %s" % timeout)
                chan.settimeout(float(timeout))

            if verbose:
                _print("INFO: Running ssh command '%s'" % c)
            try:
                chan.exec_command(c)
                #stdin, stdout, stderr = ssh_session.exec_command(c)
                #stdin, stdout, stderr = ssh_session.send(c)
            except socket.timeout:
                _print("FAIL: ssh - Got timeout (%ds) while executing command: '%s'" % (int(timeout), c))
                ssh_session.close()
                if return_output:
                    return 127, None
                return 127
            except Exception, e:
                _print("FAIL: ssh - Could not execute command: '%s'" % c)
                print "Failed due: %s" % repr(e)
                ssh_session.close()
                if return_output:
                    return 127, None
                return 127

            buff_size = 1024
            stdout_buf = ""
            while not chan.exit_status_ready():
                if chan.recv_ready():
                   stdout_buf += chan.recv(buff_size)
            exit_status = chan.recv_exit_status()
            #Read remaining data after command finished
            while chan.recv_ready():
                stdout_buf += chan.recv(buff_size)

            while chan.recv_stderr_ready():
                stdout_buf += chan.recv_stderr(buff_size)
            chan.close()
            ## Wait for the command to terminate
            #stdout_buf = ""
            #while not stdout.channel.exit_status_ready():
                ## Only print data if there is data to read in the channel
                #if stdout.channel.recv_ready():
                    #rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
                    #if len(rl) > 0:
                        ## Print data from stdout
                        ##print stdout.channel.recv(1024),
                        #stdout_buf += stdout.channel.recv(1024)

            #ret = stdout.channel.recv_exit_status()
            #if ret != 0:
                #stdout_buf += stderr.readline()
                #error += 1

            if exit_status != 0:
                error +=1

            if verbose:
                print stdout_buf

    else:
        #We use invoke_shell in situation where we need to run commands from a single shell
        #for example on cisco we need to run commands after configure terminal
        chan = ssh_session.invoke_shell()
        if not timeout:
            timeout = 60
        chan.settimeout(float(timeout))
        if expect:
            #wait for prompt
            tmp_buf = ''
            while not tmp_buf.endswith(expect):
                resp = chan.recv(9999)
                tmp_buf += resp
                #_print("DEBUG: waiting for prompt: %s" % resp)
        else:
            chan.recv(65535)
        #Handle cmd being a single string or a list of strings
        stdout_buf = ""
        for c in cmd if not isinstance(cmd, basestring) else [cmd]:
            if verbose:
                print "INFO: ssh - sending command \"%s\"" % c
            chan.send(c)
            #\r scape character is needed by ApCon switch
            chan.send(cr)
            time.sleep(1)
            tmp_buf = ""
            if expect:
                while not tmp_buf.endswith(expect):
                    #rl, wl, xl = select.select([chan], [], [], 0.0)
                    #if len(rl) > 0:
                    #    tmp_buf = chan.recv(1024)
                    #    stdout_buf += tmp_buf
                    #    _print("DEBUG: %s" % stdout_buf)
                    tmp_buf = chan.recv(1024)
                    stdout_buf += tmp_buf
                    #_print("DEBUG: %s" % stdout_buf)

            else:
                #Read until we do not receive more bytes
                while True:
                    rl, wl, xl = select.select([chan], [], [], 0.0)
                    if len(rl) > 0:
                        tmp_buf = chan.recv(1024)
                        stdout_buf += tmp_buf
                    else:
                        if verbose:
                            print stdout_buf
                        break
            continue
        chan.close()
        error = 0
        if verbose:
            print stdout_buf


    if return_output:
        return error, stdout_buf

    return error
