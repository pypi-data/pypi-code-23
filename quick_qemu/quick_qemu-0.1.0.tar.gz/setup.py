#! /usr/bin/env python3
"""
license: MIT, see LICENSE.txt
"""

from setuptools import setup

version = "0.1.0"


entry_points = {"console_scripts": []}
install_requirements = []


entry_points["console_scripts"].append('quick_qemu = quick_qemu:main')

setup(name='quick_qemu',
      version=version,
      #version_format='{tag}',
      description='Quick start qemu machines',
      author='Alexander K.',
      author_email='devkral@web.de',
      license='MIT',
      url='https://github.com/devkral/quick_qemu',
      download_url='https://github.com/devkral/quick_qemu/tarball/v'+version,
      entry_points=entry_points,
      #zip_safe=True,
      platforms='Platform Independent',
      include_package_data=True,
      package_data={
          '': ['*.txt', '*.md'],
      },
      install_requires=install_requirements,
      packages=['quick_qemu', 'quick_qemu.quick_qemu'],
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3 :: Only'],
      keywords=['qemu', 'helper'])
