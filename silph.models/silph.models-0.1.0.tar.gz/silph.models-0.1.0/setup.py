from setuptools import setup

lib_name = 'silph.models'

setup(
    name=lib_name,
    version='0.1.0',
    author='Marco Ceppi',
    author_email='marco@thesilphroad.com',
    description='Database models for TSR',
    license='other',
    classifiers=[
        'License :: Other/Proprietary License',
        'Topic :: Database',
        'Development Status :: 5 - Production/Stable',
    ],
    namespace_packages=['silph'],
    packages=[lib_name],
    install_requires=[
        'asyncqlio',
        'aiomysql',
    ],
    dependency_links=[
        'git+https://github.com/Unplottable/asyncqlio.git@discord-bot#egg=asynclio',
    ]
)
