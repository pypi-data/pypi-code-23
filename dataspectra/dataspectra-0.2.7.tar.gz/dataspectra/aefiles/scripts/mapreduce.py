#!/usr/bin/env python2.7

import cgi
import webapp2
import logging
import os, csv
import StringIO
from google.appengine.api import app_identity
from mapreduce import base_handler
from mapreduce import mapreduce_pipeline
from mapreduce import operation as op
from mapreduce.input_readers import InputReader


esr
import web_module_to_load as WMTL

def testmapperFunc(newRequest):
    f = StringIO.StringIO(newRequest)
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        newEntry = DataStoreModel(attr1=row[0], link=row[1])
        yield op.db.Put(newEntry)

class TestGCSReaderPipeline(base_handler.PipelineBase):
    def run(self, filename):
        yield mapreduce_pipeline.MapreducePipeline(
                "test_gcs",
                "testgcs.testmapperFunc",
                "mapreduce.input_readers.FileInputReader",
                mapper_params={
                    "files": [filename],
                    "format": 'lines'
                },
                shards=1)

class tempTestRequestGCSUpload(webapp2.RequestHandler):
    def get(self):
        bucket_name = os.environ.get('BUCKET_NAME',
                                     app_identity.get_default_gcs_bucket_name())

        bucket = '/gs/' + bucket_name
        filename = bucket + '/' + 'tempfile.csv'

        pipeline = TestGCSReaderPipeline(filename)
        pipeline.with_params(target="mapreducetestmodtest")
        pipeline.start()
        self.response.out.write('done')

