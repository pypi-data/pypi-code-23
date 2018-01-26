from setuptools import setup

setup(name="pysubmit",
      version="0.1",
      description="Versatile computation submission tool",
      url="https://bitbucket.org/Mc_M/pysubmit",
      author="Martin Lellep",
      author_email="martin.lellep@physik.uni-marburg.de",
      license="MIT",
      packages=["pysubmit"],
      install_requires=[
          "jinja2",
      ],
      entry_points = {
        "console_scripts": ['pysubmit=pysubmit.command_line:main'],
      },
      zip_safe=False)
