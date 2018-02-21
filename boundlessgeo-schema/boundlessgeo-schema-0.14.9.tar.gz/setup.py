from setuptools import setup, find_packages

with open('boundlessgeo_schema/README.rst', 'r') as inp:
    LONG_DESCRIPTION = inp.read()


setup(
    name='boundlessgeo-schema',
    description='schema for boundlessgeo actions',
    version=__import__('boundlessgeo_schema').get_version(),
    author='Boundless Spatial',
    author_email='contact@boundlessgeo.com',
    url='https://github.com/boundlessgeo/schema',
    long_description=LONG_DESCRIPTION,
    license='Public Domain',
    keywords=['schema', 'json', 'dict'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
        classifiers=[
        'Topic :: Utilities',
        'Intended Audience :: System Administrators',
        'Environment :: Web Environment',
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 3 - Alpha',
        'Operating System :: Other OS',
    ],
    install_requires=[
        'protobuf==3.3.0',
    ]
)
