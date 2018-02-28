import sys, copy, yaml, pprint
import simplejson as json
sys.path.append("../pukala")
from pukala import grow, ContextBase, PukalaBaseException
from fs_binding import FsBinding

def empty_doc():
    assert(grow({}, None) == {})

def no_fcalls():
    data = {"hello": {"world": [1, 2, "3"]}}
    d2 = copy.deepcopy(data)
    assert(grow(data, None) == d2)

def single_evaluation():
    class CC(object):
        def get_world(self, context):
            return "world"
    data = {"hello": ["_fcall", "get_world"]}

    gr = grow(data, CC())
    assert(gr ==
           {'hello': 'world',
            '_history': {'fcalls_evaluated': [
                ['single_call', 'get_world', ['hello']]
            ]}})

def two_sibling_evaluations():
    class CC(object):
        def get_world(self, context):
            return "world"
        def get_world2(self, context):
            return "world2"

    data = {
        "hello": ["_fcall", "get_world"],
        "hello2": ["_fcall", "get_world2"]
    }
    gr = grow(data, CC())
    assert(gr ==
           {'hello': 'world',
            'hello2': 'world2',
            '_history': {'fcalls_evaluated': [
                ['single_call', 'get_world', ['hello']],
                ['single_call', 'get_world2', ['hello2']],
            ]}})

def two_sibling_cgroup_evaluation():
    class CC(object):
        def get_world(self, context):
            return "world"
        def get_world2(self, context):
            return "world2"

    data = {
        "hello": ["_fcall", {"cgroup": "welcomer"}, "get_world"],
        "hello2": ["_fcall", {"cgroup": "welcomer"}, "get_world2"]
    }
    gr = grow(data, CC())
    assert(gr ==
           {'hello': 'world',
            'hello2': 'world2',
            '_history': {'fcalls_evaluated': [
                ['cgroup_single', 'welcomer', 'get_world', ['hello']],
                ['cgroup_single', 'welcomer', 'get_world2', ['hello2']],
            ]}} or gr ==
           {'hello': 'world',
            'hello2': 'world2',
            '_history': {'fcalls_evaluated': [
                ['cgroup_single', 'welcomer', 'get_world2', ['hello2']],
                ['cgroup_single', 'welcomer', 'get_world', ['hello']],
            ]}})

def fcall_returns_fcall():
    class CC(object):
        def get_world(self, context):
            return ["_fcall", "get_world2"]
        def get_world2(self, context):
            return "world"
    data = {"hello": ["_fcall", "get_world"]}
    gr = grow(data, CC())
    assert(gr ==
           {'hello': 'world',
            '_history': {'fcalls_evaluated': [
                ['single_call', 'get_world', ['hello']],
                ['single_call', 'get_world2', ['hello']]
            ]}})

def context_path_is_correct():
    class CC(object):
        def get_world(self, context):
            return context.path.as_arr()
    data = {"hello": {"hello1": ["_fcall", "get_world"]}}
    gr = grow(data, CC())
    assert(gr ==
           {'hello': {'hello1': ['hello', "hello1"]},
            '_history': {'fcalls_evaluated': [
                ['single_call', 'get_world', ['hello', 'hello1']]
            ]}})

def simple_doc_immutability():
    class CC(object):
        def get_world(self, context):
            context.doc["bubu"] = 123
            return "world"
    data = {"hello": {"hello1": ["_fcall", "get_world"]}}
    dd = copy.deepcopy(data)
    gr = grow(data, CC())
    assert(data == dd)
    assert(gr ==
           {'hello': {'hello1': 'world'},
            '_history': {'fcalls_evaluated': [
                ['single_call', 'get_world', ['hello', 'hello1']]
            ]}})

def nested_fcalls():
    class CC(object):
        def get_world(self, context):
            assert(context.path.as_arr() == ['hello', 'hello1'])
            return "".join(context.args)
        def get_letters(self, context):
            assert(context.path.as_arr() == ['hello', 'hello1'])
            return context.args[0]

    data = {"hello": {"hello1": ["_fcall", "get_world",
                                 ["_fcall", "get_letters", "wor"],
                                 ["_fcall", "get_letters", [
                                     "_fcall", "get_letters", "ld"
                                 ]],
                             ]}}
    gr = grow(data, CC())
    assert(gr ==
           {'hello': {'hello1': 'world'},
            '_history': {'fcalls_evaluated': [
                ['single_call', 'get_world', ['hello', 'hello1']]
            ]}})

def fcall_order_priority():
    class CC(object):
        def get_world(self, context):
            return True

    data = {
        "min_priority": ["_fcall", {"priority": -1000}, "get_world"],
        "max_priority": ["_fcall", {"priority": 1000}, "get_world"]
    }
    gr = grow(data, CC())
    assert(gr ==
           {'min_priority': True,
            'max_priority': True,
            '_history': {'fcalls_evaluated': [
                ['single_call', 'get_world', ['max_priority']],
                ['single_call', 'get_world', ['min_priority']],
            ]}})

def fcall_order_depth():
    class CC(object):
        def get_world(self, context):
            return True

    data = {
        "abra": {
            "min_priority": ["_fcall", "get_world"],
        },
        "max_priority": ["_fcall", "get_world"]
    }
    gr = grow(data, CC())
    assert(gr ==
           {'abra': {'min_priority': True},
            'max_priority': True,
            '_history': {'fcalls_evaluated': [
                ['single_call', 'get_world', ['max_priority']],
                ['single_call', 'get_world', ['abra', 'min_priority']],
            ]}})

def fcall_order_path_alphabet():
    class CC(object):
        def get_world(self, context):
            return True

    data = {
        "ddd": ["_fcall", "get_world"],
        "ccc": ["_fcall", "get_world"],
        "bbb": ["_fcall", "get_world"],
        "aaa": ["_fcall", "get_world"],
    }
    gr = grow(data, CC())
    assert(gr ==
           {'aaa': True,
            'bbb': True,
            'ccc': True,
            'ddd': True,
            '_history': {'fcalls_evaluated': [
                ['single_call', 'get_world', ['aaa']],
                ['single_call', 'get_world', ['bbb']],
                ['single_call', 'get_world', ['ccc']],
                ['single_call', 'get_world', ['ddd']],

            ]}})

def fcall_order_fcall_name():
    class CC(object):
        def aaa(self, context):
            return True
        def bbb(self, context):
            return True
        def ccc(self, context):
            return True
        def ddd(self, context):
            return True

    data = {
        "ddd": ["_fcall", "ddd"],
        "ccc": ["_fcall", "ccc"],
        "bbb": ["_fcall", "bbb"],
        "aaa": ["_fcall", "aaa"],
    }
    gr = grow(data, CC())
    assert(gr ==
           {'aaa': True,
            'bbb': True,
            'ccc': True,
            'ddd': True,
            '_history': {'fcalls_evaluated': [
                ['single_call', 'aaa', ['aaa']],
                ['single_call', 'bbb', ['bbb']],
                ['single_call', 'ccc', ['ccc']],
                ['single_call', 'ddd', ['ddd']],
            ]}})
    

def fcall_order_all():
    class CC(object):
        def aaa(self, context):
            return True
        def bbb(self, context):
            return True
        def ccc(self, context):
            return True
        def ddd(self, context):
            return True
        def zzz(self, context):
            return {
                "zzz2": ["_fcall", {"priority": 100}, "zzz2"],
                "aaa": ["_fcall", "aaa"]
            }
        def zzz2(self, context):
            return True

    data = {
        "zzz": ["_fcall", {"priority": 1000}, "zzz"],
        "ddd": ["_fcall", "ddd"],
        "ccc": ["_fcall", "ccc"],
        "bbb": ["_fcall", "bbb"],
    }
    gr = grow(data, CC())
    assert(gr["_history"]['fcalls_evaluated'] == [
                ['single_call', 'zzz', ['zzz']],
                ['single_call', 'zzz2', ['zzz', 'zzz2']],
                ['single_call', 'bbb', ['bbb']],
                ['single_call', 'ccc', ['ccc']],
                ['single_call', 'ddd', ['ddd']],
                ['single_call', 'aaa', ['zzz', 'aaa']],
            ])

def cgroup_non_cgroup_mix():
    class CC(object):
        def get_world(self, context):
            return "world"
        def get_world2(self, context):
            return "world2"

    data = {
        "hello": ["_fcall", {"cgroup": "welcomer"}, "get_world"],
        "hello2": ["_fcall", {"cgroup": "welcomer"}, "get_world2"],
        "hello3": ["_fcall", "get_world"],
        "hello4": ["_fcall", "get_world2"]
    }
    gr = grow(data, CC())
    assert(gr ==
           {'hello': 'world',
            'hello2': 'world2',
            'hello3': 'world',
            'hello4': 'world2',
            '_history': {'fcalls_evaluated': [
                ['cgroup_single', 'welcomer', 'get_world', ['hello']],
                ['cgroup_single', 'welcomer', 'get_world2', ['hello2']],
                ['single_call', 'get_world', ['hello3']],
                ['single_call', 'get_world2', ['hello4']],
            ]}} or gr ==
           {'hello': 'world',
            'hello2': 'world2',
            'hello3': 'world',
            'hello4': 'world2',
            '_history': {'fcalls_evaluated': [
                ['cgroup_single', 'welcomer', 'get_world2', ['hello2']],
                ['cgroup_single', 'welcomer', 'get_world', ['hello']],
                ['single_call', 'get_world', ['hello3']],
                ['single_call', 'get_world2', ['hello4']],
            ]}})

