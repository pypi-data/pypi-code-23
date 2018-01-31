#!/usr/bin/env python3
# encoding: utf-8

"""
cessa.rule
==========

This module implements limit rule class and corresponding interfaces.

: Copyright (c) by hac(Xiao An) <hac@zju.edu.cn>. All Rights Reserved.

"""

import os
import itertools
import copy
import json

from cessa import knowledge
from cessa.trace import retrieve_arg_value
from cessa.config import Action, Operator, Level
from functools import partial

class Rule(object):

    """ Represents a seccomp limit rule

    """

    def __init__(self, syscall, action):
        if action not in Action:
            raise ValueError('Action \'{}\' is unsupported or illegal. Use action in config.Action instead'.format(action))
        self.name = syscall
        self.action = action
        self.conds = []
        self.omit = False

    def __str__(self):
        output = 'Syscall {}'.format(self.name)
        action_str = {
            Action.KILL: ' will be KILLed',
            Action.TRAP: ' will be TRAPed',
            Action.ERRNO: ' will be ERRNOed',
            Action.TRACE: ' will be TRACEd',
            Action.ALLOW: ' will be ALLOWed'
        }.get(self.action, None)
        output += '{}'.format(action_str)

        num = len(self.conds)
        if num > 0:
            output += ' when '
        for i in range(num):
            output += '{} and '.format(self.conds[i]) if i < num - 1 else '{}.'.format(self.conds[i])
        return output

    def match(self, syscall, index=None, value=None):
        """ determines whether a syscall is matched by this rule

        :syscall: syscall name
        :index: argument index
        :value: argument value
        :returns: True/False

        """
        if self.name != syscall:
            return False
        if len(self.conds) == 0 or index == None or value == None:
            return True
        for cond in self.conds:
            if cond.match(index, value):
                return True
        return False

    def add_condition(self, cond):
        """ adds argument condition.

        :cond: argument condition
        :returns: None

        """
        # Be sure that at most one condition per argument is allowed for now.
        if len(self.conds) != 0:
            for arg in self.conds:
                if arg.index == cond.index:
                    raise ValueError('Unable to add multiple conditions based on the same argument owing to the limitation of libseccomp: adding condition {} to rule {}'.format(cond, self))
        self.conds.append(cond)

class RuleCollection(object):

    """ Represents the collection of all limit rules based on one syscall

    """

    def __init__(self, syscall, level):
        self.name = syscall
        self.level = level
        self.rules = []

    def add_rules(self, rule_list):
        """ user should make sure that all rules in rule_list are generated in the same level with RuleCollection object

        """
        if len(rule_list) == 1 and len(rule_list[0].conds) == 0:
            self.level = Level.NAME
        for rule in rule_list:
            if rule.name == self.name:
                self.rules.append(rule)

class Condition(object):

    """ Represents an argument condition

    """
    def __init__(self, index, op, value, value2=None):
        if index > 5:
            raise ValueError('At most 6 arguments is supported')
        if op not in Operator:
            raise ValueError('Operator \'{}\' is unsupported or illegal. Use operator in config.Operator instead'.format(op))
        if type(value) != int or (value2 != None and type(value2) != int):
            raise ValueError('Only integer value is allowed owing to the limitation of libseccomp')
        if op == Operator.MASKED_EQUAL and value2 == None:
            raise ValueError('Two value is required for operation MASKED_EQUAL')

        self.index = index
        self.operator = op
        self.value = value
        self.value2 = value2 if op == Operator.MASKED_EQUAL else None

    def __str__(self):
        index_str = {
            0: '0th',
            1: '1st',
            2: '2nd',
            3: '3rd',
            4: '4th',
            5: '5th'
        }.get(self.index, None)
        op_str = {
            Operator.NOT_EQUAL: 'is not equal to',
            Operator.LESS_THAN: 'is less than',
            Operator.LESS_EQUAL: 'is less than or equal to',
            Operator.EQUAL_TO: 'is equal to',
            Operator.GREATER_EQUAL: 'is greater than or equal to',
            Operator.GREATER_THAN: 'is greater than',
            Operator.MASKED_EQUAL: 'is masked equal to',
        }.get(self.operator, None)
        value_str = str(self.value) if self.value2 == None else '{} with {}'.format(self.value, self.value2)

        return '{} argument {} {}'.format(index_str, op_str, value_str)

    def match(self, index, value):
        """ determines whether an argument is matched by this condition

        :index: argument index
        :value: argument value
        :returns: True/False

        """
        if self.index != index:
            return False
        return {
            Operator.NOT_EQUAL: value != self.value,
            Operator.LESS_THAN: value < self.value,
            Operator.LESS_EQUAL: value <= self.value,
            Operator.EQUAL_TO: value == self.value,
            Operator.GREATER_EQUAL: value >= self.value,
            Operator.GREATER_THAN: value > self.value,
            Operator.MASKED_EQUAL: (value & self.value2) == self.value if self.value2 != None else False
        }.get(self.operator)


