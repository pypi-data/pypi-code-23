import unittest
import os
from watson_machine_learning_client.log_util import get_logger
import json
from watson_machine_learning_client.wml_client_error import WMLClientError
from preparation_and_cleaning import *
from watson_machine_learning_client.utils import PMML_FRAMEWORK


class TestWMLClientWithPMML(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    scoring_url = None
    logger = get_logger(__name__)

    @classmethod
    def setUpClass(self):
        TestWMLClientWithPMML.logger.info("Service Instance: setting up credentials")
        self.wml_credentials = get_wml_credentials()
        self.client = get_client()
        self.model_path = os.path.join(os.getcwd(), 'artifacts', 'iris_chaid.xml')

    def test_01_service_instance_details(self):
        TestWMLClientWithPMML.logger.info("Check client ...")
        self.assertTrue(type(self.client).__name__ == 'WatsonMachineLearningAPIClient')

        self.logger.info("Getting instance details ...")
        details = self.client.service_instance.get_details()
        TestWMLClientWithPMML.logger.debug(details)

        self.assertTrue("published_models" in str(details))
        self.assertEqual(type(details), dict)

    def test_02_publish_model(self):

        self.logger.info("Publishing PMML model ...")

        self.client.repository.ModelMetaNames.show()

        model_props = {self.client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
                       self.client.repository.ModelMetaNames.AUTHOR_EMAIL: "ibm@ibm.com",
                       self.client.repository.ModelMetaNames.NAME: "LOCALLY created iris prediction model",
                       self.client.repository.ModelMetaNames.FRAMEWORK_NAME: PMML_FRAMEWORK,
                       self.client.repository.ModelMetaNames.FRAMEWORK_VERSION: "4.2"
                       }
        published_model_details = self.client.repository.store_model(model=self.model_path, meta_props=model_props)
        TestWMLClientWithPMML.model_uid = self.client.repository.get_model_uid(published_model_details)
        TestWMLClientWithPMML.model_url = self.client.repository.get_model_url(published_model_details)
        self.logger.info("Published model ID:" + str(TestWMLClientWithPMML.model_uid))
        self.logger.info("Published model URL:" + str(TestWMLClientWithPMML.model_url))
        self.assertIsNotNone(TestWMLClientWithPMML.model_uid)
        self.assertIsNotNone(TestWMLClientWithPMML.model_url)

    def test_03_download_model(self):
        try:
            os.remove('download_test_url')
        except OSError:
            pass

        self.client.repository.download(TestWMLClientWithPMML.model_uid, filename='download_test_url')
        self.assertRaises(WMLClientError, self.client.repository.download, TestWMLClientWithPMML.model_uid, filename='download_test_url')

    def test_04_publish_model_details(self):
        details = self.client.repository.get_details(self.model_uid)
        TestWMLClientWithPMML.logger.debug("Model details: " + str(details))
        self.assertTrue("LOCALLY created iris prediction model" in str(details))

        details_all = self.client.repository.get_details()
        TestWMLClientWithPMML.logger.debug("All artifacts details: " + str(details_all))
        self.assertTrue("LOCALLY created iris prediction model" in str(details_all))

        details_models = self.client.repository.get_model_details()
        TestWMLClientWithPMML.logger.debug("All models details: " + str(details_models))
        self.assertTrue("LOCALLY created iris prediction model" in str(details_models))

    def test_05_create_deployment(self):
        deployment = self.client.deployments.create(model_uid=self.model_uid, name="Test deployment")
        TestWMLClientWithPMML.logger.info("model_uid: " + self.model_uid)
        TestWMLClientWithPMML.logger.info("Online deployment: " + str(deployment))
        self.assertTrue(deployment is not None)
        TestWMLClientWithPMML.scoring_url = self.client.deployments.get_scoring_url(deployment)
        TestWMLClientWithPMML.deployment_uid = self.client.deployments.get_uid(deployment)
        self.assertTrue("online" in str(deployment))

    def test_06_get_deployment_details(self):
        deployment_details = self.client.deployments.get_details()
        self.assertTrue("Test deployment" in str(deployment_details))

    def test_07_get_deployment_details_using_uid(self):
        deployment_details = self.client.deployments.get_details(TestWMLClientWithPMML.deployment_uid)
        self.assertIsNotNone(deployment_details)

    def test_08_score(self):
        scoring_data = {'fields': ['Sepal.Length', 'Sepal.Width', 'Petal.Length', 'Petal.Width'], 'values': [[5.1, 3.5, 1.4, 0.2]]}
        predictions = self.client.deployments.score(TestWMLClientWithPMML.scoring_url, scoring_data)
        predictions_fields = len(predictions['fields'])
        predictions_values = len([x for x in predictions['values'] if x])
        self.assertTrue(predictions_fields>0 and predictions_values>0)

    def test_09_delete_deployment(self):
        self.client.deployments.delete(TestWMLClientWithPMML.deployment_uid)

    def test_10_delete_model(self):
        self.client.repository.delete(TestWMLClientWithPMML.model_uid)

if __name__ == '__main__':
    unittest.main()
