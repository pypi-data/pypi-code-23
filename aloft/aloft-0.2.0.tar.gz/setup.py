from setuptools import setup

setup(name='aloft',
      version='0.2.0',
      description='Tool to manage Kubernetes clusters and helm charts across multiple AWS accounts and clusters',
      packages=['aloft'],
      python_requires='>=3.6',
      scripts=['bin/aloft'],
      zip_safe=False,
      install_requires=['boto3==1.5.26', 'jinja2==2.10', 'PyYAML==3.12', 'docopt==0.6.2']
      )
