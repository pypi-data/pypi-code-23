from setuptools import setup, find_packages
import versioneer


long_description = """
Documentation: `<http://altdphi.readthedocs.io>`__
"""

setup(
    name='altdphi',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='A library for calculating alternative variables for background rejection in new physics searches with missing transverse momentum at a hadron collider',
    long_description=long_description,
    description_content_type='text/markdown',
    author='Tai Sakuma',
    author_email='tai.sakuma@gmail.com',
    url='http://altdphi.readthedocs.io',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['docs', 'tests']),
)
