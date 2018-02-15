from setuptools import setup, find_packages

setup(
     name='wu-aut-register-script',
     version='1.1',
     description='A useful module to make a fast automatic register for lectures and exams',
     author='Harald Deutschmann',
     author_email='harald.deutschmann@student.tugraz.at',
     scripts=['wuRegister.py'],
     install_requires=['requests', 'bs4', 'Pool', 'datetime']
)
