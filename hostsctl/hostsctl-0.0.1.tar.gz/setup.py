from setuptools import setup

setup(
    name='hostsctl',
    version='0.0.1',
    packages=['hostsctl'],
    url='https://github.com/j-mak/hostman',
    license='MIT License',
    author='Jozef "sunny" Mak',
    author_email='sunny@jozefmak.eu',
    description='The hosts file manipulator',
    keywords=[
        'hosts'
    ],
    scripts=[
        'bin/hostsctl'
    ],
    classifiers=[
    ]
)
