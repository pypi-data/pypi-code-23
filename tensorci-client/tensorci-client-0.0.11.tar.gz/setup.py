from setuptools import setup, find_packages

setup(name='tensorci-client',
      version='0.0.11',
      description='TensorCI API Client',
      url='https://github.com/tensorci/tensorci-client',
      author='Ben Whittle',
      author_email='benwhittle31@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
        'requests==2.18.4',
        'awesome-slugify==1.6.5',
        'redis==2.10.6',
        'websocket-client==0.47.0'
      ],
      zip_safe=False)
