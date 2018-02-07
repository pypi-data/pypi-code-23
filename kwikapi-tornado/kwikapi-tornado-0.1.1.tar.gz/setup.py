from setuptools import setup, find_packages

# https://docs.djangoproject.com/en/1.11/intro/reusable-apps/
version = '0.1.1'
setup(
    name="kwikapi-tornado",
    version=version,
    packages=find_packages("."),
    package_dir={'kwikapi_tornado': 'tornado'},
    include_package_data=True,
    license='MIT License',  # example license
    description='Quickest way to build powerful HTTP APIs in Python',
    url='https://github.com/deep-compute/kwikapi.tornado',
    download_url="https://github.com/deep-compute/kwikapi.tornado/tarball/%s" % version,
    author='Deep Compute, LLC',
    author_email='contact@deepcompute.com',
    install_requires=[
    'tornado',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
