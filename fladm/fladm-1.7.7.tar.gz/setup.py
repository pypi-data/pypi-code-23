import io
from setuptools import find_packages, setup


# Read in the README for the long description on PyPI
def long_description():
    return 'description'
    # with io.open('README.rst', 'r', encoding='utf-8') as f:
    #     readme = f.read()
    # return readme

setup(name='fladm',
      version='1.7.7',
      description='Flamingo admin cli tool',
      long_description=long_description(),
      url='http://gitlab.exem-oss.org/flamingo/flamingo-adm-cli.git',
      author='Jaeik Park',
      author_email='jaeikpark81@gmail.com',
      license='Apache2',
      packages=find_packages(),
      install_requires=['paramiko', 'requests', 'requests-toolbelt', 'pyoozie'],
      entry_points = {
        'console_scripts': ['fladm=fladm.cli:main', 'flcli=flcli.cli:main']
      },
      exclude_package_data={
            '': ['flcli/cookie.dat']
      },
      package_data={'': ['*.json']},
      classifiers=[
          'Programming Language :: Python :: 2.7'
      ],
      zip_safe=False)
