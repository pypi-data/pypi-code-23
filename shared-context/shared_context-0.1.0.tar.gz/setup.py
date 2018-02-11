from setuptools import setup, find_packages

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='shared_context',
    version='0.1.0',
    description='Shared tests between unittest TestCases',
    url='https://github.com/younata/python_shared_context',
    author='Rachel Brindle',
    classifiers=[
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='unittest describe behaves like shared context',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'venv', '.tox']),
)