from setuptools import find_packages, setup

setup(
    name='infcli',
    version='1.0.0',
    description='Infinity Python Driver',
    url='https://github.com/infamily/infinity-driver',
    author='Mindey',
    author_email='mindey@qq.com',
    license='UNLICENSE',
    packages = find_packages(exclude=['docs', 'tests*']),
    install_requires=["slumber", "mock", "schematics"],
    extras_require = {
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    zip_safe=False
)
