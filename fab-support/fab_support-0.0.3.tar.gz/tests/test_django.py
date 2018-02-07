import unittest
from fabfile import clean_test
from fabric.api import local

from fab_support import set_stages, copy_null, copy_file
from fabfile import remove_tree


class TestBasicFabSupport(unittest.TestCase):

    def setUp(self):
        local('django-admin startproject test_django')

    def tearDown(self):
        remove_tree(('test_django',))

    def test_set_stages(self):
        # Can you call it
        # Definition of different environments to deploy to
        set_stages(globals(), {
            'testhost': {
                'comment': 'stage: Local build and serving from output directory',
                'config_file': 'local_conf.py',
                'destination': '',
                'copy_method': copy_null,
                'SITEURL': 'http://localhost:8000',
                'PORT': 8000,
            },
        })

