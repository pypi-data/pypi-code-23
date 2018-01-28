import io
import re
from setuptools import setup


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('py_opt_collection/__init__.py', 'rb') as f:
    version = str(_version_re.search(
        f.read().decode('utf-8')
    ).group(1)).replace('\'', '')
with io.open('README.rst', encoding='utf-8') as f:
    description = f.read()
with io.open('docs/history.rst', encoding='utf-8') as f:
    description += "\n\n%s" % f.read()

setup(
    name='PyOptCollection',
    version=version,
    author='Nghia Tr. Nguyen',
    author_email='nghia@viisix.space',
    description='A collection of Optimization Algorithms.',
    long_description=description,
    packages=['py_opt_collection'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ]
)