def fcall_returning_none():
    class CC(object):
        def get_world(self, context):
            return None
    data = {"hello": ["_fcall", "get_world"]}
    gr = grow(data, CC())
    assert(gr ==
           {'hello': None,
            '_history': {'fcalls_evaluated': [
                ['single_call', 'get_world', ['hello']]
            ]}})

def base_do_if():
    class CC(ContextBase):
        def get_world(self, context):
            return "world"
    data = {"hello": ["_fcall", "do_if",
                      ["_fcall", "do_eq", 1, 1], '["_fcall", "get_world"]',
                      "universe"],
            "hello2": ["_fcall", "do_if",
                       ["_fcall", "do_eq", 1, 2], "world", "universe"],
            "hello3": ["_fcall", "do_if",
                       ["_fcall", "do_lt", 1, 2], "world", "universe"],

    }
    gr = grow(data, CC())
    assert(gr == {
        'hello2': 'universe',
        'hello3': 'world',
        'hello': 'world', '_history': {
            'fcalls_evaluated': [
                ['single_call', 'do_if', ['hello']],
                ['single_call', 'get_world', ['hello']],
                ['single_call', 'do_if', ['hello2']],
                ['single_call', 'do_if', ['hello3']],
            ]}})

def base_do_getval():
    class CC(ContextBase):
        pass
    data = {
        "hello": ["_fcall", "do_getval", "../templates/item"],
        "hello2": ["_fcall", "do_getval", "/templates/item"],
        "templates": {
            "item": "world"
        }
    }
    gr = grow(data, CC())
    assert(gr == {
        'templates': {'item': 'world'},
        'hello2': 'world',
        'hello': 'world',
        '_history': {'fcalls_evaluated': [
            ['single_call', 'do_getval', ['hello']],
            ['single_call', 'do_getval', ['hello2']]
        ]}})

def base_do_map():
    class CC(ContextBase):
        def get_world(self, context):
            return "world%d_%d" % (context.args[0], context.args[1])
    data = {
        "hello": ["_fcall", "do_map", 5, '["_fcall", "get_world"]']
    }
    gr = grow(data, CC())
    assert(gr == {
        'hello': [
            'world0_0', 'world1_1', 'world2_2',
            'world3_3', 'world4_4'],
        '_history': {'fcalls_evaluated': [
            ['single_call', 'do_map', ['hello']],
            ['single_call', 'get_world', ['hello', 0]],
            ['single_call', 'get_world', ['hello', 1]],
            ['single_call', 'get_world', ['hello', 2]],
            ['single_call', 'get_world', ['hello', 3]],
            ['single_call', 'get_world', ['hello', 4]]
        ]}})

def base_do_fmt():
    data = {
        "hello": ["_fcall", "do_fmt", "world %s %d", "foo", 5]
    }
    gr = grow(data, ContextBase())
    assert(gr == {
        'hello': 'world foo 5',
        '_history': {'fcalls_evaluated':
                     [['single_call', 'do_fmt', ['hello']]]}}
    )

def dict_key_fcall_none():
    class CC(object):
        def get_hello(self, context):
            return None
    data = {'["_fcall", "get_hello"]': "world"}
    gr = grow(data, CC())
    assert(gr == {
        '_history': {'fcalls_evaluated':
                     [['single_call', 'get_hello',
                       ['["_fcall", "get_hello"]']]]}})

def dict_key_fcall_single():
    class CC(object):
        def get_hello(self, context):
            return "hello"
    data = {'["_fcall", "get_hello"]': "world"}
    gr = grow(data, CC())
    assert(gr ==
           {'_history': {'fcalls_evaluated': [
               ['single_call', 'get_hello',
                ['["_fcall", "get_hello"]']]
            ]}, 'hello': 'world'})

def dict_key_fcall_sequence():
    class CC(object):
        def get_hello(self, context):
            return "hello"
        def get_hello2(self, context):
            return "hello2"
        def get_world(self, context):
            return "world"

    data = {'["_fcall", "get_hello"]': {'["_fcall", "get_hello2"]':
                                        ['_fcall', 'get_world']}}

    gr = grow(data, CC())
    assert(gr ==
           {'_history': {'fcalls_evaluated': [
               ['single_call', 'get_hello',
                ['["_fcall", "get_hello"]']],
                
               ['single_call', 'get_hello2',
                ['hello', '["_fcall", "get_hello2"]']],
               
               ['single_call', 'get_world', ['hello', 'hello2']]
            ]}, 'hello': {'hello2': 'world'}})

def ignored_paths():
    class CC(object):
        def get_world(self, context):
            return "world"
        def get_world2(self, context):
            return "world2"

    data = {
        "hello": ["_fcall", "get_world"],
        "hello2": ["_fcall", "get_world2"],
        "hello3": {"hello": ["_fcall", "get_world2"]},
        "hello4": {"hello": ["_fcall", "get_world2"],
                   "hello2": ["_fcall", "get_world"]},

        "_fcall_conf": {
            "ignored": [
                ["path", "/hello2"],
                ["path", "/hello3"],
                ["path", "/hello4/hello"],
            ]
        }
    }
    gr = grow(data, CC())
    assert(gr ==
           {'_history': {'fcalls_evaluated': [
               ['single_call', 'get_world', ['hello']],
               ['single_call', 'get_world', ['hello4', 'hello2']]]},
            'hello': 'world',
            'hello4': {'hello2': 'world', 'hello':
                       ['_fcall', 'get_world2']},
            '_fcall_conf': {'ignored': [
                ['path', '/hello2'],
                ['path', '/hello3'],
                ['path', '/hello4/hello']]},
            'hello2': ['_fcall', 'get_world2'],
            'hello3': {'hello': ['_fcall', 'get_world2']}})

def ignored_fcalls():
    class CC(object):
        def get_world(self, context):
            return "world"
        def get_world2(self, context):
            return "world2"

    data = {
        "hello": ["_fcall", "get_world"],
        "hello2": ["_fcall", "get_world2"],
        "_fcall_conf": {
            "ignored": [
                ["function", "get_world"],
            ]
        }
    }
    gr = grow(data, CC())
    assert(gr == {'_history': {'fcalls_evaluated': [
        ['single_call', 'get_world2', ['hello2']]
    ]},
                  'hello2': 'world2',
                  'hello': ['_fcall', 'get_world'],
                  '_fcall_conf': {'ignored': [['function', 'get_world']]}})


def ignored_cgroup():
    class CC(object):
        def get_world(self, context):
            return "world"
        def get_world2(self, context):
            return "world2"

    data = {
        "hello": ["_fcall", {"cgroup": "welcomer"}, "get_world"],
        "hello2": ["_fcall", {"cgroup": "welcomer"}, "get_world2"],
        "_fcall_conf": {
            "ignored": [
                ["cgroup", "welcomer"],
            ]
        }
    }
    gr = grow(data, CC())
    dd = copy.deepcopy(data)
    assert(gr == dd)

def ignored_regex():
    class CC(object):
        def get_world(self, context):
            return "world"

    data = {
        "hello": {
            "hello2": ["_fcall", {"cgroup": "welcomer"}, "get_world"]
        },
        "_fcall_conf": {
            "ignored": [
                ["regex", "^/hello/.*o2/$"],
            ]
        }
    }
    gr = grow(data, CC())
    dd = copy.deepcopy(data)
    assert(gr == dd)

def ignored_regexi():
    class CC(object):
        def get_world(self, context):
            return "world"

    data = {
        "hello": {
            "hello2": ["_fcall", {"cgroup": "welcomer"}, "get_world"]
        },
        "_fcall_conf": {
            "ignored": [
                ["regexi", "foo"],
            ]
        }
    }
    gr = grow(data, CC())
    dd = copy.deepcopy(data)
    assert(gr == dd)

