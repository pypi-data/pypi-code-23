from setuptools import setup, find_packages

setup(
    name='Cessa',
    version='1.2.5rc1',
    description='A Docker security reinforcement system based on system call interception',
    # long_description=long_description,
    url='https://github.com/ihac/cessa',
    author='Xiao An',
    author_email='hac@zju.edu.cn',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=['Docker container', 'security'],
    packages=find_packages(exclude=['tests']),
    package_data={
        '': ['*.fbc', '*.qbc'],
    },
    data_files=[('configs', ['configs/clabel.list', 'configs/systable.list', 'configs/sysdig.json'])],
    scripts=['client/cessa'],
)
