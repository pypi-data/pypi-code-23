from distutils.core import setup


setup( name = "csveditor",
       url = "https://bitbucket.org/mjr129/csveditor",
       version = "0.0.0.10",
       description = "Edit CSV files from the command line.",
       author = "Martin Rusilowicz",
       license = "https://www.gnu.org/licenses/agpl-3.0.html",
       packages = ["csveditor",
                   "csveditor.extensions"],
       entry_points = { "console_scripts": ["csveditor = csveditor.__main__:main"] },
       python_requires = ">=3.6",
       install_requires = ["pyparsing", 'colorama', 'intermake', 'mhelper']
       )
