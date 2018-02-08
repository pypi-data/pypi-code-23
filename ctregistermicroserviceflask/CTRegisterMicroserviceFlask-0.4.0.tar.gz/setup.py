from setuptools import setup

setup(name='CTRegisterMicroserviceFlask',
      version='0.4.0',
      description='Library to interact with the Control-Tower api-gateway (register, do requests to other microservices, etc)',
      author='Sergio Gordillo',
      author_email='sergio.gordillo@vizzuality.com',
      license='MIT',
      packages=['CTRegisterMicroserviceFlask'],
      install_requires=[
        'flask',
        'requests'
      ],
      zip_safe=False)
