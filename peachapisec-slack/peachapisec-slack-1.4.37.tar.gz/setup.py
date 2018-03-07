import os
from setuptools import setup

cwd = os.getcwd()
try:
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    setup(
        name = 'peachapisec-slack',
        description = 'Peach API Security Slack Notifications',
        long_description = open('README.rst').read(),
        author = 'Peach Tech',
        author_email = 'contact@peach.tech',
        url = 'https://peach.tech',
        version = '1.4.37',

        py_modules = ['peach2slack'],

        # update requirements.txt as well!
        install_requires = [
			'click>=6.7', 
			'peachapisec-api==1.4.37', 
			'requests>=2.18.4',
			'pystache'
			],
		
        entry_points = {
            'console_scripts': ['peach2slack=peach2slack:run'],
        },

        license = 'Apache License, Version 2.0',
        keywords = 'peach fuzzing security test rest',

        classifiers = [
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Topic :: Security',
            'Topic :: Software Development :: Quality Assurance',
            'Topic :: Software Development :: Testing',
            'Topic :: Utilities',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3'
        ])

finally:
    os.chdir(cwd)

# end
