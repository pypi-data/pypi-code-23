from setuptools import setup


setup(
    name='gin165',
    version='0.0.8',
    description='Command line utility for my personal needs.',
    py_modules=['gin'],
    install_requires=[
        'Click',
        'Pillow',
        'svglib',
        'twine',
    ],
    entry_points={
        'console_scripts': [
            'gin=gin:gin',
        ]
    },
    python_requires='~=3.6',
)
