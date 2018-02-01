from setuptools import setup

setup(name='tensorci_client',
      version='0.0.4',
      description='TensorCI API Client',
      url='https://github.com/tensorci/tensorci-client',
      author='Ben Whittle',
      author_email='benwhittle31@gmail.com',
      license='MIT',
      packages=['tensorci_client'],
      install_requires=[
        'requests',
        'awesome-slugify',
        'redis'
      ],
      zip_safe=False)