# !/usr/bin/env python3
# encoding: utf-8

"""
cessa.trace
===========

This module implements container class and corresponding methods for tracing containers.

:Copyright (c) by hac(Xiao An) <hac@zju.edu.cn>. All Rights Reserved.

"""

import subprocess
import os.path
import logging
import shutil
import re
import json
from os import makedirs
from time import sleep
from cessa import docker
from cessa.config import SYSDIG_CONF_FILE


class Container(object):

    """ Stores key info for a container to be traced, particularly, workload scripts.

    """

    def __init__(self, name, image_id):
        container_id = docker.query_container(name)
        if container_id != None:
            raise ValueError('Conflict. The contianer name {} is already in use by container {}'.format(name, container_id))
        self.name = name
        if docker.query_image(image_id) == None:
            raise ValueError('Unable to find image {} locally'.format(image_id))
        self.image_id = image_id

        self.opts = []
        self.rules = None
        self.workload = None
        self.seccomp = None

    def set_option(self, opts):
        """ sets options for running container without checking their correctness!

        :opts: options
        :returns: None
        """
        self.opts += opts

    def set_workload(self, script_file):
        """ sets workload script for testing container.

        :script_file: EXECUTABLE workload script file(absolute path)
        :returns: None

        """
        if not os.path.isfile(script_file):
            raise RuntimeError('Workload script \'{}\' not exists'.format(script_file))
        self.workload = script_file

    def set_seccomp(self, profile):
        """ sets seccomp profile for limiting container.

        :profile: seccomp profile(path)
        :returns: None

        """
        if not os.path.isfile(profile):
            raise ValueError('Seccomp profile \'{}\' not exists'.format(profile))
        self.seccomp = profile

    def set_rules(self, rule_coll_list):
        """ sets seccomp limit rules for container

        :rule_coll_list: list of rule collection
        :returns: None

        """
        if len(rule_coll_list) == 0:
            raise ValueError('Cannot set empty rule list for container')
        self.rules = rule_coll_list

    def del_rules(self, syscall):
        """ deletes all limit rules based on the syscall

        :syscall: syscall name
        :returns: None

        """
        self.rules = list(filter(lambda rule_coll: rule_coll.name != syscall, self.rules))

    def get_rules(self, syscall):
        """ gets all limit rules based on the syscall

        :syscall: syscall name
        :returns: rule collection

        """
        for rule_coll in self.rules:
            if rule_coll.name == syscall:
                return rule_coll

    def add_rules(self, rule_coll):
        """ adds a rule collection

        :rule_coll: rule collection based on one syscall
        :returns: None

        """
        for r_c in self.rules:
            if r_c.name == rule_coll.name:
                raise ValueError('Rule collection on syscall \'{}\' already exists. You should remove it before add a new one.'.format(r_c.name))
        self.rules.append(rule_coll)

    def run(self, with_seccomp=False):
        """ runs container

        :with_seccomp: whether to use seccomp profile
        :returns: Popen object

        """
        cmd = ['docker', 'run', '-d']
        if with_seccomp and self.seccomp != None:
            cmd += ['--security-opt', 'seccomp={}'.format(self.seccomp)]
        cmd += ['--name', self.name]
        if len(self.opts) != 0:
            cmd += self.opts
        cmd.append(self.image_id)
        p = subprocess.Popen(cmd,
                             stdout = subprocess.PIPE,
                             stderr = subprocess.PIPE,
                             universal_newlines = True)
        # sleep(0.1)
        if p.wait() > 0:
            _, err = p.communicate()
            raise RuntimeError('Unable to run container {} with command \'{}\''.format(self.name, cmd), err)

    def exec_workload(self):
        """ execute the workload script of container
        :returns: None

        """
        if self.workload == None:
            raise RuntimeError('No workload script specified for container \'{}\''.format(self.name))
        if not os.path.isfile(self.workload):
            raise RuntimeError('Workload script \'{}\' not exists'.format(self.workload))
        cmd = [self.workload]
        p = subprocess.Popen(cmd,
                             stdout = subprocess.PIPE,
                             stderr = subprocess.PIPE,
                             universal_newlines = True)
        return p.wait()

    def remove(self, force=True):
        """ removes container
        :returns: None

        """
        cmd = ['docker', 'rm']
        if force: cmd.append('-f')
        cmd.append(self.name)
        p = subprocess.run(cmd,
                           stdout = subprocess.PIPE,
                           stderr = subprocess.PIPE,
                           universal_newlines = True)
        if p.returncode != 0:
            raise RuntimeError('Unable to remove container {} with command \'{}\''.format(self.name, cmd), p.stderr)

def start_sysdig(container_name, out_fp):
    """ starts sysdig to trace syscalls.

    :container_name: container name
    :out_fp: file object for storing traced syscalls
    :returns: Popen object

    """
    cmd = ['sysdig', 'container.name = {}'.format(container_name), 'and', 'syscall.type exists']
    p = subprocess.Popen(cmd,
                         stdout = out_fp,
                         stderr = subprocess.PIPE,
                         universal_newlines = True)
    if None != p.poll() > 0:
        _, err = p.communicate()
        raise RuntimeError('Unable to start sysdig with command \'{}\''.format(cmd), err)
    return p