def ignored_fcalls_evaluating():
    class CC(object):
        def get_world(self, context):
            return "world"
        def get_world2(self, context):
            return "world2"
        def get_ignoreds1(self, context):
            return ["function", "get_world"]
        def get_ignoreds2(self, context):
            return ["function", "get_world2"]

    data = {
        "hello": ["_fcall", {"priority": 1000}, "get_world"],
        "hello2": ["_fcall", "get_world"],
        "hello3": ["_fcall", "get_world2"],

        "_fcall_conf": {
            "ignored": [
                ["_fcall", "get_ignoreds1"],
                [[
                    ["_fcall", "get_ignoreds2"]
                ]]
            ]
        }
    }
    gr = grow(data, CC())
    assert(gr == {
        '_history': {'fcalls_evaluated': [
            ['single_call', 'get_world', ['hello']],
            ['single_call', 'get_ignoreds1', ['_fcall_conf', 'ignored', 0]],
            ['single_call', 'get_ignoreds2', ['_fcall_conf', 'ignored', 1, 0, 0]]]},
        'hello3': ['_fcall', 'get_world2'],
        'hello2': ['_fcall', 'get_world'],
        'hello': 'world',
        '_fcall_conf': {'ignored':
                        [['function', 'get_world'],
                         [[['function', 'get_world2']]]]}})

def strict_keys_exception():
    class CC(object):
        def get_hello(self, context):
            return "hello"
    data = {
        'hello': 123,
        '["_fcall", "get_hello"]': "world"
    }
    try:
        grow(data, CC())
    except PukalaBaseException as e:
        assert(str(e.cause) == "duplicate key hello")

def max_depth_exceeded():
    class CC(object):
        def get_world(self, context):
            return "world"
    data = {
        "hello": {"hello": ["_fcall", "get_world"]},
        "_fcall_conf": {
            "max_depth": 1
        }
    }

    try:
        grow(data, CC())
    except PukalaBaseException as e:
        assert(str(e.cause) == "path size exceeded" and
               e.cause.path.as_arr() == ['hello', 'hello'])

def segmented_fcall_path():
    class Zuu(object):
        def get_world(self, context):
            return "world"

    class Buu(object):
        def __init__(self):
            self.zuu = Zuu()
            
    class CC(object):
        def __init__(self):
            self.buu = Buu()
            
    data = {
        "hello": ["_fcall", "buu.zuu.get_world"]
    }
    gr = grow(data, CC())
    assert(gr == {
        'hello': 'world',
        '_history': {
            'fcalls_evaluated':
            [['single_call', 'buu.zuu.get_world', ['hello']]]}})

def fs_binding_open_folder_with_text_file():
    class CC(object):
        def __init__(self):
            self.fs = FsBinding("fs.", self)

        def get_fs_conf(self, context):
            z = self.fs.get_defaults(context)
            z["ftypes"][-1] = ['^folder://.*$', 'open_folder']
            return z

    data = {
        "fs_conf": ["_fcall", "get_fs_conf"],
        "some_files": ["_fcall", "fs.open_inode", "./dir0",
                       "fs_conf"]
    }
    gr = grow(data, CC())
    correct = """
_history:
  fcalls_evaluated:
  - - single_call
    - get_fs_conf
    - [fs_conf]
  - - single_call
    - fs.open_inode
    - [some_files]
fs_conf:
  ftypes:
  - ['^file://.*~$', ignored]
  - ['^file://.*\.txt$', text]
  - ['^file://.*\.cfg$', text]
  - ['^file://.*\.yml$', yaml]
  - ['^file://.*\.yaml$', yaml]
  - ['^file://.*\.json$', json]
  - ['^file://.*\.xml$', xml]
  - ['^file://.*$', closed_file]
  - ['^folder://.*$', open_folder]
  handlers:
    closed_file: ['["_fcall", "fs.pull_closed_file"]', '["_fcall", "fs.push_closed_file"]']
    closed_folder: ['["_fcall", "fs.pull_closed_folder"]', '["_fcall", "fs.push_closed_folder"]']
    ignored: ['["_fcall", "fs.pull_ignored"]', '["_fcall", "fs.push_ignored"]']
    json: ['["_fcall", "fs.pull_json"]', '["_fcall", "fs.push_json"]']
    open_folder: ['["_fcall", "fs.pull_open_folder"]', '["_fcall", "fs.push_open_folder"]']
    text: ['["_fcall", "fs.pull_text"]', '["_fcall", "fs.push_text"]']
    xml: ['["_fcall", "fs.pull_xml"]', '["_fcall", "fs.push_xml"]']
    yaml: ['["_fcall", "fs.pull_yaml"]', '["_fcall", "fs.push_yaml"]']
some_files:
  contents:
    dir1:
      contents:
        foo.txt:
          contents: [haha, haha2, '']
          ftype: text
      ftype: open_folder
    foo2.txt:
      contents: [bobo, hoho, '']
      ftype: text
  ftype: open_folder
"""
    assert(gr == yaml.load(correct))

def fs_binding_open_yaml():
    class CC(object):
        def __init__(self):
            self.fs = FsBinding("fs.", self)

        def get_fs_conf(self, context):
            z = self.fs.get_defaults(context)
            z["ftypes"][-1] = ['^folder://.*$', 'open_folder']
            return z

    data = {
        "fs_conf": ["_fcall", "get_fs_conf"],
        "some_files": ["_fcall", "fs.open_inode", "./dir1",
                       "fs_conf"]
    }
    gr = grow(data, CC())
    correct = """
_history:
  fcalls_evaluated:
  - - single_call
    - get_fs_conf
    - [fs_conf]
  - - single_call
    - fs.open_inode
    - [some_files]
fs_conf:
  ftypes:
  - ['^file://.*~$', ignored]
  - ['^file://.*\.txt$', text]
  - ['^file://.*\.cfg$', text]
  - ['^file://.*\.yml$', yaml]
  - ['^file://.*\.yaml$', yaml]
  - ['^file://.*\.json$', json]
  - ['^file://.*\.xml$', xml]
  - ['^file://.*$', closed_file]
  - ['^folder://.*$', open_folder]
  handlers:
    closed_file: ['["_fcall", "fs.pull_closed_file"]', '["_fcall", "fs.push_closed_file"]']
    closed_folder: ['["_fcall", "fs.pull_closed_folder"]', '["_fcall", "fs.push_closed_folder"]']
    ignored: ['["_fcall", "fs.pull_ignored"]', '["_fcall", "fs.push_ignored"]']
    json: ['["_fcall", "fs.pull_json"]', '["_fcall", "fs.push_json"]']
    open_folder: ['["_fcall", "fs.pull_open_folder"]', '["_fcall", "fs.push_open_folder"]']
    text: ['["_fcall", "fs.pull_text"]', '["_fcall", "fs.push_text"]']
    xml: ['["_fcall", "fs.pull_xml"]', '["_fcall", "fs.push_xml"]']
    yaml: ['["_fcall", "fs.pull_yaml"]', '["_fcall", "fs.push_yaml"]']
some_files:
  contents:
    some.yaml:
      contents:
        buba: [hehe, 321]
        foo: 123
      ftype: yaml
  ftype: open_folder
"""
    assert(gr == yaml.load(correct))


def fs_binding_open_json():
    class CC(object):
        def __init__(self):
            self.fs = FsBinding("fs.", self)

        def get_fs_conf(self, context):
            z = self.fs.get_defaults(context)
            z["ftypes"][-1] = ['^folder://.*$', 'open_folder']
            return z

    data = {
        "fs_conf": ["_fcall", "get_fs_conf"],
        "some_files": ["_fcall", "fs.open_inode", "./dir2",
                       "fs_conf"]
    }
    gr = grow(data, CC())
    correct = """
_history:
  fcalls_evaluated:
  - - single_call
    - get_fs_conf
    - [fs_conf]
  - - single_call
    - fs.open_inode
    - [some_files]
fs_conf:
  ftypes:
  - ['^file://.*~$', ignored]
  - ['^file://.*\.txt$', text]
  - ['^file://.*\.cfg$', text]
  - ['^file://.*\.yml$', yaml]
  - ['^file://.*\.yaml$', yaml]
  - ['^file://.*\.json$', json]
  - ['^file://.*\.xml$', xml]
  - ['^file://.*$', closed_file]
  - ['^folder://.*$', open_folder]
  handlers:
    closed_file: ['["_fcall", "fs.pull_closed_file"]', '["_fcall", "fs.push_closed_file"]']
    closed_folder: ['["_fcall", "fs.pull_closed_folder"]', '["_fcall", "fs.push_closed_folder"]']
    ignored: ['["_fcall", "fs.pull_ignored"]', '["_fcall", "fs.push_ignored"]']
    json: ['["_fcall", "fs.pull_json"]', '["_fcall", "fs.push_json"]']
    open_folder: ['["_fcall", "fs.pull_open_folder"]', '["_fcall", "fs.push_open_folder"]']
    text: ['["_fcall", "fs.pull_text"]', '["_fcall", "fs.push_text"]']
    xml: ['["_fcall", "fs.pull_xml"]', '["_fcall", "fs.push_xml"]']
    yaml: ['["_fcall", "fs.pull_yaml"]', '["_fcall", "fs.push_yaml"]']
some_files:
  contents:
    foo.json:
      contents:
        !!python/unicode 'hehe':
        - {!!python/unicode 'buba': 123}
        - 321
      ftype: json
  ftype: open_folder
"""
    assert(gr == yaml.load(correct))

