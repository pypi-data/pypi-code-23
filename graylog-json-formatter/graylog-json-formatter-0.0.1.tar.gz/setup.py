from setuptools import setup, find_packages

VERSION = '0.0.1'

README = open('README.rst').read()

setup(
    name='graylog-json-formatter',
    version=VERSION,
    author='Shakurov Vadim Vladimirovich',
    author_email='apelsinsd@gmail.com',
    url='https://github.com/NewVadim/graylog-json-formatter',
    license='GNU General Public License v3 (GPLv3)',
    description='JSON formatter for graylog JSON extractor.',
    long_description=README,
    py_modules=['graylog_json_formatter'],
    include_package_data=True,
    test_suite='tests',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='graylog json',
    packages=find_packages(),
    zip_safe=False,
)
