#!/usr/bin/env python3
# encoding: utf-8

"""
cessa.profile
=============

This module implements the basic operations of seccomp profile.

:Copyright (c) 2017 by hac(Xiao An) <hac@zju.edu.cn>. All Rights Reserved.

"""

import json
from cessa.config import Action, Operator, Arch

class Seccomp(object):

    """ Represents the config for a seccomp profile for syscall restriction.

    """

    def __init__(self, action):
        if action not in Action:
            raise ValueError('Action \'{}\' is unsupported or illegal. Use action in config.Action instead'.format(action))
        self.default_action = action
        self.architectures = []
        self.arch_map = []
        self.syscalls = []

    def _load_rule(self, rule):
        self.syscalls.append(rule)

    def set_arch(self, archs):
        self.architectures += archs

    def add_rules(self, rules_coll):
        """ adds rules into seccomp profile

        :rule: limit rule
        :returns: None

        """
        for rule_coll in rules_coll:
            for r in rule_coll.rules:
                self._load_rule(r)

    def to_json(self):
        """ converts seccomp object to a json object

        :returns: seccomp profile in JSON format
        """
        json_out = {}
        json_out['defaultAction'] = to_str(self.default_action)
        if len(self.architectures) != 0:
            json_out['architectures'] = []
            for arch in self.architectures:
                json_out['architectures'].append(to_str(arch))
        elif len(self.arch_map) != 0:
            pass
        else:
            raise RuntimeError('No architecture is specified for seccomp profile')
        json_out['syscalls'] = []
        for rule in self.syscalls:
            json_out['syscalls'].append(convert(rule))
        return json_out

    def dumps(self):
        """ dumps seccomp object into JSON format string

        :returns: seccomp profile in JSON format

        """
        return json.dumps(self.to_json(), indent=4, sort_keys=True)

def dump_rules(seccomp_file, rule_coll_list, default_action=Action.ERRNO, arch=Arch.X86_64):
    """ dumps rules into disk

    :seccomp_file: seccomp profile pathname
    :rule_list: rule list
    :returns: None

    """
    seccomp = Seccomp(default_action)
    seccomp.set_arch([arch])
    seccomp.add_rules(rule_coll_list)

    try:
        with open(seccomp_file, 'w') as f:
            f.write(seccomp.dumps())
    except:
        raise RuntimeError('Unable to dump rules into file \'{}\''.format(seccomp_file))


def convert(rule):
    """ converts rule into seccomp profile format

    :rule: limit rule
    :returns: dictionary with keys: name, action, args

    """
    res = {}
    res['name'] = rule.name
    res['action'] = to_str(rule.action)
    res['args'] = []
    for cond in rule.conds:
        cond_dict = {}
        cond_dict['index'] = cond.index
        cond_dict['op'] = to_str(cond.operator)
        cond_dict['value'] = cond.value
        cond_dict['valueTwo'] = cond.value2 if cond.value2 != None else 0
        res['args'].append(cond_dict)
    return res


def to_str(item):
    if item in Action:
        return {
            Action.KILL: 'SCMP_ACT_KILL',
            Action.TRAP: 'SCMP_ACT_TRAP',
            Action.ERRNO: 'SCMP_ACT_ERRNO',
            Action.TRACE: 'SCMP_ACT_TRACE',
            Action.ALLOW: 'SCMP_ACT_ALLOW'
        }.get(item, '')
    elif item in Operator:
        return {
            Operator.NOT_EQUAL: 'SCMP_CMP_NE',
            Operator.LESS_THAN: 'SCMP_CMP_LT',
            Operator.LESS_EQUAL: 'SCMP_CMP_LE',
            Operator.EQUAL_TO: 'SCMP_CMP_EQ',
            Operator.GREATER_EQUAL: 'SCMP_CMP_GE',
            Operator.GREATER_THAN: 'SCMP_CMP_GT',
            Operator.MASKED_EQUAL: 'SCMP_CMP_MASKED_EQ'
        }.get(item, '')
    elif item in Arch:
        return {
            Arch.X86: 'SCMP_ARCH_X86',
            Arch.X86_64: 'SCMP_ARCH_X86_64',
            Arch.X32: 'SCMP_ARCH_X32',
            Arch.ARM: 'SCMP_ARCH_ARM',
            Arch.AARCH64: 'SCMP_ARCH_AARCH64',
            Arch.MIPS: 'SCMP_ARCH_MIPS',
            Arch.MIPS64: 'SCMP_ARCH_MIPS64',
            Arch.MIPS64N32: 'SCMP_ARCH_MIPS64N32',
            Arch.MIPSEL: 'SCMP_ARCH_MIPSEL',
            Arch.MIPSEL64: 'SCMP_ARCH_MIPSEL64',
            Arch.MIPSEL64N32: 'SCMP_ARCH_MIPSEL64N32',
            Arch.PPC: 'SCMP_ARCH_PPC',
            Arch.PPC64: 'SCMP_ARCH_PPC64',
            Arch.PPC64LE: 'SCMP_ARCH_PPC64LE',
            Arch.S390: 'SCMP_ARCH_S390',
            Arch.S390X: 'SCMP_ARCH_S390X'
        }.get(item, '')





