################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################
import re

TOKEN_ENDPOINT_HREF_PATTERN = '{}/v3/identity/token'
EXPERIMENTS_HREF_PATTERN = '{}/v3/experiments'
EXPERIMENT_HREF_PATTERN = '{}/v3/experiments/{}'
EXPERIMENT_RUNS_HREF_PATTERN = '{}/v3/experiments/{}/runs'
EXPERIMENT_RUN_HREF_PATTERN = '{}/v3/experiments/{}/runs/{}'
PUBLISHED_MODELS_HREF_PATTERN = '{}/v3/wml_instances/{}/published_models'
DEPLOYMENTS_HREF_PATTERN = '{}/v3/wml_instances/{}/deployments'
DEPLOYMENT_HREF_PATTERN = '{}/v3/wml_instances/{}/published_models/{}/deployments/{}'
MODEL_LAST_VERSION_HREF_PATTERN = '{}/v3/ml_assets/models/{}'
DEFINITION_HREF_PATTERN = '{}/v3/ml_assets/training_definitions/{}'


def is_url(s):
    res = re.match('https?:\/\/.+', s)
    return res is not None


def is_uid(s):
    res = re.match('[a-z0-9\-]{36}', s)
    return res is not None


class HrefDefinitions:
    def __init__(self, wml_credentials):
        self._wml_credentials = wml_credentials

    def get_token_endpoint_href(self):
        return TOKEN_ENDPOINT_HREF_PATTERN.format(self._wml_credentials['url'])

    def get_published_models_href(self):
        return PUBLISHED_MODELS_HREF_PATTERN.format(self._wml_credentials['url'], self._wml_credentials['instance_id'])

    def get_model_last_version_href(self, artifact_uid):
        return MODEL_LAST_VERSION_HREF_PATTERN.format(self._wml_credentials['url'], artifact_uid)

    def get_deployments_href(self):
        return DEPLOYMENTS_HREF_PATTERN.format(self._wml_credentials['url'], self._wml_credentials['instance_id'])

    def get_experiments_href(self):
        return EXPERIMENTS_HREF_PATTERN.format(self._wml_credentials['url'])

    def get_experiment_href(self, experiment_uid):
        return EXPERIMENT_HREF_PATTERN.format(self._wml_credentials['url'], experiment_uid)

    def get_experiment_runs_href(self, experiment_uid):
        return EXPERIMENT_RUNS_HREF_PATTERN.format(self._wml_credentials['url'], experiment_uid)

    def get_experiment_run_href(self, experiment_uid, experiment_run_uid):
        return EXPERIMENT_RUN_HREF_PATTERN.format(self._wml_credentials['url'], experiment_uid, experiment_run_uid)

    def get_deployment_href(self, model_uid, deployment_uid):
        return DEPLOYMENT_HREF_PATTERN.format(self._wml_credentials['url'], self._wml_credentials['instance_id'], model_uid, deployment_uid)

    def get_definition_href(self, definition_uid):
        return DEFINITION_HREF_PATTERN.format(self._wml_credentials['url'], definition_uid)