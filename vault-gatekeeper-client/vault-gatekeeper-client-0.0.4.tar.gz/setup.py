from distutils.core import setup


setup(name='vault-gatekeeper-client',
      version='0.0.4',
      description='vault-gatekeeper-client for interacting with vault-gatekeeper-mesos service',
      url='https://github.com/jensendw/vault-gateway-client',
      author='Daniel Jensen',
      author_email='jensendw@gmail.com',
      license='Apache',
      packages=['vault_gatekeeper_client'],
      install_requires=[
          'hvac',
          'requests'
      ],
      zip_safe=False)
