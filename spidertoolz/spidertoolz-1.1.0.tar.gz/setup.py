from distutils.core import setup  #从python发布工具导入setup函数

setup(
        name        = 'spidertoolz',
        version     = '1.1.0',
        py_modules  = ['spider'],  #将模块元数据与setup函数关联
        author      = 'xiangyu.lin',
        author_email= 'xiangyu.lin@verycloud.cn',
        url         = 'http://www.linxy.top',
        description = 'A simple getUrl function.',
    )
