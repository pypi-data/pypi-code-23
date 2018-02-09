from setuptools import setup

setup(
    name='eightball',
    version='0.0.1',
    description='train, evaluate, predict',
    author='Adam Hajari',
    author_email='adamhajari@gmail.com',
    packages=['eightball'],
    zip_safe=False,
    install_requires=[
        "scikit-learn>=0.19.1",

        # These must be fixed at these versions; see README
        "pandas>=0.22.0",
        "numpy>=1.14.0",
        "matplotlib>=2.1.2"
    ],
    test_suite='nose.collector',
    tests_require=['nose']
)
