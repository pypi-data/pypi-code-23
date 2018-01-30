from setuptools import setup

setup(
    name='biostream-schemas',
    version='0.0.1',
    scripts=[
        'bmeg/clinical_pb2.py',
        'bmeg/cna_pb2.py',
        'bmeg/genome_pb2.py',
        'bmeg/phenotype_pb2.py',
        'bmeg/rna_pb2.py',
        'bmeg/variants_pb2.py'
    ]
)
