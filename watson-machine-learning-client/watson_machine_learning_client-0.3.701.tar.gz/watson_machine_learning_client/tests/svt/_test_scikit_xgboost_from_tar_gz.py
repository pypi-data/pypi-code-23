import unittest
import os
from xgboost.sklearn import XGBClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_svmlight_file
from configparser import ConfigParser
from watson_machine_learning_client.log_util import get_logger
import json
from importlib import reload
import site
from preparation_and_cleaning import *
from watson_machine_learning_client.utils import SCIKIT_LEARN_FRAMEWORK


class TestWMLClientWithXGBoost(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    scoring_url = None
    logger = get_logger(__name__)

    @classmethod
    def setUpClass(self):
        TestWMLClientWithXGBoost.logger.info("Service Instance: setting up credentials")
        # reload(site)

        self.wml_credentials = get_wml_credentials()
        self.client = get_client()
        self.model_path = os.path.join(os.getcwd(), 'artifacts', 'scikit_xgboost_model.tar.gz')

    def test_1_service_instance_details(self):
        TestWMLClientWithXGBoost.logger.info("Check client ...")
        self.assertTrue(type(self.client).__name__ == 'WatsonMachineLearningAPIClient')

        TestWMLClientWithXGBoost.logger.info("Getting instance details ...")
        details = self.client.service_instance.get_details()

        TestWMLClientWithXGBoost.logger.debug(details)
        self.assertTrue("published_models" in str(details))
        self.assertEqual(type(details), dict)

    def test_2_publish_model(self):
        TestWMLClientWithXGBoost.logger.info("Publishing scikit-xgboost model ...")

        self.client.repository.ModelMetaNames.show()

        model_props = {self.client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
                       self.client.repository.ModelMetaNames.AUTHOR_EMAIL: "ibm@ibm.com",
                       self.client.repository.ModelMetaNames.NAME: "LOCALLY created agaricus prediction model",
                       self.client.repository.ModelMetaNames.FRAMEWORK_NAME: SCIKIT_LEARN_FRAMEWORK,
                       self.client.repository.ModelMetaNames.FRAMEWORK_VERSION: "0.17",
                       }
        published_model = self.client.repository.store_model(model=self.model_path, meta_props=model_props)
        TestWMLClientWithXGBoost.model_uid = self.client.repository.get_model_uid(published_model)
        TestWMLClientWithXGBoost.logger.info("Published model ID:" + str(TestWMLClientWithXGBoost.model_uid))
        self.assertIsNotNone(TestWMLClientWithXGBoost.model_uid)

    def test_3_publish_model_details(self):
        TestWMLClientWithXGBoost.logger.info("Get published model details ...")
        details = self.client.repository.get_details(self.model_uid)

        TestWMLClientWithXGBoost.logger.debug("Model details: " + str(details))
        self.assertTrue("LOCALLY created agaricus prediction model" in str(details))

    def test_4_create_deployment(self):
        TestWMLClientWithXGBoost.logger.info("Create deployment ...")
        global deployment
        deployment = self.client.deployments.create(model_uid=self.model_uid, name="Test deployment", asynchronous=False)

        TestWMLClientWithXGBoost.logger.info("model_uid: " + self.model_uid)
        TestWMLClientWithXGBoost.logger.info("Online deployment: " + str(deployment))
        TestWMLClientWithXGBoost.scoring_url = self.client.deployments.get_scoring_url(deployment)
        self.assertTrue("online" in str(deployment))

    def test_5_get_deployment_details(self):
        TestWMLClientWithXGBoost.logger.info("Get deployment details ...")
        deployment_details = self.client.deployments.get_details()
        self.assertTrue("Test deployment" in str(deployment_details))

        TestWMLClientWithXGBoost.logger.debug("Online deployment: " + str(deployment_details))
        TestWMLClientWithXGBoost.deployment_uid = self.client.deployments.get_uid(deployment)
        self.assertIsNotNone(TestWMLClientWithXGBoost.deployment_uid)

    def test_6_score(self):
        TestWMLClientWithXGBoost.logger.info("Online model scoring ...")
        (X, _) = load_svmlight_file(os.path.join('artifacts', 'agaricus.txt.test'))
        scoring_data = {'values': [list(X.toarray()[0, :])]}
        TestWMLClientWithXGBoost.logger.debug("Scoring data: {}".format(scoring_data))
        predictions = self.client.deployments.score(TestWMLClientWithXGBoost.scoring_url, scoring_data)

        TestWMLClientWithXGBoost.logger.debug("Prediction: " + str(predictions))
        self.assertTrue(("prediction" in str(predictions)) and ("probability" in str(predictions)))

    def test_7_delete_deployment(self):
        TestWMLClientWithXGBoost.logger.info("Delete model deployment ...")
        self.client.deployments.delete(TestWMLClientWithXGBoost.deployment_uid)

    def test_8_delete_model(self):
        TestWMLClientWithXGBoost.logger.info("Delete model ...")
        self.client.repository.delete(TestWMLClientWithXGBoost.model_uid)

if __name__ == '__main__':
    unittest.main()
