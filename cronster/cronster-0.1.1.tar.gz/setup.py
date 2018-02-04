from setuptools import setup, find_packages

with open('README.rst', 'r') as f:
    readme = f.read()

requirements = [
    'croniter',
    'click',
    'PyYaml',
    'redis',
    'tabulate'
]
test_requirements = [
    'pytest',
    'pytest-cov',
    'sphinx',
    'sphinx_rtd_theme'
]

setup(
    name='cronster',
    version='0.1.1',
    description='Crawl filesystems for crontab files and schedule jobs.',
    long_description=readme,
    url='https://github.com/florianeinfalt/cronster',
    author='Florian Einfalt',
    author_email='info@florianeinfalt.de',
    license='Apache 2.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    install_requires=requirements,
    tests_require=test_requirements,
    entry_points={
        'console_scripts': [
            'cronster_crawler = cronster.crawler:cli',
            'cronster_scheduler = cronster.scheduler:cli'
        ]
    },
)
