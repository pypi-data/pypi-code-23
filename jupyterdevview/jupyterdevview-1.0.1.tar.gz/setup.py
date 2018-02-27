from distutils.core import setup

setup(
    name='jupyterdevview',
    version='1.0.1',
    author='Nick Tiligadas',
    author_email='nick@tiligadas.net',
    py_modules=['jupyterdevview'],
    scripts=[],
    url='http://pypi.python.org/pypi/jupyterdevview/',
    license='LICENSE.txt',
    description='Side by side view of code and output in jupyter notebooks',
    long_description=open('README.txt').read(),  
    data_files=[('share/jupyterdevview',['css/custom.css.dev','css/custom.css.notebook'])],
    install_requires=['pathlib2']
)
