import os
from setuptools import setup

if __name__ == "__main__":
    setup(
        name="vaisdemo",
        author='VAIS',
        packages=['vaisdemo'],
        package_data={'': ['data']},
        author_email='support@vais.vn',
        url='https://vais.vn',
        include_package_data=True,
        install_requires=["grpcio==1.4.0", "pyyaml", "future"],
        version="0.1.0",
        python_requires='>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    )
