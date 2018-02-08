from distutils.core import setup


setup( name = "mhelper",
       url = "https://bitbucket.org/mjr129/mhelper",
       version = "1.0.1.42",
       description = "Includes a collection of utility functions.",
       author = "Martin Rusilowicz",
       license = "https://www.gnu.org/licenses/agpl-3.0.html",
       packages = ["mhelper",
                   "mhelper_qt",
                   "mdbg"],
       python_requires = ">=3.6",
       install_requires = ["PyQt5",
                           "py-flags",
                           "jsonpickle"]
       )
