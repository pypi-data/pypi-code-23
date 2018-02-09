from distutils.core import setup  #从python发布工具导入setup函数

setup(
        name        = 'nocToolz',
        version     = '1.0.0',
        py_modules  = ['Toolz'],  #将模块元数据与setup函数关联
        author      = 'xiangyu.lin',
        author_email= 'xiangyu.lin@verycloud.cn',
        url         = 'http://www.linxy.top',
        description = 'A simple sendEmail function.',
    )
