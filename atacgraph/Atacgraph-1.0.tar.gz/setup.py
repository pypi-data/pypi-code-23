import setuptools
from distutils.core import setup

setup(
    name = 'Atacgraph',
    packages = ['script'],
    scripts = ['atac_graph.py'],
    version = '1.0',
    description = 'ATAC-seq pipeline',
    author = 'TimLiu',
    author_email = 't810308@gmail.com',
    url = 'https://github.com/kullatnunu/atacgraph',
    download_url = 'https://github.com/kullatnunu/atacgraph.git',
    keywords = ['atac-seq, histograme, heatmap'],
    classifiers = [],
)