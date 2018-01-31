#!/usr/bin/env python3
# encoding: utf-8

from pyke import knowledge_engine
from cessa.config import PROJECT_NAME
from pyke.knowledge_engine import CanNotProve
es_engine = knowledge_engine.engine((None, 'cessa.expert.compiled_krb'))
# es_engine = knowledge_engine.engine((None, 'cessa/compiled_knowledge'))

es_engine.activate('bc_relate')

def get_clabel_list(syscall):
    """ gets all supported clabels of a syscall

    :syscall: syscall name
    :returns: clabel tuple

    """
    try:
        with es_engine.prove_goal('bc_relate.clabel_list({}, $clabel_tuple)'.format(syscall)) as gen:
            for var, _ in gen:
                return var['clabel_tuple']
        return ()
    except Exception:
        raise RuntimeError('Cannot prove goal in get_clabel_list() with syscall = \'{}\''.format(syscall))

def get_all_args(syscall):
    """ gets all arguments' name of one syscall

    :syscall: syscall name
    :returns: argument list

    """
    try:
        with es_engine.prove_goal('bc_relate.arg_list({}, $arg_tuple)'.format(syscall)) as gen:
            for var, _ in gen:
                return var['arg_tuple']
        return ()
    except Exception:
        raise RuntimeError('Cannot prove goal in get_all_args() with syscall = \'{}\''.format(syscall))

def get_accurate_value(arg_name, label):
    """ gets all values of a argument with label specified(in accurate mode)

    :arg_name: argument name
    :label: clabel
    :returns: value tuple

    """
    try:
        with es_engine.prove_goal('bc_relate.accurate_value_tuple({}, {}, $values)'.format(arg_name, label)) as gen:
            for var, _ in gen:
                return var['values']
        return ()
    except Exception:
        raise RuntimeError('Cannot prove goal in get_accurate_value() with arg_name = \'{}\', label = \'{}\''.format(arg_name, label))

def get_value_range(arg_name):
    """ gets all possible value of argument if it has a value range.
    Users have to make sure the argument does have value range!

    :arg_name: argument name
    :returns: value tuple

    """
    try:
        macro_tuple = es_engine.prove_1_goal('bc_relate.all_value({}, $macro_tuple)'.format(arg_name))[0]['macro_tuple']
        return tuple(map(lambda x: get_value(x), macro_tuple))
    except Exception:
        raise RuntimeError('Cannot prove goal in get_arg_type() with arg_name = \'{}\''.format(arg_name))

def get_arg_type(arg_name):
    """ gets argument type from knowledge engine

    :arg_name: argument name
    :returns: type string

    """
    try:
        with es_engine.prove_goal('bc_relate.arg_type({}, $type)'.format(arg_name)) as gen:
            for var, _ in gen:
                return var['type']
            return 'other'
    except Exception:
        raise RuntimeError('Cannot prove goal in get_arg_type() with arg_name = \'{}\''.format(arg_name))

def get_value(c_macro):
    """ gets value of C macro

    :c_macro: macro in C. E.g, AF_INET
    :returns: value of C macro

    """
    # my_goal = goal.compile('bc_relate.get_value($macro)')
    try:
        with es_engine.prove_goal('bc_relate.macro_value({}, $value)'.format(c_macro)) as gen:
            for var, _ in gen:
                return var['value']
            return None
    except Exception:
        raise RuntimeError('Cannot prove goal in get_value() with c_macro = \'{}\''.format(c_macro))

def get_index(arg_name):
    """ gets index of arg_name

        E.g, socket(domain, type, protocol)
        socket_domain's index = 0, socket_type's index = 1, ...

    :arg_name: argument name
    :returns: index

    """
    try:
        with es_engine.prove_goal('bc_relate.arg_index({}, $index)'.format(arg_name)) as gen:
            for var, _ in gen:
                return var['index']
            return None
    except Exception:
        raise RuntimeError('Cannot prove goal in get_index() with arg_name = \'{}\''.format(arg_name))

def get_related_args(arg_name_list):
    """ gets related set from the argument list if exists

    :arg_name_list: argument name list
    :returns: related set or None

    """
    for arg_name in arg_name_list:
        try:
            with es_engine.prove_goal('bc_relate.related_args({}, $arg_name1)'.format(arg_name)) as gen:
                for var, _ in gen:
                    if var['arg_name1'] in arg_name_list:
                        return [arg_name, var['arg_name1']]
        except Exception:
            raise RuntimeError('Cannot prove goal in get_related_args() with arg_name = \'{}\''.format(arg_name))
    return None

def get_custom_clabels(container_name):
    """ gets custom clabels for container by asking user a series of questions according to the question base

    :container_name: container name
    :returns: clabel list

    """
    es_engine.activate('question_rule')
    ans = es_engine.prove_1_goal('questions.hint({}, {}, $ans)'.format(PROJECT_NAME, container_name))
    if not ans[0]['ans']:
        return []

    init_quest = es_engine.prove_1_goal('question_rule.question_by_clabel(INIT, $question)')[0]['question']
    return _get_custom_clabels_by_question(container_name, init_quest)

def _get_custom_clabels_by_question(container_name, question):
    try:
        ans = es_engine.prove_1_goal('questions.{}({}, $ans)'.format(question, container_name))[0]['ans']
    except CanNotProve:
        return []

    if 'none' in ans:
        return []
    clabel_list = list(ans)
    for clabel in ans:
        try:
            with es_engine.prove_goal('question_rule.question_by_clabel({}, $question)'.format(clabel)) as gen:
                for var, _ in gen:
                    new_quest = var['question']
                    clabel_list += _get_custom_clabels_by_question(container_name, new_quest)
        except Exception as e:
            raise e

    return clabel_list
