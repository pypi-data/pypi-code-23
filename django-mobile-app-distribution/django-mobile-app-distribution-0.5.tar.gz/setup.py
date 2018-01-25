import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-mobile-app-distribution',
    version='0.5',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License', 
    description='A Django app that adds iOS and Android app upload functionality to the Django admin interface.  Provides a mobile optimized HTML fronted for clients to download Ad Hoc mobile applications using their iOS or Android devices.',
    long_description=README,
    url='https://github.com/Proper-Job/django-mobile-app-distribution',
    author='Moritz Pfeiffer',
    author_email='moritz.pfeiffer@alp-phone.ch',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=['future', 'Pillow']
)
