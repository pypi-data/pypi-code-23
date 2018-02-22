#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: WangShuang
Date: 2018-01-04T16:02:37+8:00
Desc: 实现对json的扁平化操作
'''
import re

_list_index_pattern = re.compile('^([1-9][0-9]*|0)$')

def flatten_json(nested_json, sep='.', *, key_prefix=''):
    '''
    实现对json的扁平化，无论多深层级的json，都会变成一层
    '''
    ret = {}

    def _flatten_json(nested_json_, key_prefix_):
        # 空dict，list保持原样
        if not nested_json_:
            ret[key_prefix_] = nested_json_
        if isinstance(nested_json_, dict):
            for key, value in nested_json_.items():
                if key_prefix_:
                    new_key_prefix_ = key_prefix_ + sep + key
                else:
                    new_key_prefix_ = key
                _flatten_json(value, new_key_prefix_)
        elif isinstance(nested_json_, list):
            for ix, item in enumerate(nested_json_):
                if key_prefix_:
                    new_key_prefix_ = key_prefix_ + sep + str(ix)
                else:
                    new_key_prefix_ = str(ix)
                _flatten_json(item, new_key_prefix_)
        else:
            ret[key_prefix_] = nested_json_
    
    _flatten_json(nested_json, key_prefix)
    return ret 

def select_by_key_path(nested_json, selector):
    '''
    根据selector返回需要的值
    '''
    # 根据selecto构建regex
    pattern = construct_regex_from_selector(selector)

    flattened_json = flatten_json(nested_json)

    selected = {}
    for key, value in flattened_json.items():
        if pattern.match(key):
            selected[key] = value

    # 如果只有一个key符合条件，直接返回值
    # 否则返回所有符合条件的dict
    if len(selected) == 1:
        return selected.popitem()[1]
    else:
        return selected

def _remove_key_prefix(json_, sep):
    '''
    去除key在第一个sep之前的部分
    '''
    key_path = next(iter(json_))
    next_sep_pos = key_path.find(sep) + 1

    ret = {}
    for key, value in json_.items():
        ret[key[next_sep_pos:]] = value

    return ret

def _init_json(key_path, sep):
    keys = key_path.split(sep)

    if len(keys) < 1:
        raise ValueError('%s: key_path不可能小于1')

    # 确定根节点应该为list还是dict
    if _list_index_pattern.match(keys[0]):
        return []
    else:
        return {}

def unflatten_json(flattened_json, sep='.', *, remove_prefix=False):
    '''
    将扁平json恢复原状
    '''
    # 空的dict保持原样
    if not flattened_json:
        return flattened_json

    if remove_prefix:
        flattened_json = _remove_key_prefix(flattened_json, sep)

    key_path = next(iter(flattened_json))
    root = _init_json(key_path, sep)

    sorted_keys = sort_key_paths(flattened_json.keys())
    for key_path in sorted_keys:
        value = flattened_json[key_path]
        upsert_key_path(root, key_path, value)
    
    return root

def sort_key_paths(key_paths, sep='.', *, reverse=False):
    keys_list = [key_path.split(sep) for key_path in key_paths]

    mixed_keys_list = []
    for keys in keys_list:
        keys_ = []
        for key in keys:
            if _list_index_pattern.match(key):
                keys_.append(int(key))
            else:
                keys_.append(key)
        mixed_keys_list.append(keys_)

    sorted_mixed_keys_list = sorted(mixed_keys_list, reverse=reverse)

    ret = []
    for keys in sorted_mixed_keys_list:
        keys_ = []
        for key in keys:
            if isinstance(key, int):
                keys_.append(str(key))
            else:
                keys_.append(key)

        ret.append(sep.join(keys_))

    return ret


def construct_regex_from_selector(selector, sep='.'):
    '''
    将selector转换为正则表达式
    selector有以下几种格式:
    key1.key2 
    key1.2.key2
    key1.*.key2
    key1.key2|key3.key4
    
    支持shell的glob模式
    TODO: 真正把sep用起来，要考虑sep为正则表达式元字符的情况
    '''
    key_path = selector.split('.')

    regex_str = '^'
    list_index_pattern = '([1-9][0-9]*|0)'
    for key in key_path:
        # 支持shell的glob模式
        if '*' in key:
            regex_str += key.replace('*', '.*')
        elif '?' in key:
            regex_str += key.replace('?', '.')
        else:
            # 支持正则表达式的|操作符
            regex_str += ('(' + key + ')')

        regex_str += '\.'

    regex_str = regex_str[:-2]
    return re.compile(regex_str + '$')

def _upsert_last_key(root, key, value):
    '''
    只更新一步
    '''
    if _list_index_pattern.match(key): 
        # list的情况
        if not isinstance(root, list):
            raise TypeError('%s: 该key对应的元素应该为list' % key)
        index = int(key)
        len_ = len(root)
        if index < len_:
            root[index] = value
        elif index == len_:
            root.append(value)
        else:
            raise IndexError('list的长度为%d，而索引为%d' % (len_, index))
    elif isinstance(root, dict):
        root[key] = value
    else:
        raise TypeError('%s既不是list也不是dict，不支持对该类型元素进行更深的修改' % type(root))

def _init_node(key):
    if _list_index_pattern.match(key): 
        return []
    else:
        return {}

def upsert_key_path(root, key_path, value, sep='.'):
    '''
    根据key_path更新root的值为value
    如果指定的key_path不存在，会在校验后新建
    '''
    keys = key_path.split(sep)
    key = keys[0]

    if not key:
        raise ValueError('%s: 当前key为空' % key)

    if len(keys) == 1:
        _upsert_last_key(root, key, value)
    else:
        if _list_index_pattern.match(key): 
            if not isinstance(root, list):
                raise TypeError('%s: 该key对应的元素应该为list' % key)
            index = int(key)
            len_ = len(root)
            if index < len_:
                child = root[index]
            elif index == len_:
                child = _init_node(keys[1])
                root.append(child)
            else:
                raise IndexError('list的长度为%d，而索引为%d' % (len_, index))
        elif isinstance(root, dict):
            if key in root:
                child = root[key]
            else:
                child = _init_node(keys[1]) 
                root[key] = child
        else:
            raise TypeError('%s既不是list也不是dict，不支持对该类型元素进行更深的修改' % type(root))

        child_key_path = sep.join(keys[1:])
        upsert_key_path(child, child_key_path, value, sep)

def delete_key_path(root, key_path, sep='.'):
    '''
    删除key_path指定的值
    如果指定的key_path不存在，会抛出KeyError或者IndexError异常
    '''
    keys = key_path.split(sep)
    key = keys[0]
    
    if not key:
        raise ValueError('%s: 当前key为空' % key)
    
    if len(keys) == 1:
        if _list_index_pattern.match(key):
            if not isinstance(root, list):
                raise TypeError('%s: 该key对应的元素应该为list' % key)
            index = int(key)
            del root[index]
        elif  isinstance(root, dict):
            del root[key]
        else: 
            raise TypeError('%s: 根节点类型不对' % str(root))
    else:
        if _list_index_pattern.match(key):
            if not isinstance(root, list):
                raise TypeError('%s: 该key对应的元素应该为list' % key)
            index = int(key)
            child = root[index]
        elif  isinstance(root, dict):
            child = root[key]
        else: 
            raise TypeError('%s: 根节点类型不对' % str(root))
        
        child_key_path = sep.join(keys[1:])
        delete_key_path(child, child_key_path, sep)

def test_upsert_key():
    root = {
            'a': [2,3,{'aa': 'sds'},5],
            'b': {'ba': 'ok', 'bb': 'world' },
            'c': 'haola'
            }
    upsert_key_path(root, 'a.2.aa', 100)
    print(root)
    flattened_json = flatten_json(root)
    print(flattened_json)
    unflattened_json = unflatten_json(flattened_json, remove_prefix=False)
    print(unflattened_json)
    delete_key_path(unflattened_json, 'a.2')
    print(unflattened_json)


def test_flatten():
    nested_json = {
        "a": 1,
        "b": [35, 26],
        "c": [{
                "d": [2, 3, 4],
                "e": [
                    {
                        "f": 1,
                        "g": 2
                        }
                    ]
            }],
        "h": {}
        }

    from pprint import pprint
    flattened_json = flatten_json(nested_json)
    pprint(flattened_json)

if __name__ == "__main__":
    # test_upsert_key()
    # test_construct_regex()
    test_flatten()
