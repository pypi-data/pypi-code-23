from setuptools import setup, find_packages
import bubot

setup(
    name='bubot',
    version=bubot.__version__,
    description='',
    long_description='',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 3 - Alpha',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: AsyncIO',
    ],
    keywords='funniest joke comedy flying circus',
    url='http://github.com/businka/bubot',
    author='Razgovorov Mikhail',
    author_email='',
    license='Apache 2',
    packages=['bubot'],
    python_requires='>=3.5.0',
    install_requires=[
        'aiohttp',
        'aiohttp_session',
        'aiohttp_jinja2',
        'cryptography', 'motor', 'jinja2', 'asyncio_redis', 'bson',
    ],
    include_package_data=True,
    zip_safe=False
)
