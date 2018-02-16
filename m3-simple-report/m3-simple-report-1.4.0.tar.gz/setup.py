# coding: utf-8
from os.path import dirname
from os.path import join

from pip.download import PipSession
from pip.req.req_file import parse_requirements
from setuptools import find_packages
from setuptools import setup


def _get_requirements(file_name):
    pip_session = PipSession()
    requirements = parse_requirements(file_name, session=pip_session)

    return tuple(str(requirement.req) for requirement in requirements)


setup(
    name='m3-simple-report',
    description=u'Генератор отчетов',
    url='https://stash.bars-open.ru/projects/M3/repos/simple-report',
    license='MIT',
    author='BARS Group',
    author_email='bars@bars-open.ru',
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=_get_requirements('requirements.txt'),
    include_package_data=True,
    dependency_links=(
        'http://pypi.bars-open.ru/simple/m3-builder',
    ),
    setup_requires=(
        'm3-builder>=1.1',
    ),
    set_build_info=dirname(__file__),
)
