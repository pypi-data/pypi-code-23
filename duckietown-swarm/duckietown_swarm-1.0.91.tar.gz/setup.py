from setuptools import find_packages, setup


def get_version(filename):
    import ast
    version = None
    with open(filename) as f:
        for line in f:
            if line.startswith('__version__'):
                version = ast.parse(line).body[0].value.s
                break
        else:
            raise ValueError('No version found in %r.' % filename)
    if version is None:
        raise ValueError(filename)
    return version


version = get_version(filename='src/duckietown_swarm/__init__.py')

name = 'duckietown_swarm'

setup(name=name,
      url='http://github.com/duckietown/duckietown_swarm',
      maintainer="Andrea Censi",
      maintainer_email="andrea@duckietown.org",
      description='',
      long_description='',
      #package_data={'':['*.*', '*.mcdp*', '*.js', '*.png', '*.css']},

      # without this, the stuff is included but not installed
      include_package_data=True,
      keywords="Optimization",
      license="GPLv2",
      classifiers=[
        'Development Status :: 4 - Beta',
      ],
      version=version,

      download_url=
        'http://github.com/duckietown/duckietown_swarm/tarball/%s' % version,

      package_dir={'':'src'},
      packages=find_packages('src'),
      install_requires=[
        #'ConfTools>=1.0,<2',
        # '#quickapp',
        # 'reprep',
        'irc',
        'SystemCmd',
        'ConfTools',
        'termcolor',
        'ruamel.yaml',
        'ruamel.ordereddict',
        'base58',
        'netifaces',
        'multiaddr',
        'subprocess32',
        'setproctitle',
      ],
      # This avoids creating the egg file, which is a zip file, which makes our data
      # inaccessible by dir_from_package_name()
      zip_safe=False,
      dependency_links=[
      ],

      tests_require=[
#        'nose>=1.1.2,<2',
#        'comptests',
      ],

      entry_points={

         'console_scripts': [
            'dt-swarm = duckietown_swarm:duckietown_swarm_cli_main',
            'dt-swarm-watcher = duckietown_swarm:duckietown_swarm_watcher_main',
        ]
      }
)
