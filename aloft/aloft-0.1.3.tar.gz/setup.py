from setuptools import setup

setup(name='aloft',
      version='0.1.3',
      description='Tool to manage Kubernetes clusters and helm charts across multiple AWS accounts and clusters',
      packages=['aloft'],
      scripts=['bin/aloft'],
      zip_safe=False,
      install_requires=['boto3', 'jinja2', 'PyYAML', 'docopt']
      )