def fs_binding_open_xml():
    class CC(object):
        def __init__(self):
            self.fs = FsBinding("fs.", self)

        def get_fs_conf(self, context):
            z = self.fs.get_defaults(context)
            return z

    data = {
        "fs_conf": ["_fcall", "get_fs_conf"],
        "some_files": ["_fcall", "fs.open_inode", "./dir5/foo.xml",
                       "fs_conf"]
    }
    gr = grow(data, CC())
    correct = """
_history:
  fcalls_evaluated:
  - - single_call
    - get_fs_conf
    - [fs_conf]
  - - single_call
    - fs.open_inode
    - [some_files]
fs_conf:
  ftypes:
  - ['^file://.*~$', ignored]
  - ['^file://.*\.txt$', text]
  - ['^file://.*\.cfg$', text]
  - ['^file://.*\.yml$', yaml]
  - ['^file://.*\.yaml$', yaml]
  - ['^file://.*\.json$', json]
  - ['^file://.*\.xml$', xml]
  - ['^file://.*$', closed_file]
  - ['^folder://.*$', closed_folder]
  handlers:
    closed_file: ['["_fcall", "fs.pull_closed_file"]', '["_fcall", "fs.push_closed_file"]']
    closed_folder: ['["_fcall", "fs.pull_closed_folder"]', '["_fcall", "fs.push_closed_folder"]']
    ignored: ['["_fcall", "fs.pull_ignored"]', '["_fcall", "fs.push_ignored"]']
    json: ['["_fcall", "fs.pull_json"]', '["_fcall", "fs.push_json"]']
    open_folder: ['["_fcall", "fs.pull_open_folder"]', '["_fcall", "fs.push_open_folder"]']
    text: ['["_fcall", "fs.pull_text"]', '["_fcall", "fs.push_text"]']
    xml: ['["_fcall", "fs.pull_xml"]', '["_fcall", "fs.push_xml"]']
    yaml: ['["_fcall", "fs.pull_yaml"]', '["_fcall", "fs.push_yaml"]']
some_files:
  ftype: xml
  contents:
    _t: data
    a: {}
    c:
    - "haha"
    - _t: country
      a: {name: Liechtenstein}
      c:
      - _t: rank
        a: {}
        c: ['1']
      - _t: year
        a: {}
        c: ['2008']
      - _t: gdppc
        a: {}
        c: ['141100']
      - _t: neighbor
        a: {direction: E, name: Austria}
        c: []
      - _t: neighbor
        a: {direction: W, name: Switzerland}
        c: []
    - "haha2"
    - _t: country
      a: {name: Singapore}
      c:
      - _t: rank
        a: {}
        c: ['4']
      - _t: year
        a: {}
        c: ['2011']
      - _t: gdppc
        a: {}
        c: ['59900']
      - _t: neighbor
        a: {direction: N, name: Malaysia}
        c: []
    - _t: country
      a: {name: Panama}
      c:
      - _t: rank
        a: {}
        c: ['68']
      - _t: year
        a: {}
        c: ['2011']
      - _t: gdppc
        a: {}
        c: ['13600']
      - _t: neighbor
        a: {direction: W, name: Costa Rica}
        c: []
      - _t: neighbor
        a: {direction: E, name: Colombia}
        c: []
"""
    assert(gr == yaml.load(correct))


def fs_binding_open_folder_but_not_open_it():
    class CC(object):
        def __init__(self):
            self.fs = FsBinding("fs.", self)

        def get_fs_conf(self, context):
            z = self.fs.get_defaults(context)
            return z

    data = {
        "fs_conf": ["_fcall", "get_fs_conf"],
        "some_files": ["_fcall", "fs.open_inode", "./dir0",
                       "fs_conf"]
    }
    gr = grow(data, CC())
    correct = """
_history:
  fcalls_evaluated:
  - - single_call
    - get_fs_conf
    - [fs_conf]
  - - single_call
    - fs.open_inode
    - [some_files]
fs_conf:
  ftypes:
  - ['^file://.*~$', ignored]
  - ['^file://.*\.txt$', text]
  - ['^file://.*\.cfg$', text]
  - ['^file://.*\.yml$', yaml]
  - ['^file://.*\.yaml$', yaml]
  - ['^file://.*\.json$', json]
  - ['^file://.*\.xml$', xml]
  - ['^file://.*$', closed_file]
  - ['^folder://.*$', closed_folder]
  handlers:
    closed_file: ['["_fcall", "fs.pull_closed_file"]', '["_fcall", "fs.push_closed_file"]']
    closed_folder: ['["_fcall", "fs.pull_closed_folder"]', '["_fcall", "fs.push_closed_folder"]']
    ignored: ['["_fcall", "fs.pull_ignored"]', '["_fcall", "fs.push_ignored"]']
    json: ['["_fcall", "fs.pull_json"]', '["_fcall", "fs.push_json"]']
    open_folder: ['["_fcall", "fs.pull_open_folder"]', '["_fcall", "fs.push_open_folder"]']
    text: ['["_fcall", "fs.pull_text"]', '["_fcall", "fs.push_text"]']
    xml: ['["_fcall", "fs.pull_xml"]', '["_fcall", "fs.push_xml"]']
    yaml: ['["_fcall", "fs.pull_yaml"]', '["_fcall", "fs.push_yaml"]']
some_files: {ftype: closed_folder, path: ./dir0}
"""
    assert(gr == yaml.load(correct))


def fs_binding_open_folder_but_not_open_files():
    class CC(object):
        def __init__(self):
            self.fs = FsBinding("fs.", self)

        def get_fs_conf(self, context):
            z = self.fs.get_defaults(context)
            z["ftypes"] = [
                ['^folder://.*$', 'open_folder'],
                ['^file://.*$', 'closed_file']
            ]
            return z

    data = {
        "fs_conf": ["_fcall", "get_fs_conf"],
        "some_files": ["_fcall", "fs.open_inode", "./dir0",
                       "fs_conf"]
    }
    gr = grow(data, CC())
    correct = """
_history:
  fcalls_evaluated:
  - - single_call
    - get_fs_conf
    - [fs_conf]
  - - single_call
    - fs.open_inode
    - [some_files]
fs_conf:
  ftypes:
  - ['^folder://.*$', open_folder]
  - ['^file://.*$', closed_file]
  handlers:
    closed_file: ['["_fcall", "fs.pull_closed_file"]', '["_fcall", "fs.push_closed_file"]']
    closed_folder: ['["_fcall", "fs.pull_closed_folder"]', '["_fcall", "fs.push_closed_folder"]']
    ignored: ['["_fcall", "fs.pull_ignored"]', '["_fcall", "fs.push_ignored"]']
    json: ['["_fcall", "fs.pull_json"]', '["_fcall", "fs.push_json"]']
    open_folder: ['["_fcall", "fs.pull_open_folder"]', '["_fcall", "fs.push_open_folder"]']
    text: ['["_fcall", "fs.pull_text"]', '["_fcall", "fs.push_text"]']
    xml: ['["_fcall", "fs.pull_xml"]', '["_fcall", "fs.push_xml"]']
    yaml: ['["_fcall", "fs.pull_yaml"]', '["_fcall", "fs.push_yaml"]']
some_files:
  contents:
    dir1:
      contents:
        foo.txt: {ftype: closed_file, path: ./dir0/dir1/foo.txt}
      ftype: open_folder
    foo2.txt: {ftype: closed_file, path: ./dir0/foo2.txt}
  ftype: open_folder
"""
    assert(gr == yaml.load(correct))


