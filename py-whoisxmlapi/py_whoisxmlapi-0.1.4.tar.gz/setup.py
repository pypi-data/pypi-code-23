from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='py_whoisxmlapi',
      version='0.1.4',
      description='Python3 WhoisService data parser',
      long_description=readme(),
      url='https://bitbucket.org/tvdsluijs/py_whoisxmlapi',
      author='Theo van der Sluijs',
      author_email='theo@vandersluijs.nl',
      license='CC BY-NC-SA 4.0',
      classifiers=[
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
        ],
      keywords='whois domains',
      packages=['py_whoisxmlapi'],
      zip_safe=False)