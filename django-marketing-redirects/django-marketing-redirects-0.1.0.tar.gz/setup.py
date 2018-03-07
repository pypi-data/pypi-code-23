import os
from setuptools import find_packages, setup


try:
    with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
        README = readme.read()
except Exception:
    README = '<failed to open README.rst>'


os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


install_dependencies = (
    'Django>=1.8',
)


setup(
    name='django-marketing-redirects',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='Redirect URLs including query parameters necessary for marketing use.',
    long_description=README,
    author='jeffrey k eliasen',
    author_email='jeff+django-marketing-redirects@jke.net',
    url='https://github.com/seawolf42/django-marketing-redirects',
    zip_safe=False,
    keywords='django-marketing-redirects',
    classifiers=[
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=install_dependencies,
    tests_require=install_dependencies + ('mock',),
)
