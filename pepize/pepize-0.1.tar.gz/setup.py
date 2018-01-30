from setuptools import setup

setup(name='pepize',
      version='0.1',
      description='Easier than refactoring',
      url='http://github.com/Euphe/pepize',
      author='Boris Tseitlin',
      author_email='b.tseytlin@lambda-it.ru',
      license='MIT',
      packages=['pepize'],
      install_requires=[
          'stringcase',
      ],
      zip_safe=False)