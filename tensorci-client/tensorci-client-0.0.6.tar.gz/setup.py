from setuptools import setup

setup(name='tensorci-client',
      version='0.0.6',
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