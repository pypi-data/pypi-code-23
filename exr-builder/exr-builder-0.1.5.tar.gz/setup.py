from setuptools import setup
import exr.meta_builder
setup(
    name="exr-builder",
    version=exr.meta_builder.__version__,
    author="Peter Salnikov",
    author_email="opensource@exrny.com",
    url=exr.meta_builder.__website__,
    packages=["exr", "exr.builder"],
    entry_points={'console_scripts': ['exrb=exr.builder:main']},
    install_requires=['sh'],
    license="MIT License",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Build Tools'
    ],
    keywords=['devops', 'build tool'],
    description="Lightweight Python Build Tool.",
    long_description=open("README.rst").read()+"\n"+open("CHANGES.rst").read()
)
