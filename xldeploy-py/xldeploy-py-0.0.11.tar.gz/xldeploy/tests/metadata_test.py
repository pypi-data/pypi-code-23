from unittest import TestCase
import xldeploy

class MetadataTest(TestCase):

    def setUp(self):
        config = xldeploy.Config()
        client = xldeploy.Client(config)
        self.meta = client.metadata

    def test_list_descriptors(self):
        des_list = self.meta.list_descriptors()
        self.assertTrue(isinstance(des_list, list))
