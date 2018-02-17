from setuptools import setup

setup(
	name='janitor_cleaner',
	version='0.2',
	description='Clean your disk drives with ease',
	url='http://github.com/vedantrathore/janitor',
	author='Vedant Rathore',
	author_email='vedantr1998@gmail.com',
	license='MIT',
	zip_safe=False,
	include_package_data=True,
	install_requires=[
		'Click'
	],
	entry_points={
		'console_scripts':['janitor=src.cli:main']
	}
)
