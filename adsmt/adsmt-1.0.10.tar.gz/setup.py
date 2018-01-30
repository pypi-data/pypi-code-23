from setuptools import setup, find_packages


setup(
    name='adsmt',
    version='1.0.10',
    description='Active Directory Simple Management Toolkit',
    long_description='Simple Active Directory console-based management toolkit (CLI - command line interface)'
                     ' which is designed to execute basic administration of MSAD like creating, modifying,'
                     ' listing, deleting and searching users, groups, computers; printing and managing domain'
                     ' tree structure and so on. The point of this toolkit creation was to give to system'
                     ' administrators an ability to easily manage Samba4-based AD domains (when there is no'
                     ' ability to use GUI MS management console and samba utilities (samba-tool, ldbsearch'
                     ' and so on) are not comfortable to use.',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Systems Administration',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
        'Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP',
    ],
    keywords='ad active directory samba manage console cli',
    url='https://bitbucket.org/deniskhodus/adsmt',
    author='Denis Khodus',
    author_email='deniskhodus@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=['ldap3>=2.4'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'adsmt = adsmt.cli:main',
            'adcli = adsmt.cli:main'
        ]
    }
)
