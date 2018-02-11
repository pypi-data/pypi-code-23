from setuptools import setup, find_packages


with open('README.rst') as f:
    long_description = f.read()


setup(
    name='vscodex',
    description='VSCode Extension Manager',
    long_description=long_description,
    url='https://github.com/cauebs/vscodex',
    version='0.1.3-1',

    author='Cauê Baasch de Souza',
    author_email='cauebs@protonmail.com',
    license='MIT',

    install_requires=['docopt', 'requests', 'bs4', 'semver', 'tqdm'],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'codex = vscodex.__main__:main',
        ],
    },

    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
