import sys
import re
import os
import time
import copy
import json
import platform

if sys.version[0] != '2':
    from functools import reduce
    raw_input = input


class T(object):
    __version = 'V2.0.1'
    __log_title = 'FuncLib ( ' + __version + ' )'
    __log_title_fix = 'FuncLib ( ' + __version + ' ) --> T.'

    @staticmethod
    def info():
        keys = T.each(lambda x: re.sub(r'\n|\s|=', '', x[:8]), T.__info.split('T.')[1:])
        docs_vars = vars(T)
        docs_keys = T.each(lambda x: '_T__' + x, keys)
        docs = {}
        for key in keys:
            docs[key] = docs_vars[docs_keys[keys.index(key)]]
        return {'keys': keys, 'docs': docs}

    __info = """
===================================================================================
                                    Func-Lib
                    A data processing methods lib for Python(2/3)
-----------------------------------------------------------------------------------
                             Author: @CN-Tower
                          Create At: 2018-2-2
                          Update At: 2018-2-10
                            Version: """ + __version + """
                             GitHub: http://github.com/CN-Tower/FuncLib
-----------------------------------------------------------------------------------
                      0: T.info                 1: T.index
                      2: T.find                 3: T.filter
                      4: T.reject               5: T.reduce
                      6: T.contains             7: T.flatten
                      8: T.each                 9: T.uniq
                     10: T.drop                11: T.pluck                
                     12: T.every               13: T.some                
                     14: T.list                15: T.dump
                     16: T.clone               17: T.test
                     18: T.replace             19: T.iscan
                     20: T.log                 21: T.timer               
                     22: T.now                 23: T.help                
===================================================================================
    """

    @staticmethod
    def index(predicate, _list):
        if bool(_list) and (isinstance(_list, list) or isinstance(_list, tuple)):
            if predicate in _list:
                return _list.index(predicate)
            elif isinstance(predicate, dict):
                for i in range(0, len(_list)):
                    tmp_bool = True
                    for key in predicate:
                        if key not in _list[i] or predicate[key] != _list[i][key]:
                            tmp_bool = False
                            break
                    if tmp_bool:
                        return i
                return -1
            elif bool(predicate) and 'function' in str(type(predicate)):
                for i in range(0, len(_list)):
                    if predicate(_list[i]):
                        return i
            return -1
        return -1

    __index = """ 
    ### T.index
        Looks through the list and returns the item index. If no match is found,
        or if list is empty, -1 will be returned.
        eg:
            from funclib import T
            persons = [{"name": "Tom", "age": 12},
                {"name": "Jerry", "age": 20},
                {"name": "Mary", "age": 35}]

            Jerry_idx = T.index({"name": 'Jerry'}, persons)
            Mary_idx  = T.index(lambda x: x['name'] == 'Mary', persons)

            print(Jerry_idx)  # => 1
            print(Mary_idx)   # => 2
    """

    @staticmethod
    def find(predicate, _list):
        idx = T.index(predicate, _list)
        if idx != -1:
            return _list[idx]
        return None

    __find = """
    ### T.find
        Looks through each value in the list, returning the first one that passes
        a truth test (predicate), or None.If no value passes the test the function
        returns as soon as it finds an acceptable element, and doesn't traverse
        the entire list.
        eg:
            from funclib import T
            persons = [{"name": "Tom", "age": 12},
                {"name": "Jerry", "age": 20},
                {"name": "Mary", "age": 35}]

            Jerry = T.find({"name": 'Jerry'}, persons)
            Mary  = T.find(lambda x: x['name'] == 'Mary', persons)

            print(Jerry)  # => {'age': 20, 'name': 'Jerry'}
            print(Mary)   # => {'age': 35, 'name': 'Mary'}
    """

    @staticmethod
    def filter(predicate, _list):
        tmp_list = T.clone(_list)
        ret_list = []
        while True:
            index = T.index(predicate, tmp_list)
            if index == -1:
                break
            else:
                ret_list.append(tmp_list[index])
                if index < len(tmp_list) - 1:
                    tmp_list = tmp_list[index + 1:]
                else:
                    break
        return ret_list

    __filter = """
    ### T.filter
        Looks through each value in the list, returning an array of all the values that
        pass a truth test (predicate).
        eg:
            from funclib import T
            persons = [{"name": "Tom", "age": 20},
                       {"name": "Jerry", "age": 20},
                       {"name": "Jerry", "age": 35}]

            Jerry = T.filter({"age": 20}, persons)
            Mary = T.filter(lambda x: x['name'] == 'Jerry', persons)
            print(Jerry)  # => [{'age': 20, 'name': 'Tom'}, {'age': 20, 'name': 'Jerry'}]
            print(Mary)   # => [{'age': 20, 'name': 'Jerry'}, {'age': 35, 'name': 'Jerry'}]
    """

    @staticmethod
    def reject(predicate, _list):
        index = T.index(predicate, _list)
        if index != -1:
            tmp_list = T.clone(_list)
            del tmp_list[index]
            return T.reject(predicate, tmp_list)
        return _list

    __reject = """
    ### T.reject
        Returns the values in list without the elements that the truth test (predicate) passes.
        The opposite of filter.
        eg:
            from funclib import T
            persons = [{"name": "Tom", "age": 12},
                       {"name": "Jerry", "age": 20},
                       {"name": "Mary", "age": 35}]

            not_Mary = T.reject({"name": "Mary"}, persons)
            adults = T.reject(lambda x: x['age'] < 18, persons)

            print(not_Mary)  # => [{"age": 12, "name": "Tom"}, {"age": 20, "name": "Jerry"}]
            print(adults)    # => [{"age": 20, "name": "Jerry"}, {"age": 35, "name": "Mary"}]
    """

    @staticmethod
    def reduce(*args):
        return reduce(*args)

    __reduce = """
    ### T.reduce
        Returns the buildIn method 'reduce', in python 3 the 'reduce' is imported from functools.
        eg:
            from funclib import T
            num_list = [1 , 2, 3, 4]
            print(T.reduce(lambda a, b: a + b, num_list))  # => 10
    """

    @staticmethod
    def contains(predicate, _list):
        index = T.index(predicate, _list)
        return index != -1

    __contains = """
    ### T.contains
        Returns true if the value is present in the list.
        eg:
            from funclib import T
            persons = [{"name": "Tom", "age": 12},
                       {"name": "Jerry", "age": 20},
                       {"name": "Mary", "age": 35}]

            is_contains_Jerry = T.contains({"name": "Jerry", "age": 12}, persons)
            is_contains_Mary = T.contains(lambda x: x['name'] == 'Mary', persons)

            print(is_contains_Jerry)  # => False
            print(is_contains_Mary)   # => True
    """

    @staticmethod
    def flatten(_list, is_deep=False):
        if _list and isinstance(_list, list):
            tmp_list = []
            for item in _list:
                if isinstance(item, list):
                    if is_deep:
                        tmp_list += T.flatten(item, True)
                    else:
                        tmp_list += item
                else:
                    tmp_list.append(item)
            return tmp_list
        return _list

    __flatten = """
    ### T.flatten
        Flattens a nested array (the nesting can be to any depth). If you pass shallow,
        the array will only be flattened a single level.
        eg:
            from funclib import T
            flt_list_01 = T.flatten([1, [2], [3, [[4]]]])
            flt_list_02 = T.flatten([1, [2], [3, [[4]]]], True)
            print (flt_list_01)  # => [1, 2, 3, [[4]]]
            print (flt_list_02)  # => [1, 2, 3, 4];
    """

    @staticmethod
    def each(*args):
        return list(map(*args))

    __each = """
    ### T.each
        Produces a new values list by mapping each value in list through a transformation
        function (iteratee). 
        eg:
            from funclib import T
            num_list = [1 , 2, 3, 4]
            list_10 = T.each(lambda x: x % 2, num_list)
            print(list_10)  #=> [1, 0, 1, 0]
    """

    @staticmethod
    def uniq(predicate, _list=None):
        is_no_predicate = False
        if _list is None:
            _list = predicate
            is_no_predicate = True
        if isinstance(_list, tuple):
            _list = list(_list)
        if bool(_list) and isinstance(_list, list):
            tmp_list = T.clone(_list)
            if is_no_predicate:
                for i in range(0, len(tmp_list)):
                    if len(tmp_list) <= i + 1:
                        break
                    tmp_list = tmp_list[:i + 1] + T.reject(tmp_list[i], tmp_list[i + 1:])
            else:
                index = T.index(predicate, tmp_list)
                if index != -1 and index + 1 < len(tmp_list):
                    tmp_list = tmp_list[:index + 1] + T.reject(predicate, tmp_list[index + 1:])
            return tmp_list
        return _list

    __uniq = """
    ### T.uniq
        Produces a duplicate-free version of the array.
        In particular only the first occurence of each value is kept.
        eg:
            from funclib import T
            persons00 = ("Tom", "Tom", "Jerry")
            persons01 = ["Tom", "Tom", "Jerry"]
            persons02 = [{"name": "Tom", "age": 12, "sex": "m"},
                         {"name": "Tom", "age": 20, "sex": "m"},
                         {"name": "Mary", "age": 35, "sex": "f"}]
            demo_list = [False, [], False, True, [], {}, False, '']

            unique_persons00 = T.uniq(persons00)
            unique_persons01 = T.uniq(persons01)
            unique_demo_list = T.uniq(demo_list)
            one_Tom = T.uniq({"name": "Tom"}, persons02)
            one_mail = T.uniq(lambda x: x['sex'] == "m", persons02)

            print(unique_persons00)  # => ["Jerry", "Tom"]
            print(unique_persons01)  # => ["Jerry", "Tom"]
            print(unique_demo_list)  # => [False, [], True, {}, '']
            print(one_Tom)  # => [{'age': 12, 'name': 'Tom', 'sex': 'm'}, {'age': 35, 'name': 'Mary', 'sex': 'f'}]
            print(one_mail)  # => [{'age': 12, 'name': 'Tom', 'sex': 'm'}, {'age': 35, 'name': 'Mary', 'sex': 'f'}]
    """

    @staticmethod
    def drop(_list, is_drop_0=False):
        if bool(_list) and isinstance(_list, list):
            tmp_list = T.clone(_list)
            list_len = len(tmp_list)
            for i in range(0, list_len):
                for j in range(0, list_len):
                    if j == list_len:
                        break
                    if is_drop_0:
                        drop_condition = not bool(tmp_list[j])
                    else:
                        drop_condition = not bool(tmp_list[j]) and tmp_list[j] != 0
                    if drop_condition:
                        tmp_list.remove(tmp_list[j])
                        list_len -= 1
            return tmp_list
        return _list

    __drop = """
    ### T.drop
        Delete false values expect 0.
        eg:
            from funclib import T
            tmp_list = [0, '', 3, None, [], {}, ['Yes'], 'Test']
            drop_val = T.drop(tmp_list)
            drop_val_and_0 = T.drop(tmp_list, True)

            print(drop_val)        # => [0, 3, ['Yes'], 'Test']
            print(drop_val_and_0)  # => [3, ['Yes'], 'Test']
    """

    @staticmethod
    def pluck(body, *key, **opt):
        if isinstance(body, dict):
            tmp_body = [body]
        else:
            tmp_body = body
        if isinstance(tmp_body, list) or isinstance(tmp_body, tuple):
            for k in key:
                field_k = T.each(lambda x: x[k], tmp_body)
                if len(field_k) > 0:
                    tmp_body = reduce(T.list, T.each(lambda x: x[k], tmp_body))
                tmp_body = T.list(tmp_body)
            if bool(opt) and "uniq" in opt and opt['uniq']:
                tmp_body = T.uniq(tmp_body)
        return tmp_body

    __pluck = """
    ### T.pluck
        Pluck the list element of collections.
        eg:
            from funclib import T
            persons = [{"name": "Tom", "hobbies": ["sing", "running"]},
                {"name": "Jerry", "hobbies": []},
                {"name": "Mary", "hobbies": ['hiking', 'sing']}]

            hobbies = T.pluck(persons, 'hobbies')
            hobbies_uniq = T.pluck(persons, 'hobbies', uniq=True)

            print(hobbies)      # => ["sing", "running", 'hiking', 'sing']
            print(hobbies_uniq) # => ["sing", "running", 'hiking']
    """

    @staticmethod
    def every(predicate, _list):
        if bool(_list) and (isinstance(_list, list) or isinstance(_list, tuple)):
            for item in _list:
                if predicate != item:
                    if isinstance(predicate, dict):
                        for key in predicate:
                            if key not in item or predicate[key] != item[key]:
                                return False
                    elif 'function' in str(type(predicate)):
                        if not bool(predicate(item)):
                            return False
                    else:
                        return False
            return True
        return False
    __every = """
    ### T.every
        Returns true if all of the values in the list pass the predicate truth test.
        Short-circuits and stops traversing the list if a false element is found.
        eg:
            from funclib import T
            num_list = [1, 1, 2, 3, 5, 8]
            persons = [{"name": "Tom", "age": 12, "sex": "m"},
                       {"name": "Jerry", "age": 20, "sex": "m"},
                       {"name": "Mary", "age": 35, "sex": "f"}]

            is_all_five = T.every(5, num_list)
            is_all_male = T.every({"sex": "m"}, persons)
            is_all_adult = T.every(lambda x: x['age'] > 18, persons)
            print(is_all_five)   # => False
            print(is_all_male)   # => False
            print(is_all_adult)  # => False
    """

    @staticmethod
    def some(predicate, _list):
        if bool(_list) and (isinstance(_list, list) or isinstance(_list, tuple)):
            for item in _list:
                if predicate != item:
                    if isinstance(predicate, dict):
                        tmp_bool = True
                        for key in predicate:
                            if key not in item or predicate[key] != item[key]:
                                tmp_bool = False
                        if tmp_bool:
                            return True
                    elif 'function' in str(type(predicate)):
                        if bool(predicate(item)):
                            return True
                else:
                    return True
            return False
        return False

    __some = """
    ### T.some
        Returns true if any of the values in the list pass the predicate truth test.
        Short-circuits and stops traversing the list if a true element is found.
        eg:
            from funclib import T
            num_list = [1, 1, 2, 3, 5, 8]
            persons = [{"name": "Tom", "age": 12, "sex": "m"},
                       {"name": "Jerry", "age": 20, "sex": "m"},
                       {"name": "Mary", "age": 35, "sex": "f"}]

            is_any_five = T.some(5, num_list)
            is_any_male = T.some({"sex": "m"}, persons)
            is_any_adult = T.some(lambda x: x['age'] > 18, persons)
            print(is_any_five)   # => True
            print(is_any_male)   # => True
            print(is_any_adult)  # => True
    """

    @staticmethod
    def list(*values):
        def list_handler(val):
            if isinstance(val, list):
                return val
            return [val]

        if len(values) == 0:
            return []
        elif len(values) == 1:
            return list_handler(values[0])
        else:
            return reduce(lambda a, b: list_handler(a) + list_handler(b), values)

    __list = """
    ### T.list
        Return now system time.
        eg:
            from funclib import T
            print(T.list())       # => []
            print(T.list([]))     # => []
            print(T.list({}))     # => [{}]
            print(T.list(None))   # => [None]
            print(T.list('test')) # => ['test']
    """

    @staticmethod
    def dump(_json):
        if isinstance(_json, list) or isinstance(_json, dict) or isinstance(_json, tuple):
            return json.dumps(_json, sort_keys=True, indent=2)
        return _json

    __dump = """
    ### T.dump
        Return a formatted json string.
        eg:
            from funclib import T
            persons = [{"name": "Tom", "hobbies": ["sing", "running"]},
                {"name": "Jerry", "hobbies": []}]
            print(T.dump(persons)) #=>
            [
              {
                "hobbies": [
                  "sing", 
                  "running"
                ], 
                "name": "Tom"
              }, 
              {
                "hobbies": [], 
                "name": "Jerry"
              }
            ]
    """

    @staticmethod
    def clone(obj):
        return copy.deepcopy(obj)

    __clone = """
    ### T.clone
        Create a deep-copied clone of the provided plain object.
        eg:
            from funclib import T
            persons = [{"name": "Tom", "age": 12}, {"name": "Jerry", "age": 20}]
            persons_01 = persons
            persons_02 = T.clone(persons)
            T.find({'name': 'Tom'}, persons)['age'] = 18
            print(persons_01)  # => [{"name": "Tom", "age": 18}, {"name": "Jerry", "age": 20}]
            print(persons_02)  # => [{"name": "Tom", "age": 12}, {"name": "Jerry", "age": 20}]
    """

    @staticmethod
    def test(pattern, origin):
        return re.search(pattern, origin) is not None

    __test = """
    ### T.test
        Check is the match successful, a boolean value will be returned.
        eg:
            from funclib import T
            not_in = T.test(r'ab', 'Hello World!')
            in_str = T.test(r'll', 'Hello World!')
            print(not_in)  # => False
            print(in_str)  # => True
    """

    @staticmethod
    def replace(*args):
        return re.sub(*args)

    __replace = """
    ### T.replace
        Replace sub string of the origin string with re.sub()
        eg:
            from funclib import T
            info = 'Hello I'm Tom!'
            print(T.replace('Tom', 'Jack', info))  # => True
    """

    @staticmethod
    def iscan(exp):
        if isinstance(exp, str):
            try:
                exec (exp)
                return True
            except:
                return False
        return False

    __iscan = """
    ### T.iscan
        Test is the expression valid, a boolean value will be returned.
        eg:
            from funclib import T
            print(T.iscan(int('a')))  # => False
            print(T.iscan(int(5)))  # => True
    """

    @staticmethod
    def log(msg='Have no Message!', title='FuncLib ( ' + __version + ' )', line_len=85):
        title = isinstance(title, str) and title or str(title) or 'FuncLib ( ' + __version + ' )'
        title = len(title) <= 35 and title or title[:35]
        line_b = '=' * line_len
        line_m = '-' * line_len
        title = ' ' * int((line_len - len(title)) / 2) + title
        print('%s\n%s\n%s' % (line_b, title, line_m))
        print(T.dump(msg))
        print(line_b)

    __log = """
    ### T.log
        Show log clear in console.
        eg:
            from funclib import T
            T.log([{"name": "Tom", "hobbies": ["sing", "running"]}, {"name": "Jerry", "hobbies": []}])

            # =>
===========================================================================
                            """ + __log_title + """
---------------------------------------------------------------------------
[
  {
    "hobbies": [
      "sing", 
      "running"
    ], 
    "name": "Tom"
  }, 
  {
    "hobbies": [], 
    "name": "Jerry"
  }
]
===========================================================================
    """

    @staticmethod
    def timer(fn, times=60, interval=1):
        if 'function' not in str(type(fn)) or not isinstance(times, int) or not isinstance(interval, int) \
                or times < 1 or interval < 0:
            return
        is_time_out = False
        count = 0
        while True:
            count += 1
            if count == times:
                fn()
                is_time_out = True
                break
            elif fn():
                break
            time.sleep(interval)
        return is_time_out

    __timer = """
    ### T.timer
        Set a timer with interval and timeout limit.
        eg: 
            from funclib import T
            count = 0
            def fn():
                global count
                if count == 4:
                    return True
                count += 1
                print(count)
            T.timer(fn, 10, 2)
            # =>
                >>> 1  #at 0s
                >>> 2  #at 2s
                >>> 3  #at 4s
                >>> 4  #at 4s
    """

    @staticmethod
    def now():
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    __now = """
    ### T.now
        Return now system time.
        eg:
            from funclib import T
            print(T.now()) # => '2018-2-1 19:32:10'
    """

    @staticmethod
    def help(*args, **kwargs):
        row_cols = 6
        docs_info = T.info()
        keys = docs_info['keys']
        docs = docs_info['docs']
        max_len = max(T.each(lambda x: len(x), keys)) + 6
        if len(args) > 0:
            if args[0] in keys:
                T.__clear()
                T.log(docs[args[0]], T.__log_title_fix + args[0])
            if 'keep' in kwargs and kwargs['keep']:
                T.help(**kwargs)
        else:
            if not ('keep' in kwargs and kwargs['keep']):
                T.__clear()
                print (docs['info'])
            elif not ('info' in kwargs and kwargs['info']):
                print ('')
                hints = T.each(lambda x: T.__fixstrlen(T.__fixstrlen(str(keys.index(x))) + ': T.' + x, max_len), keys)
                end = 0
                while True:
                    sta = end
                    end = end + row_cols
                    if end > len(hints):
                        hints.append(' ' * (end - len(hints)) * max_len + ' ')
                        end = len(hints)
                    print '[ ' + reduce(lambda a, b: a + ' ' + b, hints[sta:end]) + ']'
                    if end == len(hints):
                        break
                print ('')
            idx = raw_input('Input a index (Nothing input will return): ')
            if idx:
                if T.iscan('int(%s)' % idx) and int(idx) in range(0, len(keys)):
                    T.__clear()
                    key = keys[int(idx)]
                    if idx == '0':
                        print (docs[key])
                        return T.help(keep=True, info=True)
                    else:
                        T.log(docs[key], T.__log_title_fix + key)
                T.help(keep=True)

    __help = """
    ### T.help
        Return the FuncLib or it's method doc
        eg:
            from funclib import T
            T.help('index')
            # => 
===========================================================================
                 """ + __log_title_fix + """index 
---------------------------------------------------------------------------
""" + __index + """
===========================================================================
        """

    @staticmethod
    def __clear():
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')

    @staticmethod
    def __fixstrlen(string, max_len=14):
        length = len(string)
        if length == 1:
            return ' ' + string
        elif 2 < length < max_len:
            return string + ' ' * (max_len - length)
        return string
