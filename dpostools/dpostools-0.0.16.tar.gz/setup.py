from setuptools import setup

setup(
    name='dpostools',
    version='0.0.16',
    packages=['dpostools', 'dpostools.tests', 'park'],
    url='https://github.com/BlockHub/blockhubdpostools.git',
    license='MIT',
    author='Charles',
    author_email='karel@blockhub.nl',
    description='generic toolkit for interacting with DPOS chains',
    include_package_data=True,
    package_data={'': ['yamls/*.yaml']},
    install_requires=[
          'pyyaml', 'psycopg2', 'arky',
      ],
    dependency_links=['https://github.com/faustbrian/ARK-Python/archive/master.zip']
)
