from setuptools import setup

setup(name='atkspy',
      version='0.1',
      description='A python package that supports SOAP interface to communicate with the Microsoft ATKS',
      url='https://github.com/AliAbdelaal/ATKSpy',
      author='Ali Abdelaal',
      author_email='aliabdelaal369@gmail.com',
      license='MIT',
      packages=['atkspy'],
      install_requires=[
          'zeep',
      ],
      python_requires='>=3',
      zip_safe=False)