import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='django-huangwei-course',
    version='0.1',
    packages=['course'],
    description='A line of description',
    long_description=README,
    author='huangwei',
    author_email='imonyse@gmail.com',
    license='MIT',
    install_requires=[
        'Django==1.11',
    ]
)
