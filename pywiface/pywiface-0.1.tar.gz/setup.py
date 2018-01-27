from setuptools import setup

setup(
    name='pywiface',
    version='0.1',
    packages=['pywiface'],
    url='',
    license='MIT',
    author="Keane O'Kelley",
    author_email='keane.m.okelley@gmail.com',
    description='Python wrapper for managing wireless interfaces',
    scripts=['scripts/pywiface'],
    install_requires=[
        'scapy-python3',
        'termcolor'
    ]
)
