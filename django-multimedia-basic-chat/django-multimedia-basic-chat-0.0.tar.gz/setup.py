import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()


setup(
    name='django-multimedia-basic-chat',
    version='0.0',
    packages=['multimedia_chat'],
    description='A example django chat package',
    long_description=README,
    author='Faizan Shaikh',
    author_email='faizan.shaikh308@gmail.com',
    url='https://github.com/faizans-cuelogic/django-multimedia-basic-chat/',
    license='MIT',
    install_requires=[
        'Django>==1.10',
        'djangorestframework>==3.7.0',
    ]
)
