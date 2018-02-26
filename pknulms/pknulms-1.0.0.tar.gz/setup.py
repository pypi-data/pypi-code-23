import os
from setuptools import setup


def get_content(path):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    with open(path) as f:
        return f.read()


setup(
    name='pknulms',
    version='1.0.0',
    url='https://github.com/hallazzang/pknulms-py',
    license='MIT',
    author='Hanjun Kim',
    author_email='hallazzang@gmail.com',
    description='Pukyong National University Smart-LMS Python client',
    long_description=get_content('README.md'),
    py_modules=['pknulms'],
    install_requires=[
        'requests',
    ],
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
