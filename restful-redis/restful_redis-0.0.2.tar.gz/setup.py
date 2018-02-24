from setuptools import setup, find_packages

setup(name='restful_redis',
      version='0.0.2',
      description='Redis queues for synchronous server2server ops',
      url='https://github.com/whittlbc/restful_redis',
      author='Ben Whittle',
      author_email='benwhittle31@gmail.com',
      license='MIT.',
      packages=find_packages(),
      install_requires=[
        'redis==2.10.6'
      ],
      zip_safe=False)