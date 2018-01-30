from setuptools import setup, find_packages


setup(
    name='genorm',
    version='0.1.2',
    description='GenORM (simple functional MySQL/PostgreSQL ORM)',
    # long_description='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Database :: Front-Ends',
    ],
    keywords='orm mysql psql postgres postgresql genorm',
    url='https://bitbucket.org/deniskhodus/genorm',
    author='Denis Khodus',
    author_email='deniskhodus@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=['Pillow'],
    include_package_data=False,
    zip_safe=False,
    # entry_points={
    #     'console_scripts': [
    #         'adsmt = adsmt.cli:main',
    #         'adcli = adsmt.cli:main'
    #     ]
    # }
)

