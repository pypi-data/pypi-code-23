from setuptools import setup

setup(
    name="djassr",
    version=__import__('djassr').__version__,
    author="Alexandre Varas",
    author_email="alej0varas@gmail.com",
    license='GNU Library or Lesser General Public License (LGPL)',
    description="Django AWS S3 Signed Requests API with Django Rest Framework",
    url='https://github.com/alej0varas/djassr',
    packages=('djassr', ),
    intall_requires=['django', 'djangorestframework', 'boto3'],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    test_suite='runtests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

    ],
)
