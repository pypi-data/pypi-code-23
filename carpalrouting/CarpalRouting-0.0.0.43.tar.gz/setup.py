from setuptools import setup, find_packages

setup(
    name='CarpalRouting',
    keywords=['routing optimization', 'last mile'],
    description='A routing optimization engine.',
    py_modules=['manage'],
    install_requires=['ortools', 'pandas', 'requests', 'coverage', 'shapely', 'xlrd', 'Click', 'openpyxl'],
    entry_points='''
        [console_scripts]
        routing=manage:cli
    ''',
    license='Apache License 2.0',
    version='0.0.0.43',
    author='CarPal Fleet',
    author_email='nick@carpal.me',
    packages=find_packages(),
    platforms='any',
)