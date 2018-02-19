from setuptools import setup
from setuptools import find_packages

setup(name='elefas',
      version='0.1.7',
      description='Friendly hyperparameter optimization ',
      author='Maciej Mikulski',
      author_email='maciej.mikulski@doctoral.uj.edu.pl',
      url='https://github.com/mjmikulski/elefas',
      license='MIT',
      install_requires=['numpy>=1.9.1',
                        'python>=3.6'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      keywords='hyperparameters optimization',
      packages=find_packages())
