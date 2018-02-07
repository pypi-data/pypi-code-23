from distutils.core import setup

setup(
    name = "vakuum",
    version = "1.1",
    py_modules = ["vakuum"],
    author = "WSH",
    author_email = "shihang.wang0226@gamil.com",
    description = "install the needed packages",
    install_requires = [
       'matplotlib>=2.1.1',
       'numpy>=1.14.0',
       'pandas>=0.21.0',
       'PyQt5>=5.8.1',
       'scipy>=1.0.0',
       'pyserial>=3.4',
	],
    python_requires='>=3',
    )   
