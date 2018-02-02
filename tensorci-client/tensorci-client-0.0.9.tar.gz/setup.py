from setuptools import setup, find_packages

setup(name='tensorci-client',
      version='0.0.9',
      description='TensorCI API Client',
      url='https://github.com/tensorci/tensorci-client',
      author='Ben Whittle',
      author_email='benwhittle31@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
        'requests',
        'awesome-slugify',
        'redis'
      ],
      zip_safe=False)