def fs_binding_open_text_files_with_custom_handler():
    class CC(object):
        def __init__(self):
            self.fs = FsBinding("fs.", self)
            
        def append_some_stuff(self, context):
            # just an example how it can be done
            zz = self.fs.pull_text(context)
            zz["contents"] += ["and some stuff", "1", "2", "3"]
            return zz
            
        def get_fs_conf(self, context):
            z = self.fs.get_defaults(context)
            z["ftypes"][-1] = ['^folder://.*$', 'open_folder']
            z["ftypes"] = [["^file://.*\\.txt$", "my_text"]] + z[
                "ftypes"]
            z["handlers"]["my_text"] = [
                '["_fcall", "append_some_stuff"]',
                None
            ]
            return z

    data = {
        "fs_conf": ["_fcall", "get_fs_conf"],
        "some_files": ["_fcall", "fs.open_inode", "./dir0",
                       "fs_conf"]
    }
    correct = """
_history:
  fcalls_evaluated:
  - - single_call
    - get_fs_conf
    - [fs_conf]
  - - single_call
    - fs.open_inode
    - [some_files]
fs_conf:
  ftypes:
  - ['^file://.*\.txt$', my_text]
  - ['^file://.*~$', ignored]
  - ['^file://.*\.txt$', text]
  - ['^file://.*\.cfg$', text]
  - ['^file://.*\.yml$', yaml]
  - ['^file://.*\.yaml$', yaml]
  - ['^file://.*\.json$', json]
  - ['^file://.*\.xml$', xml]
  - ['^file://.*$', closed_file]
  - ['^folder://.*$', open_folder]
  handlers:
    closed_file: ['["_fcall", "fs.pull_closed_file"]', '["_fcall", "fs.push_closed_file"]']
    closed_folder: ['["_fcall", "fs.pull_closed_folder"]', '["_fcall", "fs.push_closed_folder"]']
    ignored: ['["_fcall", "fs.pull_ignored"]', '["_fcall", "fs.push_ignored"]']
    json: ['["_fcall", "fs.pull_json"]', '["_fcall", "fs.push_json"]']
    my_text: ['["_fcall", "append_some_stuff"]', null]
    open_folder: ['["_fcall", "fs.pull_open_folder"]', '["_fcall", "fs.push_open_folder"]']
    text: ['["_fcall", "fs.pull_text"]', '["_fcall", "fs.push_text"]']
    xml: ['["_fcall", "fs.pull_xml"]', '["_fcall", "fs.push_xml"]']
    yaml: ['["_fcall", "fs.pull_yaml"]', '["_fcall", "fs.push_yaml"]']
some_files:
  contents:
    dir1:
      contents:
        foo.txt:
          contents: [haha, haha2, '', and some stuff, '1', '2', '3']
          ftype: my_text
      ftype: open_folder
    foo2.txt:
      contents: [bobo, hoho, '', and some stuff, '1', '2', '3']
      ftype: my_text
  ftype: open_folder
"""
    gr = grow(data, CC())
    assert(gr == yaml.load(correct))

def fs_binding_open_text_files_with_embedded_fcalls():
    class CC(object):
        def __init__(self):
            self.fs = FsBinding("fs.", self)

        def get_fs_conf(self, context):
            z = self.fs.get_defaults(context)
            return z
            
        def get_some_lines(self, context):
            return ["foo", "buu", "poo"]

    data = {
        "fs_conf": ["_fcall", "get_fs_conf"],
        "some_files": ["_fcall", "fs.open_inode", "./dir3/foo.txt",
                       "fs_conf"]
    }
    gr = grow(data, CC())
    correct = """
_history:
  fcalls_evaluated:
  - - single_call
    - get_fs_conf
    - [fs_conf]
  - - single_call
    - fs.open_inode
    - [some_files]
  - - single_call
    - get_some_lines
    - [some_files, contents, 1]
fs_conf:
  ftypes:
  - ['^file://.*~$', ignored]
  - ['^file://.*\.txt$', text]
  - ['^file://.*\.cfg$', text]
  - ['^file://.*\.yml$', yaml]
  - ['^file://.*\.yaml$', yaml]
  - ['^file://.*\.json$', json]
  - ['^file://.*\.xml$', xml]
  - ['^file://.*$', closed_file]
  - ['^folder://.*$', closed_folder]
  handlers:
    closed_file: ['["_fcall", "fs.pull_closed_file"]', '["_fcall", "fs.push_closed_file"]']
    closed_folder: ['["_fcall", "fs.pull_closed_folder"]', '["_fcall", "fs.push_closed_folder"]']
    ignored: ['["_fcall", "fs.pull_ignored"]', '["_fcall", "fs.push_ignored"]']
    json: ['["_fcall", "fs.pull_json"]', '["_fcall", "fs.push_json"]']
    open_folder: ['["_fcall", "fs.pull_open_folder"]', '["_fcall", "fs.push_open_folder"]']
    text: ['["_fcall", "fs.pull_text"]', '["_fcall", "fs.push_text"]']
    xml: ['["_fcall", "fs.pull_xml"]', '["_fcall", "fs.push_xml"]']
    yaml: ['["_fcall", "fs.pull_yaml"]', '["_fcall", "fs.push_yaml"]']
some_files:
  contents:
  - some text, and afterwards some fcall, in json syntax
  - [foo, buu, poo]
  - ''
  ftype: text
"""
    assert(gr == yaml.load(correct))

def fs_binding_save_text():
    class CC(object):
        def __init__(self):
            self.fs = FsBinding("fs.", self)

        def get_fs_conf(self, context):
            z = self.fs.get_defaults(context)
            return z
            
    data = {
        "fs_conf": ["_fcall", "get_fs_conf"],
        "source": {
            "a_file.txt": {
                "ftype": "text",
                "contents": [
                    "line1",
                    "line2"
                ]
            }
        },
        "steps": [
            ["_fcall", "fs.save_inode",
             "/source/a_file.txt",
             "/tmp/a_file2.txt",
             "/fs_conf"],
            ["_fcall", "fs.open_inode",
             "/tmp/a_file2.txt",
             "/fs_conf"],
        ]
    }
    gr = grow(data, CC())
    correct = """
_history:
  fcalls_evaluated:
  - - single_call
    - get_fs_conf
    - [fs_conf]
  - - single_call
    - fs.save_inode
    - [steps, 0]
  - - single_call
    - fs.open_inode
    - [steps, 1]
fs_conf:
  ftypes:
  - ['^file://.*~$', ignored]
  - ['^file://.*\.txt$', text]
  - ['^file://.*\.cfg$', text]
  - ['^file://.*\.yml$', yaml]
  - ['^file://.*\.yaml$', yaml]
  - ['^file://.*\.json$', json]
  - ['^file://.*\.xml$', xml]
  - ['^file://.*$', closed_file]
  - ['^folder://.*$', closed_folder]
  handlers:
    closed_file: ['["_fcall", "fs.pull_closed_file"]', '["_fcall", "fs.push_closed_file"]']
    closed_folder: ['["_fcall", "fs.pull_closed_folder"]', '["_fcall", "fs.push_closed_folder"]']
    ignored: ['["_fcall", "fs.pull_ignored"]', '["_fcall", "fs.push_ignored"]']
    json: ['["_fcall", "fs.pull_json"]', '["_fcall", "fs.push_json"]']
    open_folder: ['["_fcall", "fs.pull_open_folder"]', '["_fcall", "fs.push_open_folder"]']
    text: ['["_fcall", "fs.pull_text"]', '["_fcall", "fs.push_text"]']
    xml: ['["_fcall", "fs.pull_xml"]', '["_fcall", "fs.push_xml"]']
    yaml: ['["_fcall", "fs.pull_yaml"]', '["_fcall", "fs.push_yaml"]']
source:
  a_file.txt:
    contents: [line1, line2]
    ftype: text
steps:
- null
- contents: [line1, line2]
  ftype: text
"""
    assert(gr == yaml.load(correct))

def fs_binding_save_open_folder():    
    class CC(object):
        def __init__(self):
            self.fs = FsBinding("fs.", self)

        def get_fs_conf(self, context):
            z = self.fs.get_defaults(context)
            z["ftypes"][-1] = ['^folder://.*$', 'open_folder']
            return z
            
    data = {
        "fs_conf": ["_fcall", "get_fs_conf"],
        "steps": [
            ["_fcall", "fs.exec_local",
             ["rm", "-rf", "/tmp/a_dir0"]],
            ["_fcall", "fs.open_inode",
             "./dir0",
             "/fs_conf"],
            ["_fcall", "fs.save_inode",
             "../1",
             "/tmp/a_dir0",
             "/fs_conf"],
            ["_fcall", "fs.open_inode",
             "/tmp/a_dir0",
             "/fs_conf"],
        ]
    }
    gr = grow(data, CC())
    correct = """
_history:
  fcalls_evaluated:
  - - single_call
    - get_fs_conf
    - [fs_conf]
  - - single_call
    - fs.exec_local
    - [steps, 0]
  - - single_call
    - fs.open_inode
    - [steps, 1]
  - - single_call
    - fs.save_inode
    - [steps, 2]
  - - single_call
    - fs.open_inode
    - [steps, 3]
fs_conf:
  ftypes:
  - ['^file://.*~$', ignored]
  - ['^file://.*\.txt$', text]
  - ['^file://.*\.cfg$', text]
  - ['^file://.*\.yml$', yaml]
  - ['^file://.*\.yaml$', yaml]
  - ['^file://.*\.json$', json]
  - ['^file://.*\.xml$', xml]
  - ['^file://.*$', closed_file]
  - ['^folder://.*$', open_folder]
  handlers:
    closed_file: ['["_fcall", "fs.pull_closed_file"]', '["_fcall", "fs.push_closed_file"]']
    closed_folder: ['["_fcall", "fs.pull_closed_folder"]', '["_fcall", "fs.push_closed_folder"]']
    ignored: ['["_fcall", "fs.pull_ignored"]', '["_fcall", "fs.push_ignored"]']
    json: ['["_fcall", "fs.pull_json"]', '["_fcall", "fs.push_json"]']
    open_folder: ['["_fcall", "fs.pull_open_folder"]', '["_fcall", "fs.push_open_folder"]']
    text: ['["_fcall", "fs.pull_text"]', '["_fcall", "fs.push_text"]']
    xml: ['["_fcall", "fs.pull_xml"]', '["_fcall", "fs.push_xml"]']
    yaml: ['["_fcall", "fs.pull_yaml"]', '["_fcall", "fs.push_yaml"]']
steps:
- cmd: [rm, -rf, /tmp/a_dir0]
  cwd: null
  err: ['']
  out: ['']
- contents:
    dir1:
      contents:
        foo.txt:
          contents: [haha, haha2, '']
          ftype: text
      ftype: open_folder
    foo2.txt:
      contents: [bobo, hoho, '']
      ftype: text
  ftype: open_folder
- null
- contents:
    dir1:
      contents:
        foo.txt:
          contents: [haha, haha2, '']
          ftype: text
      ftype: open_folder
    foo2.txt:
      contents: [bobo, hoho, '']
      ftype: text
  ftype: open_folder
"""
    assert(gr == yaml.load(correct))

