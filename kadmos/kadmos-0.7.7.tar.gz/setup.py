from setuptools import setup, find_packages


version = '0.7.7'


def readme():
    with open('readme.md') as f:
        return f.read()


setup(name='kadmos',
      version=version,
      description='Knowledge- and graph-based Agile Design with Multidisciplinary Optimization System',
      long_description=readme(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
      ],
      keywords='optimization agile multidisciplinary graph engineering',
      url='https://bitbucket.org/imcovangent/kadmos',
      download_url='https://bitbucket.org/imcovangent/kadmos/raw/master/dist/'+version+'.tar.gzip',
      author='Imco van Gent',
      author_email='i.vangent@tudelft.nl',
      license='Apache Software License',
      packages=find_packages(),
      install_requires=[
            'metis>=0.2a3',
            'lxml',
            'tabulate',
            'flask',
            'matplotlib',
            'matlab',
            'networkx>=2.0',
            'numpy',
            'progressbar2'
      ],
      include_package_data=True,
      zip_safe=False)
