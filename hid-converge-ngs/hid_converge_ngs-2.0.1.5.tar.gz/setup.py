from setuptools import setup

setup(
	name='hid_converge_ngs',
	version='2.0.1.5',
	author='HID',
	license='Thermofisher Scientific',
	packages=['ngs','service','utils'],
	install_requires=['hid_converge'],
	dependency_links=['https://pypi.python.org/pypi/hid_converge'],
	include_package_data=False,
	zip_safe=False
)
