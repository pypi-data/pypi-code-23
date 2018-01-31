#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/23 9:55
# @Author  : chenjw
# @Site    : 
# @File    : jsonParse.py
# @Software: PyCharm Community Edition
# @Desc    :  do what

import json

class JsonParse:
    def __init__(self, target=None):
        if target is None:
            self.Dict = {}
        elif isinstance(target, str):
            self.Dict = json.loads(target)
        elif isinstance(target, dict):
            self.Dict = json.loads(json.dumps(target))
        else:
            self.Dict = {}

    def isEmpty(self):
        if len(self.Dict) == 0:
            return True
        return False

    def Exist(self, key):
        return self.exist(key, self.Dict)

    # inner func
    def exist(self, key, default_dict):
        if isinstance(key, str) is False:
            return False
        if key in default_dict.keys():
            return True
        else:
            return False

    def Val(self, key):
        return self.val(key, self.Dict)

    # inner func
    def val(self, key, default_dict):
        if self.exist(key, default_dict) is False:
            return None
        else:
            return default_dict[key]

    def ExistP(self, keyP):
        if isinstance(keyP, str) is False:
            return False
        return self.existP(keyP, self.Dict)

    # inner func
    def isInt(self, s):
        try:
            if int(s) >= 0:
                return True
            return False
        except:
            return False

    # inner func
    def existP(self, keyP, default_dict=None, default_list=None):
        if default_dict is None and default_list is None:
            return False
        if keyP == '':
            return False
        index = keyP.find('/')
        if index < 0:
            if default_dict is not None:
                return self.exist(keyP, default_dict)
            else:
                return False
        elif index == 0:
            if len(keyP) > 1:
                return self.existP(keyP[1:], default_dict, default_list)
            else:
                return False
        elif index == len(keyP) - 1:
            return self.existP(keyP[:-1], default_dict, default_list)
        else:
            pre = keyP[:index]
            suffix = keyP[index + 1:]
            if isinstance(default_dict, dict) and self.exist(pre, default_dict):
                tmp = default_dict[pre]
                if isinstance(tmp, dict):
                    return self.existP(suffix, tmp, None)
                elif isinstance(tmp, list):
                    return self.existP(suffix, None, tmp)
                return False
            elif self.isInt(pre) and isinstance(default_list, list) and int(pre) < len(default_list) and isinstance(
                    default_list[int(pre)], dict):
                return self.existP(suffix, default_list[int(pre)], None)
            else:
                return False

    def ValP(self, keyP):
        if self.ExistP(keyP.strip()) is False:
            return None
        return self.valP(keyP.strip(), self.Dict)

    # inner func
    def valP(self, keyP, default_dict=None, default_list=None):
        if default_dict is None and default_list is None:
            return None
        if keyP == '':
            return None
        index = keyP.find('/')
        if index < 0:
            if default_dict is not None and self.exist(keyP, default_dict):
                return default_dict[keyP]
            else:
                return None
        elif index == 0:
            if len(keyP) > 1:
                return self.valP(keyP[1:], default_dict, default_list)
            else:
                return None
        elif index == len(keyP) - 1:
            return self.valP(keyP[:-1], default_dict, default_list)
        else:
            pre = keyP[:index]
            suffix = keyP[index + 1:]
            if isinstance(default_dict, dict) and self.exist(pre, default_dict):
                tmp = default_dict[pre]
                if isinstance(tmp, dict):
                    return self.valP(suffix, tmp, None)
                elif isinstance(tmp, list):
                    return self.valP(suffix, None, tmp)
                return None
            elif self.isInt(pre) and isinstance(default_list, list) and int(pre) < len(default_list) and isinstance(
                    default_list[int(pre)], dict):
                return self.valP(suffix, default_list[int(pre)], None)
            else:
                return None

    def Ary(self, key):
        return self.ary(key, self.Dict)

    # inner func
    def ary(self, key, default_dict):
        if self.exist(key, default_dict) is False:
            return None
        else:
            tmp = default_dict[key]
            if isinstance(tmp, list):
                return tmp
            else:
                return None

    def AryP(self, keyP):
        if self.ExistP(keyP) is False:
            return None
        return self.aryP(keyP, self.Dict, None)

    # inner func
    def aryP(self, keyP, default_dict=None, default_list=None):
        if default_dict is None and default_list is None:
            return None
        if keyP == '':
            return None
        index = keyP.find('/')
        if index < 0:
            if default_dict is not None and self.exist(keyP, default_dict):
                return self.ary(keyP, default_dict)
            else:
                return None
        elif index == 0:
            if len(keyP) > 1:
                return self.aryP(keyP[1:], default_dict, default_list)
            else:
                return None
        elif index == len(keyP) - 1:
            return self.aryP(keyP[:-1], default_dict, default_list)
        else:
            pre = keyP[:index]
            suffix = keyP[index + 1:]
            if isinstance(default_dict, dict) and self.exist(pre, default_dict):
                tmp = default_dict[pre]
                if isinstance(tmp, dict):
                    return self.aryP(suffix, tmp, None)
                elif isinstance(tmp, list):
                    return self.aryP(suffix, None, tmp)
                return None
            elif self.isInt(pre) and isinstance(default_list, list) and int(pre) < len(default_list) and isinstance(
                    default_list[int(pre)], dict):
                return self.aryP(suffix, default_list[int(pre)], None)
            else:
                return None

    def Int(self, key):
        try:
            return int(self.Val(key))
        except:
            return 0

    def IntP(self, key):
        try:
            return int(self.ValP(key))
        except:
            return 0

    def Float(self, key):
        try:
            return float(self.Val(key))
        except:
            return 0

    def FloatP(self, key):
        try:
            return float(self.ValP(key))
        except:
            return 0

    def Str(self, key):
        try:
            return str(self.Val(key))
        except:
            return ''

    def StrP(self, key):
        try:
            return str(self.ValP(key))
        except:
            return ''

    def Json(self, key):
        try:
            return JsonParse(self.Val(key))
        except:
            return JsonParse({})

    def JsonP(self, key):
        try:
            return JsonParse(self.ValP(key))
        except:
            return JsonParse({})

    def toInt(self, default_list=None):
        if isinstance(default_list, list) is False:
            return None
        int_list = []
        for sin_item in default_list:
            if isinstance(sin_item, int):
                int_list.append(sin_item)
            else:
                return None
        return int_list

    def AryInt(self, key):
        try:
            return list(self.toInt(self.Ary(key)))
        except:
            return []

    def AryIntP(self, key):
        try:
            return list(self.toInt(self.AryP(key)))
        except:
            return []

    def toFloat(self, default_list=None):
        if isinstance(default_list, list) is False:
            return None
        float_list = []
        for sin_item in default_list:
            if isinstance(sin_item, float) or isinstance(sin_item, int):
                float_list.append(float(sin_item))
            else:
                return None
        return float_list

    def AryFloat(self, key):
        try:
            return list(self.toFloat(self.Ary(key)))
        except:
            return []

    def AryFloatP(self, key):
        try:
            return list(self.toFloat(self.AryP(key)))
        except:
            return []

    def toStr(self, default_list=None):
        if isinstance(default_list, list) is False:
            return None
        str_list = []
        for sin_item in default_list:
            if isinstance(sin_item, str):
                str_list.append(sin_item)
            else:
                return None
        return str_list

    def AryStr(self, key):
        try:
            return list(self.toStr(self.Ary(key)))
        except:
            return []

    def AryStrP(self, key):
        try:
            return list(self.toStr(self.AryP(key)))
        except:
            return []

    def toJson(self, default_list=None):
        if isinstance(default_list, list) is False:
            return None
        json_list = []
        for sin_item in default_list:
            if isinstance(sin_item, dict):
                json_list.append(JsonParse(sin_item))
            else:
                return None
        return json_list

    def AryJson(self, key):
        try:
            return list(self.toJson(self.Ary(key)))
        except:
            return []

    def AryJsonP(self, key):
        try:
            return list(self.toJson(self.AryP(key)))
        except:
            return []

    def toString(self):
        return json.dumps(self.Dict)

