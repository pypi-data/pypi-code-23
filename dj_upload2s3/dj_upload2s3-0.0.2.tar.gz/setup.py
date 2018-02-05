from distutils.core import setup
from setuptools import find_packages

VERSION = '0.0.2'

CLASSIFIERS = [
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Topic :: Software Development',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Environment :: Web Environment',
    'Development Status :: 3 - Alpha',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

setup(
    name='dj_upload2s3',
    description='Django Direct Upload files to S3',
    version=VERSION,
    author='Alexandre Busquets',
    author_email='abusquets@gmail.com',
    license='MIT License',
    platforms=['OS Independent'],
    url='https://github.com/Microdisseny/dj_upload2s3',
    packages=find_packages(exclude=['__pycache__']),
    include_package_data=True,
    classifiers=CLASSIFIERS,
    zip_safe=False,
)
