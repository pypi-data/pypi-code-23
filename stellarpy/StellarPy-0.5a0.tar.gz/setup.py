from setuptools import setup, find_packages
from os.path import join, dirname
import stellarpy

setup(
    name='StellarPy',
    version=stellarpy.__version__,
    description='Python Planetary System',
    author='Ruslan Vasilevskiy',
    author_email='vasilevskiy.r@gmail.com',
    license='BSD',
    platforms='any',
    url='https://github.com/ezinall/SolPy',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    install_requires=['numpy>=1.13.3', 'pyqtgraph>=0.10.0'],
    python_requires='==3, >=3.4',
    keywords=['space', 'plot', 'science'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
