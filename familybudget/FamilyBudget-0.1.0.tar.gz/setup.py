
from distutils.core import setup

setup(
    # Application name:
    name="FamilyBudget",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Mykyta Danylov",
    author_email="nikita.v.danilov@gmail.com",

    # Packages
    packages=["app"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="http://pypi.python.org/pypi/FamilyBudget_v010/",

    #
    # license="LICENSE.txt",
    description="This simple app allows you to calculate family budget easily. You have 2 options: Incomes for registering your incoming money and Expenses for your spending. The main app's attraction is Archive, where all comments on each money input is saved. Now you can easily see what each penny was spent for!",
    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
    ],
)
