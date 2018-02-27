import io
import re
from os.path import join, dirname, abspath
from setuptools import setup, find_packages


def read(name):
    here = abspath(dirname(__file__))
    return io.open(
        join(here, name), encoding='utf8'
    ).read()


setup(
    name="vmshepherd-zookeeper-driver",
    version="0.0.2",
    author='Krzysztof Warunek',
    author_email='krzysztof@warunek.net',
    url='https://github.com/kwarunek/vmshepherd-zookeeper-driver',
    description='Runtime and lock management for VmShepherd',
    long_description='%s\n%s' % (
        read('README.rst'),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=read('requirements.txt').split('\n'),
    zip_safe=False,
    entry_points={
        'vmshepherd.driver.runtime': ['ZookeeperDriver = vmshepherd_zookeeper_driver:ZookeeperDriver'],
    },
    keywords=['vmshepherd', 'openstack', 'zookeeper', 'runtime', 'lock'],
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: POSIX',
        'Development Status :: 4 - Beta'
    ]
)