def gen_rules(syscall_list,
              match_action=Action.ALLOW,
              record_dir=None,
              clabel_file=None,
              level=Level.NAME):

    """ generates limit rules according to the preprocessed syscall trace records.

    :syscall_list: list of syscall names
    :match_action: seccomp action to be taken when rule is matched
    :record_dir: directory where program stores the preprocessed trace records.
    :clabel_file: a file where clabel configs for container are stored
    :level: limit level of rules
    :returns: rule collection list

    """
    if record_dir == None:
        return gen_name_rules(syscall_list, match_action)
    if not os.path.isdir(record_dir):
        raise ValueError('\'{}\' is not a directory'.format(record_dir))
    gen_rules_f = {
        Level.NAME: gen_name_rules,
        Level.ARG: gen_arg_rules,
        Level.CLABEL: gen_clabel_rules,
        Level.CUSTOM: gen_custom_rules
    }.get(level, None);
    if gen_rules_f == None:
        raise ValueError('\'{}\' is not a legal level'.format(level))
    return gen_rules_f(syscall_list, match_action, record_dir, clabel_file)

def gen_name_rules(syscall_list, match_action, *unused):
    rule_coll_list = []
    for syscall in syscall_list:
        rule_coll = RuleCollection(syscall, Level.NAME)
        rule_coll.add_rules([Rule(syscall, match_action)])
        rule_coll_list.append(rule_coll)
    return rule_coll_list

def gen_arg_rules(syscall_list,
                  match_action,
                  record_dir,
                  *unused):
    rule_coll_list = []
    for syscall in syscall_list:
        rule_coll = RuleCollection(syscall, Level.ARG)
        rule_coll.add_rules(gen_arg_rule_1(syscall, match_action, record_dir))
        rule_coll_list.append(rule_coll)
    return rule_coll_list

def gen_clabel_rules(syscall_list,
                     match_action,
                     record_dir,
                     clabel_file):
    rule_coll_list = []
    if clabel_file == None:
        return gen_arg_rules(syscall_list, match_action, record_dir)
    clabel_conf = load_clabel_conf(clabel_file)

    for syscall in syscall_list:
        clabel_list = knowledge.get_clabel_list(syscall)
        rule_coll_list.append(gen_clabel_rule_1(syscall, match_action, record_dir, clabel_list, clabel_conf))

    return rule_coll_list