def track_container(container, trace_file, record_dir):
    trace_syscall(container, trace_file)
    return data_preprocessing(trace_file, record_dir)

def trace_syscall(container, trace_file):
    """ uses sysdig to trace container's syscall with executing workload script.

    :container: container to be traced
    :trace_file: file path for storing traced syscalls
    :returns: None

    """
    # two exceptions here: start_sysdig error and open_file error. Catch them!
    try:
        sysdigp = start_sysdig(container.name, open(trace_file, 'w'))
        container.run()
        # wait for starting container
        # sleep(1)
        container.exec_workload()
        # wait for sysdig recording workload syscall
        # sleep(3)
        sysdigp.kill()
        container.remove()
    except Exception as e:
        print(logging.exception(e))
        raise RuntimeError('Unable to trace container \'{}\''.format(container.name))

def data_preprocessing(trace_file, out_dir):
    """ preprocesses trace file and separates syscall records by sort-uniq

    :trace_file: file with syscall trace
    :out_dir: output directory for separated syscall records
    :returns: syscall list

    """
    if not os.path.isdir(out_dir):
        try:
            makedirs(out_dir)
        except:
            raise ValueError('Unable to create directory \'{}\''.format(out_dir))
    syscall_info = {}
    syscall_list = set()
    try:
        sysdig_conf = load_sysdig_conf(SYSDIG_CONF_FILE)
        for line in open(trace_file, 'r'):
            mark, name, *args = line.split()[5:]
            # '>' means syscall entry, '<' means syscall return
            if mark == '>':
                if name in sysdig_conf['abandon']:
                    continue
                name, args = correct_syscall(name, args, sysdig_conf)
                syscall_list.add(name)
                if syscall_info.get(name, None) == None:
                    syscall_info[name] = [args]
                else:
                    syscall_info[name].append(args)
        # dump into file
        # then, sort and uniq
        for name, args_list in syscall_info.items():
            syscall_dir = os.path.join(out_dir, name)
            syscall_file = os.path.join(syscall_dir, 'args.list')
            if os.path.exists(syscall_dir):
                shutil.rmtree(syscall_dir)
            makedirs(syscall_dir)
            with open(syscall_file, 'w') as fp:
                for args in args_list:
                    if len(args) != 0: fp.write('{}\n'.format(' '.join(args)))

            syscall_uniq_file = os.path.join(syscall_dir, 'args.uniq.list')
            cmd = ['sort {} | uniq -c | sort -nr > {}'.format(syscall_file, syscall_uniq_file)]
            p = subprocess.run(cmd,
                               shell = True,
                               stdout = subprocess.PIPE,
                               stderr = subprocess.PIPE,
                               universal_newlines = True)
            if p.returncode != 0:
                raise RuntimeError('Unable to sort syscall records with command \'{}\''.format(cmd))
    except Exception as e:
        raise e
    return syscall_list


def retrieve_arg_value(syscall, arg_record_file):
    """ retrieves argument values from a preprocessed record file

    :syscall: the name of system call
    :arg_record_file: output file of data_preprocessing()
    :returns: dictionary with key=combination of syscall name and arg name, value=list of arg value

    """
    arg_value_dict = {}
    sysdig_conf = load_sysdig_conf(SYSDIG_CONF_FILE)
    for line in open(arg_record_file, 'r'):
        _, *arg_list = line.split()
        for arg in arg_list:
            p = re.match("(\w+)=(\d+).*", arg)
            if p == None:
                continue
            arg_name, arg_value = p.group(1), int(p.group(2))
            # _, arg_name = correct_syscall(syscall, arg_name, sysdig_conf)
            arg_name = syscall + '_' + arg_name
            if arg_value_dict.get(arg_name, None) == None:
                arg_value_dict[arg_name] = [arg_value]
            else:
                arg_value_dict[arg_name].append(arg_value)
    return arg_value_dict

def load_sysdig_conf(sysdig_file):
    """ loads sysdig config into json object

    :returns: JSON object

    """
    return json.load(open(sysdig_file, 'r'))

def correct_syscall(syscall, args, conf):
    """ corrects syscall name and argument name
    This method makes sense because sysdig produces syscall/argument names which are conflicting with linux man page.

    :syscall: syscall name
    :args: argument list
    :returns: correct syscall and correct args

    """
    if conf['correct'].get(syscall, None) == None:
        return syscall, args
    syscall_conf = conf['correct'][syscall]

    includes_conf = None
    syscall = syscall_conf['name']
    if syscall_conf.get('includes', None) != None:
        includes_conf = syscall_conf['includes']

    newargs = []
    for arg in args:
        p = re.match("(\w+)=(\d+).*", arg)
        if p == None:
            continue
        arg_name = p.group(1)
        if includes_conf != None and includes_conf.get(arg_name, None) != None:
            syscall = includes_conf[arg_name]
        if syscall_conf['arguments'].get(arg_name, None) == None:
            newargs.append(arg)
        else:
            newargs.append(arg.replace(arg_name, syscall_conf['arguments'][arg_name]))
    return syscall, newargs
