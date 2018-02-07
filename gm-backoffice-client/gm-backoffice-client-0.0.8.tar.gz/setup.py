from setuptools import find_packages, setup

setup(
    name='gm-backoffice-client',
    version='0.0.8',
    description="Client for mtrl.ai orders API",
    keywords=[],
    url="https://github.com/gdml/backoffice-client/",
    author="Fedor Borshev",
    author_email="f@f213.in",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        'requests',
        'jsonschema',
    ],
    include_package_data=True,
    zip_safe=False,
)
