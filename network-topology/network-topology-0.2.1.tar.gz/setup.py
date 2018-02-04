from setuptools import setup

setup(name='network-topology',
      version='0.2.1',
      description='Simplify overlapping lines into a single graph',
      url='http://github.com/TriTAG/network-topology',
      author='Mike Boos',
      author_email='mike.boos@tritag.ca',
      license='BSD',
      packages=['network_topology'],
      install_requires=[
          'shapely', 'triangle', 'networkx', 'numpy', 'rtree', 'logging'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
