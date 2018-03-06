from setuptools import setup
import io

setup(
    name='bw2temporalis',
    version="1.0",
    packages=[
        "bw2temporalis",
        "bw2temporalis.tests",
        "bw2temporalis.examples",
        "bw2temporalis.dyn_methods"
    ],
    author="Giuseppe Cardellini, Chris Mutel",
    author_email="giuseppe.cardellini@gmail.com, cmutel@gmail.com",
    license=io.open('LICENSE.txt', encoding='utf-8').read(),
    url="https://bitbucket.org/cardosan/brightway2-temporalis",
    install_requires=[
        "brightway2>=2.1.1",
        "bw2data>=3.0",
        "bw2calc",
        "bw2io>=RC3",
        "bw2speedups>=2.2",
        "numpy>=1.6",
        "scipy",
        "numexpr",
    ],
    description='Provide a dynamic LCA calculations for the Brightway2 life cycle assessment framework',
    long_description=io.open('README.rst', encoding='utf-8').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        #~'Programming Language :: Python :: 2.7', #to be fixed
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)