def fs_binding_save_yaml():
    class CC(object):
        def __init__(self):
            self.fs = FsBinding("fs.", self)

        def get_fs_conf(self, context):
            z = self.fs.get_defaults(context)
            return z
            
    data = {
        "fs_conf": ["_fcall", "get_fs_conf"],
        "source": {
            "a_file.yml": {
                "ftype": "yaml",
                "contents": {
                    "hello": "world",
                    "hello1": ["world", "!"]
                }
            }
        },
        "steps": [
            ["_fcall", "fs.save_inode",
             "/source/a_file.yml",
             "/tmp/a_file2.yml",
             "/fs_conf"],
            ["_fcall", "fs.open_inode",
             "/tmp/a_file2.yml",
             "/fs_conf"],
        ]
    }
    gr = grow(data, CC())
    correct = """
_history:
  fcalls_evaluated:
  - - single_call
    - get_fs_conf
    - [fs_conf]
  - - single_call
    - fs.save_inode
    - [steps, 0]
  - - single_call
    - fs.open_inode
    - [steps, 1]
fs_conf:
  ftypes:
  - ['^file://.*~$', ignored]
  - ['^file://.*\.txt$', text]
  - ['^file://.*\.cfg$', text]
  - ['^file://.*\.yml$', yaml]
  - ['^file://.*\.yaml$', yaml]
  - ['^file://.*\.json$', json]
  - ['^file://.*\.xml$', xml]
  - ['^file://.*$', closed_file]
  - ['^folder://.*$', closed_folder]
  handlers:
    closed_file: ['["_fcall", "fs.pull_closed_file"]', '["_fcall", "fs.push_closed_file"]']
    closed_folder: ['["_fcall", "fs.pull_closed_folder"]', '["_fcall", "fs.push_closed_folder"]']
    ignored: ['["_fcall", "fs.pull_ignored"]', '["_fcall", "fs.push_ignored"]']
    json: ['["_fcall", "fs.pull_json"]', '["_fcall", "fs.push_json"]']
    open_folder: ['["_fcall", "fs.pull_open_folder"]', '["_fcall", "fs.push_open_folder"]']
    text: ['["_fcall", "fs.pull_text"]', '["_fcall", "fs.push_text"]']
    xml: ['["_fcall", "fs.pull_xml"]', '["_fcall", "fs.push_xml"]']
    yaml: ['["_fcall", "fs.pull_yaml"]', '["_fcall", "fs.push_yaml"]']
source:
  a_file.yml:
    contents:
      hello: world
      hello1: [world, '!']
    ftype: yaml
steps:
- null
- contents:
    hello: world
    hello1: [world, '!']
  ftype: yaml
"""
    assert(gr == yaml.load(correct))

def fs_binding_save_json():
    class CC(object):
        def __init__(self):
            self.fs = FsBinding("fs.", self)

        def get_fs_conf(self, context):
            z = self.fs.get_defaults(context)
            return z
            
    data = {
        "fs_conf": ["_fcall", "get_fs_conf"],
        "source": {
            "a_file.json": {
                "ftype": "json",
                "contents": {
                    "hello": "world",
                    "hello1": ["world", "!"]
                }
            }
        },
        "steps": [
            ["_fcall", "fs.save_inode",
             "/source/a_file.json",
             "/tmp/a_file2.json",
             "/fs_conf"],
            ["_fcall", "fs.open_inode",
             "/tmp/a_file2.json",
             "/fs_conf"],
        ]
    }
    gr = grow(data, CC())
    correct = """
_history:
  fcalls_evaluated:
  - - single_call
    - get_fs_conf
    - [fs_conf]
  - - single_call
    - fs.save_inode
    - [steps, 0]
  - - single_call
    - fs.open_inode
    - [steps, 1]
fs_conf:
  ftypes:
  - ['^file://.*~$', ignored]
  - ['^file://.*\.txt$', text]
  - ['^file://.*\.cfg$', text]
  - ['^file://.*\.yml$', yaml]
  - ['^file://.*\.yaml$', yaml]
  - ['^file://.*\.json$', json]
  - ['^file://.*\.xml$', xml]
  - ['^file://.*$', closed_file]
  - ['^folder://.*$', closed_folder]
  handlers:
    closed_file: ['["_fcall", "fs.pull_closed_file"]', '["_fcall", "fs.push_closed_file"]']
    closed_folder: ['["_fcall", "fs.pull_closed_folder"]', '["_fcall", "fs.push_closed_folder"]']
    ignored: ['["_fcall", "fs.pull_ignored"]', '["_fcall", "fs.push_ignored"]']
    json: ['["_fcall", "fs.pull_json"]', '["_fcall", "fs.push_json"]']
    open_folder: ['["_fcall", "fs.pull_open_folder"]', '["_fcall", "fs.push_open_folder"]']
    text: ['["_fcall", "fs.pull_text"]', '["_fcall", "fs.push_text"]']
    xml: ['["_fcall", "fs.pull_xml"]', '["_fcall", "fs.push_xml"]']
    yaml: ['["_fcall", "fs.pull_yaml"]', '["_fcall", "fs.push_yaml"]']
source:
  a_file.json:
    contents:
      hello: world
      hello1: [world, '!']
    ftype: json
steps:
- null
- contents:
    hello: world
    hello1: [world, '!']
  ftype: json
"""
    assert(gr == yaml.load(correct))

def fs_binding_save_xml():
    class CC(object):
        def __init__(self):
            self.fs = FsBinding("fs.", self)

        def get_fs_conf(self, context):
            z = self.fs.get_defaults(context)
            return z
            
    data = {
        "fs_conf": ["_fcall", "get_fs_conf"],
        "source": {
            "a_file.xml": {
                "ftype": "xml",
                "contents": {
                    "_t": "data",
                    "a": {"buba": "007"},
                    "c": [
                        "heh",
                        {
                                "_t": "klo",
                            "a": {},
                            "c": ["70707"]
                        }
                    ]
                }
            }
        },
        "steps": [
            ["_fcall", "fs.save_inode",
             "/source/a_file.xml",
             "/tmp/a_file2.xml",
             "/fs_conf"],
            ["_fcall", "fs.open_inode",
             "/tmp/a_file2.xml",
             "/fs_conf"],
        ]
    }
    gr = grow(data, CC())
    correct = """
_history:
  fcalls_evaluated:
  - - single_call
    - get_fs_conf
    - [fs_conf]
  - - single_call
    - fs.save_inode
    - [steps, 0]
  - - single_call
    - fs.open_inode
    - [steps, 1]
fs_conf:
  ftypes:
  - ['^file://.*~$', ignored]
  - ['^file://.*\.txt$', text]
  - ['^file://.*\.cfg$', text]
  - ['^file://.*\.yml$', yaml]
  - ['^file://.*\.yaml$', yaml]
  - ['^file://.*\.json$', json]
  - ['^file://.*\.xml$', xml]
  - ['^file://.*$', closed_file]
  - ['^folder://.*$', closed_folder]
  handlers:
    closed_file: ['["_fcall", "fs.pull_closed_file"]', '["_fcall", "fs.push_closed_file"]']
    closed_folder: ['["_fcall", "fs.pull_closed_folder"]', '["_fcall", "fs.push_closed_folder"]']
    ignored: ['["_fcall", "fs.pull_ignored"]', '["_fcall", "fs.push_ignored"]']
    json: ['["_fcall", "fs.pull_json"]', '["_fcall", "fs.push_json"]']
    open_folder: ['["_fcall", "fs.pull_open_folder"]', '["_fcall", "fs.push_open_folder"]']
    text: ['["_fcall", "fs.pull_text"]', '["_fcall", "fs.push_text"]']
    xml: ['["_fcall", "fs.pull_xml"]', '["_fcall", "fs.push_xml"]']
    yaml: ['["_fcall", "fs.pull_yaml"]', '["_fcall", "fs.push_yaml"]']
source:
  a_file.xml:
    contents:
      _t: data
      a: {buba: '007'}
      c:
      - heh
      - _t: klo
        a: {}
        c: ['70707']
    ftype: xml
steps:
- null
- contents:
    _t: data
    a: {buba: '007'}
    c:
    - heh
    - _t: klo
      a: {}
      c: ['70707']
  ftype: xml
"""
    assert(gr == yaml.load(correct))

