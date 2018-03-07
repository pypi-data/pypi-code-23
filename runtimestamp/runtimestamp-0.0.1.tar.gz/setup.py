import sys
from setuptools import setup

setup(name='runtimestamp',
	packages=['runtimestamp'],
	version='0.0.1',
	description='Leaves an timestamp and signature at the top of every notebook',
	author='leon yin',
	author_email='ly501@nyu.edu',
	url='https://github.com/yinleon/runtimestamp',
	keywords='jupyter notebook, timestamp',
	license='MIT',
	install_requires=[
		'platform',
		'datetime',
	]
)
