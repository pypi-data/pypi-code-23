import setuptools

setuptools.setup(
    name="dff_calc",
    version="0.1.0",
    url="https://github.com/PBLab/dFF-calc.git",

    author="Hagai Har-Gil",
    author_email="hagaihargil@protonmail.com",

    description="Simple dF/F calculation for neural calcium traces",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=['numpy', 'pandas', 'attrs'],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