def fs_binding_save_ignored():
    class CC(object):
        def __init__(self):
            self.fs = FsBinding("fs.", self)

        def get_fs_conf(self, context):
            z = self.fs.get_defaults(context)
            return z

        def try_open_inode(self, context):
            try:
                return self.fs.open_inode(context)
            except Exception as e:
                return "not exists"
            
    data = {
        "fs_conf": ["_fcall", "get_fs_conf"],
        "source": None,
        "steps": [
            ["_fcall", "fs.save_inode",
             "/source",
             "/tmp/a_file2.ignored",
             "/fs_conf"],
            ["_fcall", "try_open_inode",
             "/tmp/a_file2.ignored",
             "/fs_conf"],
        ]
    }
    gr = grow(data, CC())
    correct = """
_history:
  fcalls_evaluated:
  - - single_call
    - get_fs_conf
    - [fs_conf]
  - - single_call
    - fs.save_inode
    - [steps, 0]
  - - single_call
    - try_open_inode
    - [steps, 1]
fs_conf:
  ftypes:
  - ['^file://.*~$', ignored]
  - ['^file://.*\.txt$', text]
  - ['^file://.*\.cfg$', text]
  - ['^file://.*\.yml$', yaml]
  - ['^file://.*\.yaml$', yaml]
  - ['^file://.*\.json$', json]
  - ['^file://.*\.xml$', xml]
  - ['^file://.*$', closed_file]
  - ['^folder://.*$', closed_folder]
  handlers:
    closed_file: ['["_fcall", "fs.pull_closed_file"]', '["_fcall", "fs.push_closed_file"]']
    closed_folder: ['["_fcall", "fs.pull_closed_folder"]', '["_fcall", "fs.push_closed_folder"]']
    ignored: ['["_fcall", "fs.pull_ignored"]', '["_fcall", "fs.push_ignored"]']
    json: ['["_fcall", "fs.pull_json"]', '["_fcall", "fs.push_json"]']
    open_folder: ['["_fcall", "fs.pull_open_folder"]', '["_fcall", "fs.push_open_folder"]']
    text: ['["_fcall", "fs.pull_text"]', '["_fcall", "fs.push_text"]']
    xml: ['["_fcall", "fs.pull_xml"]', '["_fcall", "fs.push_xml"]']
    yaml: ['["_fcall", "fs.pull_yaml"]', '["_fcall", "fs.push_yaml"]']
source: null
steps: [null, not exists]
"""
    assert(gr == yaml.load(correct))

def fs_binding_save_closed_folder():
    class CC(object):
        def __init__(self):
            self.fs = FsBinding("fs.", self)

        def get_fs_conf(self, context):
            z = self.fs.get_defaults(context)
            return z

        def get_fs_conf2(self, context):
            z = self.fs.get_defaults(context)
            z["ftypes"][-1] = ['^folder://.*$', 'open_folder']
            return z

            
    data = {
        "fs_conf": ["_fcall", "get_fs_conf"],
        "steps": [
            ["_fcall", "fs.exec_local",
             ["rm", "-rf", "/tmp/a_dir0"]],
            ["_fcall", "fs.open_inode",
             "./dir0",
             "/fs_conf"],
            ["_fcall", "fs.save_inode",
             "../1",
             "/tmp/a_dir0",
             "/fs_conf"],
            ["_fcall", "fs.open_inode",
             "/tmp/a_dir0",
             ["_fcall", "get_fs_conf2"]],
        ]
    }
    gr = grow(data, CC())
    correct = """
_history:
  fcalls_evaluated:
  - - single_call
    - get_fs_conf
    - [fs_conf]
  - - single_call
    - fs.exec_local
    - [steps, 0]
  - - single_call
    - fs.open_inode
    - [steps, 1]
  - - single_call
    - fs.save_inode
    - [steps, 2]
  - - single_call
    - fs.open_inode
    - [steps, 3]
fs_conf:
  ftypes:
  - ['^file://.*~$', ignored]
  - ['^file://.*\.txt$', text]
  - ['^file://.*\.cfg$', text]
  - ['^file://.*\.yml$', yaml]
  - ['^file://.*\.yaml$', yaml]
  - ['^file://.*\.json$', json]
  - ['^file://.*\.xml$', xml]
  - ['^file://.*$', closed_file]
  - ['^folder://.*$', closed_folder]
  handlers:
    closed_file: ['["_fcall", "fs.pull_closed_file"]', '["_fcall", "fs.push_closed_file"]']
    closed_folder: ['["_fcall", "fs.pull_closed_folder"]', '["_fcall", "fs.push_closed_folder"]']
    ignored: ['["_fcall", "fs.pull_ignored"]', '["_fcall", "fs.push_ignored"]']
    json: ['["_fcall", "fs.pull_json"]', '["_fcall", "fs.push_json"]']
    open_folder: ['["_fcall", "fs.pull_open_folder"]', '["_fcall", "fs.push_open_folder"]']
    text: ['["_fcall", "fs.pull_text"]', '["_fcall", "fs.push_text"]']
    xml: ['["_fcall", "fs.pull_xml"]', '["_fcall", "fs.push_xml"]']
    yaml: ['["_fcall", "fs.pull_yaml"]', '["_fcall", "fs.push_yaml"]']
steps:
- cmd: [rm, -rf, /tmp/a_dir0]
  cwd: null
  err: ['']
  out: ['']
- {ftype: closed_folder, path: ./dir0}
- null
- contents:
    dir1:
      contents:
        foo.txt:
          contents: [haha, haha2, '']
          ftype: text
      ftype: open_folder
    foo2.txt:
      contents: [bobo, hoho, '']
      ftype: text
  ftype: open_folder

"""
    assert(gr == yaml.load(correct))

def fs_binding_save_closed_file():
    class CC(object):
        def __init__(self):
            self.fs = FsBinding("fs.", self)

        def get_fs_conf(self, context):
            z = self.fs.get_defaults(context)
            return z
            
    data = {
        "fs_conf": ["_fcall", "get_fs_conf"],
        "steps": [
            ["_fcall", "fs.exec_local",
             ["rm", "-rf", "/tmp/foo.unknown"]],
            ["_fcall", "fs.open_inode",
             "./dir4/foo.unknown",
             "/fs_conf"],
            ["_fcall", "fs.save_inode",
             "../1",
             "/tmp/foo.unknown",
             "/fs_conf"],
            ["_fcall", "fs.exec_local",
             ["stat", '--printf="%s"', "/tmp/foo.unknown"]],
        ]
    }
    gr = grow(data, CC())
    correct = """
_history:
  fcalls_evaluated:
  - - single_call
    - get_fs_conf
    - [fs_conf]
  - - single_call
    - fs.exec_local
    - [steps, 0]
  - - single_call
    - fs.open_inode
    - [steps, 1]
  - - single_call
    - fs.save_inode
    - [steps, 2]
  - - single_call
    - fs.exec_local
    - [steps, 3]
fs_conf:
  ftypes:
  - ['^file://.*~$', ignored]
  - ['^file://.*\.txt$', text]
  - ['^file://.*\.cfg$', text]
  - ['^file://.*\.yml$', yaml]
  - ['^file://.*\.yaml$', yaml]
  - ['^file://.*\.json$', json]
  - ['^file://.*\.xml$', xml]
  - ['^file://.*$', closed_file]
  - ['^folder://.*$', closed_folder]
  handlers:
    closed_file: ['["_fcall", "fs.pull_closed_file"]', '["_fcall", "fs.push_closed_file"]']
    closed_folder: ['["_fcall", "fs.pull_closed_folder"]', '["_fcall", "fs.push_closed_folder"]']
    ignored: ['["_fcall", "fs.pull_ignored"]', '["_fcall", "fs.push_ignored"]']
    json: ['["_fcall", "fs.pull_json"]', '["_fcall", "fs.push_json"]']
    open_folder: ['["_fcall", "fs.pull_open_folder"]', '["_fcall", "fs.push_open_folder"]']
    text: ['["_fcall", "fs.pull_text"]', '["_fcall", "fs.push_text"]']
    xml: ['["_fcall", "fs.pull_xml"]', '["_fcall", "fs.push_xml"]']
    yaml: ['["_fcall", "fs.pull_yaml"]', '["_fcall", "fs.push_yaml"]']
steps:
- cmd: [rm, -rf, /tmp/foo.unknown]
  cwd: null
  err: ['']
  out: ['']
- {ftype: closed_file, path: ./dir4/foo.unknown}
- null
- cmd: [stat, --printf="%s", /tmp/foo.unknown]
  cwd: null
  err: ['']
  out: ['"5"']
"""
    assert(gr == yaml.load(correct))

