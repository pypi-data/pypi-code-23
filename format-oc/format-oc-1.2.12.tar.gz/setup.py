from setuptools import setup

setup(
	name='format-oc',
	version='1.2.12',
	url='https://github.com/ouroboroscoding/format-oc-python',
	description='Format-OC is a system designed in several languages that uses JSON files to define documents and their allowed parameters to such a fine degree that almost no knowledge of databases is required to get a fully functional back-end, with admin functions, up and running.',
	keywords=['data','format','database','db','sql','nosql'],
	author='Chris Nasr - OuroborosCoding',
	author_email='ouroboroscode@gmail.com',
	license='Apache-2.0',
	packages=['FormatOC'],
	install_requires=[],
	test_suite='tests',
	zip_safe=True
)
