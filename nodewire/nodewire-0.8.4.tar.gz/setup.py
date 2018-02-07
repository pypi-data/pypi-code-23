from setuptools import setup
# https://python-packaging.readthedocs.io/en/latest/minimal.html
# python setup.py sdist upload

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='nodewire',
      version='0.8.4',
      description='NodeWire',
      long_description=readme(),
      url='http://www.nodewire.org',
      author='Ahmad Sadiq',
      author_email='sadiq.a.ahmad@gmail.com',
      license='BSD',
      packages=['nodewire'],
      scripts=['bin/nw_script.py', 'bin/nw_gateway.py', 'bin/nw_client.py'],
      install_requires=[
            #'paho-mqtt',   # no longer needed
            'configparser',
            #'netifaces', # no longer needed
            'pyserial',
            'requests',
            'asyncio'
      ],
      zip_safe=False)