def gen_clabel_rule_1(syscall,
                      match_action,
                      record_dir,
                      clabel_list,
                      clabel_conf
                      ):
    if len(clabel_list) == 0:
        return gen_arg_rules([syscall], match_action, record_dir)[0]

    arg_tuple = knowledge.get_all_args(syscall)
    arg_clabel_value = dict([(arg, set()) for arg in arg_tuple])

    rule_list = gen_arg_rule_1(syscall, match_action, record_dir)
    for lab in set(clabel_list):
        if lab not in clabel_conf['clabels']:
            continue
        for arg in arg_tuple:
            arg_values_with_lab = knowledge.get_accurate_value(arg, lab)
            for macro in arg_values_with_lab:
                value = knowledge.get_value(macro)
                arg_clabel_value[arg].add(value)

    not_matched_values = copy.deepcopy(arg_clabel_value)
    for r in rule_list:
        for arg, value_set in arg_clabel_value.items():
            arg_index = knowledge.get_index(arg)
            for value in value_set:
                if r.match(syscall, arg_index, value):
                    #print(not_matched_values, arg, value)
                    not_matched_values[arg].remove(value)

    for arg, value_set in not_matched_values.items():
        if len(value_set) == 0:
            continue
        rule_list += gen_rule_from_one_arg(syscall, arg, value_set, match_action)

    rule_coll = RuleCollection(syscall, Level.CLABEL)
    rule_coll.add_rules(rule_list)

    return rule_coll

def gen_custom_rules(syscall_list,
                     match_action,
                     record_dir,
                     clabel_file):
    """ generates limit rules by asking user a set of questions

    :syscall_list: list of syscall names
    :match_action: seccomp action to be taken when rule is matched
    :record_dir: directory where program stores the preprocessed trace records.
    :clabel_file: a file where clabel configs for container are stored
    :returns: rule collection list

    """
    rule_coll_list = []
    if clabel_file == None:
        clabel_conf = {'clabels': []}
    else:
        clabel_conf = load_clabel_conf(clabel_file)
    custom_clabel_list = knowledge.get_custom_clabels('containerXXX')
    # new_clabels represents all clabels generated by questions, not by clabel file
    new_clabels = set(custom_clabel_list) - set(clabel_conf['clabels'])
    clabel_conf['clabels'] += custom_clabel_list

    for syscall in syscall_list:
        clabel_list = knowledge.get_clabel_list(syscall)
        rule_coll = gen_clabel_rule_1(syscall, match_action, record_dir, clabel_list, clabel_conf)
        # if the syscall uses some clabel in new_clabels, the level of its rule should be Level.CUSTOM
        if not set(new_clabels).isdisjoint(set(clabel_list)):
            rule_coll.level = Level.CUSTOM
        rule_coll_list.append(rule_coll)

    return rule_coll_list


def gen_arg_rule_1(syscall,
                   match_action,
                   record_dir):
    if (match_action == Action.ALLOW):
        return gen_arg_rule_1_whitelist(syscall, match_action, record_dir)
    else:
        return gen_arg_rule_1_blacklist(syscall, match_action, record_dir)

def gen_arg_rule_1_whitelist(syscall, match_action, record_dir):
    syscall_dir = os.path.join(record_dir, syscall)
    if not os.path.isdir(syscall_dir):
        return gen_name_rules([syscall], match_action)[0].rules
        # raise RuntimeError('\'{}\' is not a directory'.format(syscall_dir))
    arg_value_dict = retrieve_arg_value(syscall, os.path.join(syscall_dir, 'args.uniq.list'))
    arg_value_dict = dict(filter(_arg_is_valid, arg_value_dict.items()))
    if (len(arg_value_dict) == 0):
        return gen_name_rules([syscall], match_action)[0].rules
    arg_name_list = [arg_name for arg_name, _ in arg_value_dict.items()]

    arg_related_set = knowledge.get_related_args(arg_name_list)
    rule_list_list = []
    if arg_related_set == None: # all args are independent
        for arg_name in arg_name_list:
            rule_list_list.append(gen_rule_from_one_arg(syscall, arg_name, arg_value_dict[arg_name], match_action))
    else:
        rule_list_list.append(gen_rule_from_related_args(syscall, arg_related_set, arg_value_dict, match_action))
        for arg_name in arg_name_list:
            if arg_name not in arg_related_set:
                rule_list_list.append(gen_rule_from_one_arg(syscall, arg_name, arg_value_dict[arg_name], match_action))
    return join_rules_list(rule_list_list)

