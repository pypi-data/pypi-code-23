import os, time
from setuptools import setup, find_packages

lt = time.localtime()
version = (lt.tm_year, (10 + lt.tm_mon) * 100 + lt.tm_mday, (10 + lt.tm_hour) * 100 + lt.tm_min)
versionString = '.'.join(map(str, version))

# Clean up old binaries for twine upload
#if os.path.exists("dist"):
#  rmFiles = list(sorted(os.listdir("dist")))
#  print(repr(rmFiles))
#  for file in (f for f in rmFiles[:-1] if any([f.endswith(ext) for ext in (".tar.gz", "zip")])):
#    print("Removing old sdist archive %s" % file)
#    try: os.unlink(os.path.join("dist", file))
#    except: print("Cannot remove old distribution file " + file)

setup(
  name = 'termwidth',
  version = versionString,
  description = "Terminal width detection library",
  long_description = "",
  classifiers = [c.strip() for c in """
        Development Status :: 5 - Production/Stable
        Intended Audience :: Developers
        License :: OSI Approved :: GNU General Public License v3 (GPLv3)
        Operating System :: OS Independent
        Programming Language :: Python
        Programming Language :: Python :: 3
        Programming Language :: Python :: 3 :: Only
        """.split('\n') if c.strip()],  # https://pypi.python.org/pypi?:action=list_classifiers
  keywords = 'terminal width size posix curses tput linux windows',
  author = 'Arne Bachmann',
  author_email = 'ArneBachmann@users.noreply.github.com',
  maintainer = 'Arne Bachmann',
  maintainer_email = 'ArneBachmann@users.noreply.github.com',
  url = 'http://github.com/ArneBachmann/termwidth',
  license = 'GNU General Public License v3 (GPLv3)',
  packages = [""],
  zip_safe = False
)