def fs_binding_exec_local():
    class CC(object):
        def __init__(self):
            self.fs = FsBinding("fs.", self)
        def extract(self, context):
            return context.args[0]["err"][0].split()[0]
    data = {
        "some_call": ["_fcall", "extract",
                      ["_fcall", "fs.exec_local",
                       ["python", "--version"]]]
    }
    gr = grow(data, CC())
    correct = """
_history:
  fcalls_evaluated:
  - - single_call
    - extract
    - [some_call]
some_call: Python
"""
    assert(gr == yaml.load(correct))
    
def base_dependencies():
    class CC(object):
        def c1(self, context):
            pass
        def c2(self, context):
            pass
    data = {
        "calls": [
            ["_fcall", {"deps": ["/calls/1"]}, "c2"],
            ["_fcall", "c1"],
        ]
    }
    gr = grow(data, CC())
    assert(gr == {
        '_history': {
            'fcalls_evaluated': [
                ['single_call', 'c1', ['calls', 1]],
                ['single_call', 'c2', ['calls', 0]]]},
        'calls': [None, None]})

def self_dependency():
    class CC(object):
        def c1(self, context):
            pass
    data = {
        "calls": [
            ["_fcall", {"deps": ["/calls/0"]}, "c1"],
        ]
    }
    gr = grow(data, CC())
    assert(gr == {
        '_history': {
            'fcalls_evaluated': [
                ['single_call', 'c1', ['calls', 0]]]},
        'calls': [None]})

def mutual_dependencies():
    class CC(object):
        def c1(self, context):
            pass
        def c2(self, context):
            pass
        def c3(self, context):
            pass

    data = {
        "calls": [
            ["_fcall", {"deps": ["/calls/1"]}, "c2"],
            ["_fcall", {"deps": ["/calls/2"]}, "c1"],
            ["_fcall", {"deps": ["/calls/0"]}, "c3"],
        ]
    }
    try:
        gr = grow(data, CC())
    except Exception as e:
        assert(str(e.cause) == "mutual dependencies")

def multiple_dependencies():
    class CC(object):
        def c1(self, context):
            pass
        def c2(self, context):
            pass
        def c3(self, context):
            pass

    data = {
        "calls": [
            ["_fcall", {"deps": ["/calls/1", "/calls/2"]}, "c2"],
            ["_fcall", "c1"],
            ["_fcall", "c3"],
        ]
    }
    gr = grow(data, CC())
    assert(gr == {
        '_history': {
            'fcalls_evaluated': [
                ['single_call', 'c1', ['calls', 1]],
                ['single_call', 'c3', ['calls', 2]],
                ['single_call', 'c2', ['calls', 0]]]},
        'calls': [None, None, None]})

def dependency_chain():
    class CC(object):
        def c1(self, context):
            pass
        def c2(self, context):
            pass
        def c3(self, context):
            pass

    data = {
        "calls": [
            ["_fcall", {"deps": ["/calls/1"]}, "c2"],
            ["_fcall", {"deps": ["/calls/2"]}, "c1"],
            ["_fcall", "c3"],
        ]
    }
    gr = grow(data, CC())
    assert(gr == {
        '_history': {
            'fcalls_evaluated': [
                ['single_call', 'c3', ['calls', 2]],
                ['single_call', 'c1', ['calls', 1]],
                ['single_call', 'c2', ['calls', 0]]]},
        'calls': [None, None, None]})

def non_exist_path_dependency():
    class CC(object):
        def c1(self, context):
            pass
    data = {
        "calls": [
            ["_fcall", {"deps": ["/mystikum"]}, "c1"],
        ]
    }
    try:
        gr = grow(data, CC())
    except Exception as e:
        assert(str(e.cause.cause) == "dependency /mystikum not fullfilled")

def dependency_vs_priority():
    class CC(object):
        def c1(self, context):
            pass
        def c2(self, context):
            pass

    data = {
        "calls": [
            ["_fcall", {"priority": -1000}, "c1"],
            ["_fcall", {"deps": ["/calls/0"]}, "c2"],
        ]
    }
    gr = grow(data, CC())
    assert(gr == {
        '_history': {
            'fcalls_evaluated': [
                ['single_call', 'c1', ['calls', 0]],
                ['single_call', 'c2', ['calls', 1]]]},
        'calls': [None, None]})

def dynamic_dependencies():
    class CC(object):
        def c1(self, context):
            pass
        def c2(self, context):
            return {"buba": ["_fcall", "c3"]}
        def c3(self, context):
            pass
    data = {
        "calls": [
            ["_fcall", {"deps": ["/calls/1/.*"]}, "c1"],
            ["_fcall", "c2"],
        ]
    }
    gr = grow(data, CC())
    assert(gr == {
        '_history': {
            'fcalls_evaluated': [
                ['single_call', 'c2', ['calls', 1]],
                ['single_call', 'c3', ['calls', 1, 'buba']],
                ['single_call', 'c1', ['calls', 0]]]},
        'calls': [None, {'buba': None}]})

def dependencies_and_cgroup():
    class CC(object):
        def c1(self, context):
            pass
        def c2(self, context):
            pass
    data = {
        "calls": [
            ["_fcall", {"deps": ["/calls/1"], "cgroup": "buba"}, "c1"],
            ["_fcall", "c2"],
        ]
    }
    try:
        gr = grow(data, CC())
    except Exception as e:
        assert(str(e.cause) == "cgroup is not currently supported for dependent fcalls")

def fs_binding_exec_local_dangerous_rm():
    class CC(object):
        def __init__(self):
            self.fs = FsBinding("fs.", self)
        def extract(self, context):
            return context.args[0]["err"][0].split()[0]
    data = {
        "some_call": ["_fcall", "extract",
                      ["_fcall", "fs.exec_local",
                       ["rm", "-r", "/tmp/bububu/*"]]]
    }
    try:
        gr = grow(data, CC())
    except Exception as e:
        assert(str(e.cause.cause) == "wildcard * not allowed with rm -r, use allow_rm_rf_asterisk in opts dictionary to bypass this check")


all_cases_func = [
    empty_doc,
    no_fcalls,
    single_evaluation,
    two_sibling_evaluations,
    two_sibling_cgroup_evaluation,
    fcall_returns_fcall,
    context_path_is_correct,
    simple_doc_immutability,
    nested_fcalls,
    fcall_order_priority,
    fcall_order_depth,
    fcall_order_path_alphabet,
    fcall_order_fcall_name,
    fcall_order_all,
    cgroup_non_cgroup_mix,
    fcall_returning_none,
    base_do_if,
    base_do_getval,
    base_do_map,
    base_do_fmt,
    dict_key_fcall_single,
    dict_key_fcall_none,
    dict_key_fcall_sequence,
    ignored_paths,
    ignored_fcalls,
    ignored_cgroup,
    ignored_regex,
    ignored_regexi,
    ignored_fcalls_evaluating,
    strict_keys_exception,
    max_depth_exceeded,
    segmented_fcall_path,
    fs_binding_open_folder_with_text_file,
    fs_binding_open_yaml,
    fs_binding_open_json,
    fs_binding_open_xml,
    fs_binding_open_folder_but_not_open_it,
    fs_binding_open_folder_but_not_open_files,
    fs_binding_open_text_files_with_custom_handler,
    fs_binding_open_text_files_with_embedded_fcalls,
    fs_binding_save_text,
    fs_binding_save_open_folder,
    fs_binding_save_yaml,
    fs_binding_save_json,
    fs_binding_save_xml,
    fs_binding_save_ignored,
    fs_binding_save_closed_folder,
    fs_binding_save_closed_file,
    fs_binding_exec_local,
    fs_binding_exec_local_dangerous_rm,
    base_dependencies,
    self_dependency,
    mutual_dependencies,
    multiple_dependencies,
    dependency_chain,
    non_exist_path_dependency,
    dependency_vs_priority,
    dynamic_dependencies,
    dependencies_and_cgroup,
]

def do_tests():
    test_names = [i.__name__ for i in all_cases_func]
    all_cases = dict([(i.__name__, i) for i in all_cases_func])
    cases = sys.argv[1:]
    if not cases:
        cases = test_names
    for i in cases:
        print "#### %s ###" % i
        all_cases[i]()

if __name__ == "__main__":
    try:
        do_tests()
    except PukalaBaseException as e:
        print e.doc
        print e.get_formed_desc()
    # attempt to stop exceptions coming from python threading
    # infrastructure; ThreadPool.finish() just wakes them up,
    # not joining (which is correct, as threads may be stuck);
    # and apparently there is something which causes exception if
    # during shutdown thread tries to access lock or condition
    # variable
    import time
    time.sleep(0.1)
