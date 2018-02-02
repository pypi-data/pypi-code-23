from distutils.core import setup


setup( name = "stringcoercion",
       url = "https://bitbucket.org/mjr129/stringcoercion",
       version = "0.0.0.16",
       description = "An extendable class that converts strings to object types.",
       author = "Martin Rusilowicz",
       license = "https://www.gnu.org/licenses/agpl-3.0.html",
       packages = ["stringcoercion"],
       install_requires = ["mhelper",
                           "py-flags", ],
       python_requires = ">=3.6"
       )
