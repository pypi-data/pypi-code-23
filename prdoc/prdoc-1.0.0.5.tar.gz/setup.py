from distutils.core import setup


with open( "readme.md", "r" ) as file:
    long_description = file.read()

setup( name = "prdoc",
       url = "https://bitbucket.org/mjr129/prdoc",
       version = "1.0.0.5",
       description = "Print a markdown file to the terminal.",
       long_description = long_description,
       author = "Martin Rusilowicz",
       license = "https://www.gnu.org/licenses/agpl-3.0.html",
       packages = ["prdoc"],
       entry_points = { "console_scripts": ["prdoc = prdoc.__main__:main"] },
       install_requires = ["mhelper"],
       python_requires = ">=3.6"
       )
