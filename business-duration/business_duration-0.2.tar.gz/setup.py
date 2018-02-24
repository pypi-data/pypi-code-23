from setuptools import setup

setup(name='business_duration',
	version='0.2',
	description='Calculates business duration in days, hours, minutes and seconds by excluding weekends, public holidays and non-business hours',
	url='https://github.com/gnaneshwar441/Business_Duration',
	author='Gnaneshwar G',
	author_email='gnaneshwar441@gmail.com',
	license='MIT',
	packages=['business_duration'],
	long_description=open('README.rst').read(),
	zip_safe=False)