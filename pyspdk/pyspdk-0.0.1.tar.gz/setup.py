# coding:utf8
from setuptools import setup, find_packages

setup(
    name='pyspdk',     # 包名
    version='0.0.1',     # 版本号
    author='helloway',
    author_email='simple_hlw@163.com',
    packages=find_packages('pyspdk'),  # 包括所有pysdpk中的包
    package_dir={'': 'pyspdk'},   # 告诉distutils包都在pysdpk下
    package_data={
        # 任何包中含有.md文件，都包含它
        '': ['*.md'],
        # 包含pysdpk包proto文件夹中的 *.proto文件
        'pyspdk': ['proto/*.proto']
    },
    # 包内所有文件指的是受版本控制（CVS/SVN/GIT等）的文件，或者通过MANIFEST.in声明
    include_package_data=True, install_requires=['google', 'psutil']
)
