from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='hellotimostar',
    version='1.0',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
	entry_points={
	'console_scripts':
		['hello = hello.hello:hello',
		 'serve = hello.hello:run_server']
	},
	install_requires=[
		'Flask'
	],
	test_suite='tests',
	url='https://yandex.ru',
	author='Timofey Starodubtsev',
	author_email='timostar98@gmail.com'
)