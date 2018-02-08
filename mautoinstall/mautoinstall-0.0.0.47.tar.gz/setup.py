from distutils.core import setup


setup( name = "mautoinstall",
       url = "https://bitbucket.org/mjr129/mautoinstall",
       version = "0.0.0.47",
       description = "Install helper for my apps with a friendlyish command-line UI.",
       author = "Martin Rusilowicz",
       license = "https://www.gnu.org/licenses/agpl-3.0.html",
       packages = ["mautoinstall"],
       entry_points = { "console_scripts": ["mautoinstall = mautoinstall.__main__:main"] },
       python_requires = ">=3.6",
       install_requires = ["typing"]
       )
