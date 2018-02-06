from setuptools import setup, find_packages


def get_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()


setup(
    name='eco-connect',
    version='0.23.4',
    description='Ecorithm\'s eco-connect ',
    long_description='Please see http://eco-connect.readthedocs.io/en/latest/ '
    'for Documentation.',
    license="Proprietary",
    python_requires='>=3.6',
    url='https://github.com/ecorithm/eco_connect_public',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=get_requirements(),
    project_urls={
        "Documentation": "http://eco-connect.readthedocs.io/en/latest/",
        "Source Code": "https://github.com/ecorithm/eco_connect",
    }
)
