from setuptools import setup

fname = 'README.rst'

try:
    import pypandoc
    pypandoc.convert('README.md', 'rst', outputfile=fname)
except ImportError:
    print('WARNING: Package being build without ReST documentation. Please install pypandoc.')

try:
    with open(fname) as fp:
        readme = fp.read()
except:
      readme = None

setup(name='sermonaudio',
      version='0.2.2',
      description='The official Python client library for accessing the SermonAudio.com APIs',
      long_description=readme,
      classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.6',
      ],
      url='http://api.sermonaudio.com/',
      author='SermonAudio.com',
      author_email='info@sermonaudio.com',
      keywords='sermon audio sermonaudio API preaching church bible',
      license='MIT',
      packages=['sermonaudio', 'sermonaudio.node', 'sermonaudio.broadcaster'],
      install_requires=[
            'requests>=2.18.4',
            'pytz>=2017.3',
            'python-dateutil'
      ])
