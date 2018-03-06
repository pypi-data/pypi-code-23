from setuptools import setup, find_packages

setup(
    python_requires='<3.0.*',
    name='red-pandas',
    version='0.6',
    py_modules=['red_pandas'],
    description='A random test lib',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        red-pandas=red_pandas:print_message
    ''',
)
