from setuptools import setup

setup(name='tensorci-client',
      version='0.0.2',
      description='TensorCI API Client',
      url='https://github.com/tensorci/tensorci-client',
      author='Ben Whittle',
      author_email='benwhittle31@gmail.com',
      license='MIT',
      packages=['tensorci'],
      install_requires=[
        'requests',
        'awesome-slugify'
      ],
      zip_safe=False)