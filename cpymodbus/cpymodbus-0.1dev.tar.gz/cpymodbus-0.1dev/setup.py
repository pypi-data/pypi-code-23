from distutils.core import setup, Extension

slave_module = Extension (
    'modbus_slave',
    include_dirs = ['/usr/include/modbus'],
    libraries = ['modbus'],
    sources = ['slave.c']
)

classifiers = ['Development Status :: 5 - Production/Stable',
               'Operating System :: POSIX :: Linux',
               'Intended Audience :: Developers',
               'Programming Language :: Python :: 2.6',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3',
               'Topic :: Software Development',
               'Topic :: Home Automation',
               'Topic :: System :: Hardware']

setup (
    name = 'cpymodbus',
    version = '0.1dev',
    description = 'Modbus slave package',
    author = 'Jonathan Daniel',
    author_email='qjonathandaniel@gmail.com',
    url='https://github.com/jonathan-daniel/CPyModbus',
    download_url = 'https://github.com/jonathan-daniel/CPyModbus/archive/0.1.tar.gz',
    keywords = ['modbus', 'libmodbus', 'pymodbus'],
    platforms=['linux'],
    classifiers = classifiers,
    ext_modules = [slave_module]
)