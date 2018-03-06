try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os

packageName = "pyresid"
packageDir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          packageName)

__version__ = "0.1.4"

setup(# package information
      name=packageName,
      version=__version__,
      author="Rob Firth",
      author_email="robert.firth@stfc.ac.uk",
      url="",
      description="Python tools for mining Protein Residuals from Fulltext articles using PMC number, ePMC and PDB",
      long_description='''Python tools for mining Protein Residuals from Fulltext articles using PMC number, ePMC and PDB.
  
           Copyright [2018] [STFC]

           Licensed under the Apache License, Version 2.0 (the "License");
           you may not use this file except in compliance with the License.
           You may obtain a copy of the License at
        
               http://www.apache.org/licenses/LICENSE-2.0
        
           Unless required by applicable law or agreed to in writing, software
           distributed under the License is distributed on an "AS IS" BASIS,
           WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
           See the License for the specific language governing permissions and
           limitations under the License.''',

      packages=[packageName,],
      package_dir={packageName: packageName},
      package_data={packageName:['mmCIF/*']},
      install_requires=["bs4", "scipy", "numpy", "matplotlib", "spacy", "lxml", "biopython", "pycifrw"]#,
    )
