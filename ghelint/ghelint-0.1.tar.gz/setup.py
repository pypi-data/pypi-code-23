from setuptools import setup

setup(
    name='ghelint',
    version='0.1',
    description='ghelint',
    packages=['ghelint'],
    license='MIT',
    entry_points={  # Optional
        'console_scripts': [
            'ghelint=ghelint:main',
        ],
    }
)
