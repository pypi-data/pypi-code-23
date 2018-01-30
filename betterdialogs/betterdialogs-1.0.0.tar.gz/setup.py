from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='betterdialogs',
    version='1.0.0',
    description='Simple boilerplate library for tkinter GUIs (Python 3 ONLY)',
    long_description=readme(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities'
    ],
    url='https://github.com/morngrar/betterdialogs',
    author='Svein-Kåre Bjørnsen',
    author_email='sveinkare@gmail.com',
    license='GPL',
    include_package_data = True,
    packages=find_packages(),
    install_requires=[
        "Pillow>=5.0.0"
    ],
    scripts=[]
)
