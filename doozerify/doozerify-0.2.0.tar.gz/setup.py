from setuptools import setup
import sys


def read(filename):
    with open(filename) as f:
        return f.read()


setup(
    name='doozerify',
    version='0.2.0',
    author='Andy Dirnberger',
    author_email='andy@dirnberger.me',
    url='https://gitlab.com/dirn/doozerify',
    description='A tool to aid the transition from Henson to Doozer',
    long_description=read('README.rst'),
    license='MIT',
    pymodules=['doozerify'],
    zip_safe=False,
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