def gen_arg_rule_1_blacklist(syscall, match_action, record_dir):
    """ generates blacklist limit rules for the syscall
    Note that here record_dir is not a directory any more, but a dict of argument value

    :syscall: syscall name
    :match_action: seccomp action to be taken when rule is matched
    :record_dir: a dict of argument value
    :returns: rule list

    """
    arg_value_dict = record_dir # Be careful! This only work in blacklist mode!
    arg_value_dict = dict(filter(_arg_is_valid, arg_value_dict.items()))
    if (len(arg_value_dict) == 0):
        return gen_name_rules([syscall], match_action)[0].rules
    arg_name_list = [arg_name for arg_name, _ in arg_value_dict.items()]

    rule_list = []
    for arg_name in arg_name_list:
        rule_list += gen_rule_from_one_arg(syscall, arg_name, arg_value_dict[arg_name], match_action)
    return rule_list


def gen_rule_from_one_arg(syscall, arg_name, arg_value_list, match_action):
    arg_value_set = set(arg_value_list) # remove duplicate
    arg_type = knowledge.get_arg_type(arg_name)
    f = {
        'range': _gen_rules_range,
        'fd': _gen_rules_fd,
        'bufsize': _gen_rules_bufsize,
        'bitwise': _gen_rules_bitwise,
    }.get(arg_type, None)
    if f != None:
        return f(syscall, arg_name, arg_value_set, match_action)
    return []

def gen_rule_from_related_args(syscall, arg_related_set, arg_value_dict, match_action):
    rule_list = []
    value_pair_list = []
    arg1, arg2 = arg_related_set
    arg1_value_list = arg_value_dict[arg1]
    arg2_value_list = arg_value_dict[arg2]

    for i in range(len(arg_value_dict[arg1])):
        value_pair = (arg1_value_list[i], arg2_value_list[i])
        if value_pair in value_pair_list:
            continue
        else:
            value_pair_list.append(value_pair)
            arg1_rules = gen_rule_from_one_arg(syscall, arg1, [arg1_value_list[i]], match_action)
            arg2_rules = gen_rule_from_one_arg(syscall, arg2, [arg2_value_list[i]], match_action)
            if len(arg1_rules) == len(arg2_rules) == 1:
                rule_list.append(join_rules(arg1_rules+arg2_rules))
            else:
                raise RuntimeError('Cannot generate related rules for these two arguments {}'.format(arg_related_set))
    return rule_list

def join_rules_list(rule_list_list):
    final_rule_list = []
    combined_rules_list = itertools.product(*rule_list_list)
    for rule_list in combined_rules_list:
        final_rule_list.append(join_rules(rule_list))
    return final_rule_list

def join_rules(rule_list):
    if len(rule_list) == 0:
        raise RuntimeError('Rule list is empty')
    elif len(rule_list) == 1:
        return rule_list[0]
    final_rule = copy.deepcopy(rule_list[0])
    for rule in rule_list[1:]:
        for cond in rule.conds:
            final_rule.add_condition(cond)
    return final_rule


def _gen_multiple_rules(syscall, action, arg_index, op, value_list):
    """ generates multiple rules(for the same argument and the same operator) automatically

    :syscall: syscall name
    :action: the action towards this rules
    :arg_name: the index of argument
    :op: operator
    :value_list: value list of argument
    :returns: rule list

    """
    rule_list = []
    for value in value_list:
        rule = Rule(syscall, action)
        rule.add_condition(Condition(arg_index, op, value))
        rule_list.append(rule)
    return rule_list

