from setuptools import setup

setup(
    name='sniffy',
    version='0.0.1',
    description='Sniffy prints information about captured TCP packages.',
    keywords='sample setuptools development',  # Optional
    py_modules=['sniffy'],
    install_requires=['dpkt', 'pypcap'],
    entry_points={
        'console_scripts': [
            'sniffy=sniffy:main',
        ],
    }
)
