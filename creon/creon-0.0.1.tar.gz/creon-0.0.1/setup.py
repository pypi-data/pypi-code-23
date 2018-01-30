from setuptools import setup

extras_require = {}
install_requires = [
    'pypiwin32 >= 220, < 230',
]
setup_requires = []


setup(
    name='creon',
    version='0.0.1',
    description='DASHIN Securities Creon Client',
    url='https://github.com/AMIN-Partners/creon',
    author='Ayun Park',
    py_modules=['creon'],
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
    ]
)