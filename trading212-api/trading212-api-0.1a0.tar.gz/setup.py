from setuptools import setup, find_packages

setup(
    name="trading212-api",
    version="v0.1a0",
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    include_package_data=True,
    package_data={'': ['*.ini', 'logs/*.ini']},  # to check
    zip_safe=False,
    author="Federico Lolli",
    author_email="federico123579@gmail.com",
    description="Package to interact with the broker service Trading212",
    license="MIT",
    keywords="trading api",
    url="https://gitlab.com/federico123579/Trading212api",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: User Interfaces',
    ]
)
