""" 从Python发布工具导入"setup"函数 """
from distutils.core import setup

setup(
        name = 'python_sanitize',
        version = '1.0.0',
        py_modules = ['python_sanitize'],#将模块的元数据与setup函数的参数关联
        author = 'dmlpython',
        author_email = '1252366224@qq.com',
        url = 'https://gitee.com/Violaine/events',
        description = '增加一个函数参数实现缩进控制开关',
    )
