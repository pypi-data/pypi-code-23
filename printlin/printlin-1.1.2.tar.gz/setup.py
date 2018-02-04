from distutils.core import setup  #从python发布工具导入setup函数

setup(
        name        = 'printlin',
        version     = '1.1.2',
        py_modules  = ['printl'],  #将模块元数据与setup函数关联
        author      = 'hfpy',
        author_email= 'xiangyu.lin@verycloud.cn',
        url         = 'http://www.linxy.top',
        description = 'A simple printer of nested list',
    )
