from setuptools import setup

setup(name='cld',
      version='0.1.3',
      description='Tool to manage Kubernetes clusters and helm charts across multiple AWS accounts and clusters',
      packages=['cloudctl'],
      scripts=['bin/cloudctl'],
      zip_safe=False)
