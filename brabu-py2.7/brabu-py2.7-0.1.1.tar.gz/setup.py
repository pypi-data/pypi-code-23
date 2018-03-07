# -*- coding: utf-8 -*-
from setuptools import setup, findall, find_packages
import sys, os
from subprocess import check_call

py_version = sys.version_info[0]
py_version_minor = sys.version_info[1]
version_num = '{}.{}'.format(py_version, py_version_minor)
if py_version  == 3:
    qt_ui_version = '5'
else:
    qt_ui_version = '4'

pyuic_comm = 'pyuic{0}'.format(qt_ui_version)
pyuic_compl1 = 'brabu/gui/brams.ui.qt{0}'.format(qt_ui_version)
pyuic_compl2 = "-o brabu/gui/brams.py"

os_system_line = "{} {} {}".format(pyuic_comm, pyuic_compl1, pyuic_compl2)
print(os_system_line)
os.system(os_system_line)
# check_call([pyuic_comm, pyuic_compl1, pyuic_compl2])

setup(
    name='brabu-py{}'.format(version_num),
    version='0.1.1',
    url='http://brams.cptec.inpe.br/',
    license='GNU General Public License',
    author='Luiz Flavio Rodrigues, Denis Eiras',
    author_email='luflarois@gmail.com, denis.eiras@gmail.com',
    keywords='BRABU BRAMS RAMSIN BUILD UTILITY',
    description='BRAMS Ramsin Build Utility for Python {}'.format(version_num),
    include_package_data=True,
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required
    #packages=['brabu'],
    package_dir={'brabu': 'brabu'},
    data_files=[
        ('data/gui', findall('data/gui')),
        ('data/ramsin_controller', ['data/ramsin_controller/variables.dat', 'data/ramsin_controller/RAMSIN_template']),
        ('data/ramsin_controller/patterns', findall('data/ramsin_controller/patterns'))
    ],

    # install_requires=install_requires_array,
    install_requires = ['numpy==1.14.0;python_version=="3.5.*"', 'numpy==1.11.1;python_version=="2.7.*"',
                          'matplotlib==2.1.2', 'PyQt5==5.10;python_version=="3.5.*"'],

    python_requires='=={}.*'.format(version_num),

)