def _gen_rules_range(syscall, arg_name, value_set, match_action):
    """ generates rules for arguments with 'range' type

    :syscall: syscall name
    :arg_name: argument name
    :value_set: argument value set recorded by sysdig
    :returns: rule list

    """
    rule_list = []
    arg_index = knowledge.get_index(arg_name)
    gen_f = partial(_gen_multiple_rules, syscall, match_action, arg_index)

    # blacklist
    if match_action != Action.ALLOW:
        return gen_f(Operator.EQUAL_TO, value_set)

    if len(value_set) <= 3:
        rule_list += gen_f(Operator.EQUAL_TO, value_set)
    else:
        all_value_range = knowledge.get_value_range(arg_name)
        if len(value_set) >= len(all_value_range) - 3:
            non_value_set = {x for x in all_value_range if x not in value_set}
            rule_list += gen_f(Operator.EQUAL_TO, non_value_set)
        else:
            max_v, min_v = max(value_set), min(value_set)
            smaller_num = len([v for v in all_value_range if v < min_v])
            larger_num = len([v for v in all_value_range if v > max_v])
            if smaller_num > larger_num:
                rule_list += gen_f(Operator.GREATER_EQUAL, {min_v})
            else:
                rule_list += gen_f(Operator.LESS_EQUAL, {max_v})
    return rule_list

def _gen_rules_fd(syscall, arg_name, value_set, match_action):
    """ generates rules for arguments with 'fd' type

    :syscall: syscall name
    :arg_name: argument name
    :value_set: argument value set recorded by sysdig
    :returns: rule list

    """
    arg_index = knowledge.get_index(arg_name)

    value_set = set(filter(lambda fd: fd <= 0x7FFFFFFF, value_set))
    max_fd = 1 << max(value_set).bit_length()

    # blacklist mode
    if match_action != Action.ALLOW:
        return _gen_multiple_rules(syscall, match_action, arg_index, Operator.GREATER_THAN, {max_fd})

    return _gen_multiple_rules(syscall, match_action, arg_index, Operator.LESS_EQUAL, {max_fd})

def _gen_rules_bufsize(syscall, arg_name, value_set, match_action):
    """ generates rules for arguments with 'bufsize' type

    :syscall: syscall name
    :arg_name: argument name
    :value_set: argument value set recorded by sysdig
    :returns: rule list

    """
    arg_index = knowledge.get_index(arg_name)
    max_size = max(value_set)
    if max_size != 0:
        max_size -= 1
    limit_size = 1 << max_size.bit_length()

    # blacklist mode
    if match_action != Action.ALLOW:
        return _gen_multiple_rules(syscall, match_action, arg_index, Operator.GREATER_THAN, {limit_size})

    return _gen_multiple_rules(syscall, match_action, arg_index, Operator.LESS_EQUAL, {limit_size})

def _gen_rules_bitwise(syscall, arg_name, value_set, match_action):
    """ generates rules for arguments with 'bufsize' type

    :syscall: syscall name
    :arg_name: argument name
    :value_set: argument value set recorded by sysdig
    :returns: rule list

    """
    arg_index = knowledge.get_index(arg_name)

    # blacklist mode
    if match_action != Action.ALLOW:
        rule_list = []
        for value in value_set:
            rule = Rule(syscall, match_action)
            rule.add_condition(Condition(arg_index, Operator.MASKED_EQUAL, value, value))
            rule_list.append(rule)
        return rule_list

    powers = 0;
    for value in value_set:
        all_powers = _powers_of_2(value)
        for x in all_powers:
            powers |= x
    powers ^= int('0xFFFFFFFF', base=16)
    rule = Rule(syscall, match_action)
    rule.add_condition(Condition(arg_index, Operator.MASKED_EQUAL, 0, powers))
    return [rule]

def _powers_of_2(num):
    powers = []
    i = 1
    while (i <= num):
        if i & num != 0:
            powers.append(i)
        i <<= 1
    return powers

def _arg_is_valid(arg_dict_item):
    valid_args = ['bitwise', 'bufsize', 'range']
    arg_name, _ = arg_dict_item
    arg_type = knowledge.get_arg_type(arg_name)
    return arg_type in valid_args

def load_clabel_conf(clabel_file):
    """ loads clabel config into json object

    :returns: JSON object

    """
    return json.load(open(clabel_file, 'r'))
