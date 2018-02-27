from setuptools import setup, find_packages

import puppeteer_pdf


setup(
    name='django-puppeteer-pdf',
    packages=find_packages(),
    include_package_data=True,
    version=puppeteer_pdf.__version__,
    description='Converts HTML to PDF using puppeteer.',
    long_description=open('README.rst').read(),
    license='BSD-2-Clause',
    author=puppeteer_pdf.__author__,
    author_email='admin@incuna.com',
    url='https://github.com/incuna/django-puppeteer-pdf',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Framework :: Django',
    ],
    keywords='django puppeteer pdf',
)
