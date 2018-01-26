# -*- coding: utf-8 -*-


#以字符串的方式传入参数，解析该字符串参数，让它变成可以调用的函数或者方法
def load_class(name):
    components = name.split('.')
    module_path = '.'.join(components[:-1])
    class_name = components[-1]
    mod = __import__(module_path, fromlist=[class_name])
    klass = getattr(mod, class_name)
    return klass


def expand(template, count, params={}, value=None, expanders=[]):
    for expander_class in expanders:
        klass = load_class(expander_class)
        expander = klass(template, count, params, value)
        value = expander.expand()
    return value
