from setuptools import setup


requires = ["django-allauth>=0.30.0"]


setup(
    name='django-allauth-hatena',
    version='0.1.2',
    description='Allauth provider for hatena OAuth',
    url='https://github.com/h3poteto/django-allauth-hatena',
    author='h3poteto',
    author_email='h3.poteto@gmail.com',
    license='MIT',
    keywords='allauth hatena',
    packages=[
        "allauth_hatena",
    ],
    install_requires=requires,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
