"""Testing utilities"""
from skills_utils.job_posting_import import JobPostingImportBase

import unittest

MANDATORY_FIELDS = [
    'title',
    'description',
    'datePosted',
    'validThrough',
    'jobLocation',
]


class SampleImporter(JobPostingImportBase):
    """A basic importer that can be run through the ImporterTest"""
    def _iter_postings(self, quarter):
        pass

    def _transform(self, document):
        transformed = {field: '' for field in MANDATORY_FIELDS}
        transformed['@context'] = "http://schema.org"
        transformed['@type'] = 'JobPosting'
        return transformed


class ImporterTest(unittest.TestCase):
    """Common superclass for all partner ETL tests"""
    importer_class = SampleImporter
    sample_input_document = {}

    def test_schema_org(self):
        """Make basic assertions about common schema"""

        assert hasattr(self, 'sample_input_document')
        importer = self.importer_class(partner_id='xx')
        transformed = importer._transform(self.sample_input_document)
        assert transformed['@context'] == 'http://schema.org'
        assert transformed['@type'] == 'JobPosting'
        for field in MANDATORY_FIELDS:
            assert field in transformed
