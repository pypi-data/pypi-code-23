################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from watson_machine_learning_client.wml_client_error import ApiRequestFailure, WMLClientError
from watson_machine_learning_client.href_definitions import HrefDefinitions
import re
import os

INSTANCE_DETAILS_TYPE = 'instance_details_type'
DEPLOYMENT_DETAILS_TYPE = 'deployment_details_type'
EXPERIMENT_RUN_DETAILS_TYPE = 'experiment_run_details_type'
MODEL_DETAILS_TYPE = 'model_details_type'
DEFINITION_DETAILS_TYPE = 'definition_details_type'
EXPERIMENT_DETAILS_TYPE = 'experiment_details_type'
TRAINING_RUN_DETAILS_TYPE = 'training_run_details_type'

UNKNOWN_ARRAY_TYPE = 'resource_type'
UNKNOWN_TYPE = 'unknown_type'

SPARK_MLLIB = "mllib"
SPSS_FRAMEWORK = "spss-modeler"
TENSORFLOW_FRAMEWORK = "tensorflow"
XGBOOST_FRAMEWORK = "xgboost"
SCIKIT_LEARN_FRAMEWORK = "scikit-learn"
PMML_FRAMEWORK = "pmml"


def get_ml_token(watson_ml_creds):
    import requests
    import json

    if 'ml_token' not in watson_ml_creds:
        response = requests.get(HrefDefinitions(watson_ml_creds).get_token_endpoint_href(), auth=(watson_ml_creds['username'], watson_ml_creds['password']))
        if response.status_code == 200:
            watson_ml_creds['ml_token'] = json.loads(response.text).get('token')
        else:
            raise ApiRequestFailure("Error during getting ML Token.", response)
    return watson_ml_creds['ml_token']


def get_headers(wml_token):
    return {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + wml_token}


def print_text_header_h1(title):
    print('\n\n' + ('#' * len(title)) + '\n')
    print(title)
    print('\n' + ('#' * len(title)) + '\n\n')


def print_text_header_h2(title):
    print('\n\n' + ('-' * len(title)))
    print(title)
    print(('-' * len(title)) + '\n\n')


def get_type_of_details(details):
    if 'resources' in details:
        return UNKNOWN_ARRAY_TYPE
    else:
        try:
            if re.search('\/v3\/wml_instances\/[^\/]+$', details['metadata']['url']) is not None:
                return INSTANCE_DETAILS_TYPE
        except:
            pass

        try:
            if re.search('\/published_models\/[^\/]+/deployments/[^\/]+$', details['metadata']['url']) is not None:
                return DEPLOYMENT_DETAILS_TYPE
        except:
            pass

        try:
            if re.search('\/v3\/experiments\/[^\/]+/runs/[^\/]+$', details['metadata']['url']) is not None:
                return EXPERIMENT_RUN_DETAILS_TYPE
        except:
            pass

        try:
            if re.search('\/published_models\/[^\/]+$', details['metadata']['url']) is not None or re.search('\/v3\/ml_assets\/models\/[^\/]+$', details['entity']['ml_asset_url']) is not None:
                return MODEL_DETAILS_TYPE
        except:
            pass

        try:
            if re.search('\/v3\/ml_assets\/training_definitions\/[^\/]+$', details['metadata']['url']) is not None:
                return DEFINITION_DETAILS_TYPE
        except:
            pass

        try:
            if re.search('\/v3\/experiments\/[^\/]+$', details['metadata']['url']) is not None:
                return EXPERIMENT_DETAILS_TYPE
        except:
            pass

        try:
            if re.search('\/v3\/models\/[^\/]+$', details['metadata']['url']) is not None:
                return TRAINING_RUN_DETAILS_TYPE
        except:
            pass

        return UNKNOWN_TYPE


def pack(directory_path):
    pass


def unpack(filename):
    pass


def load_model_from_directory(framework, directory_path):
    if framework == SPARK_MLLIB:
        from pyspark.ml import PipelineModel
        return PipelineModel.read().load(directory_path)
    elif framework == SPSS_FRAMEWORK:
        pass
    elif framework == TENSORFLOW_FRAMEWORK:
        pass
    elif framework == SCIKIT_LEARN_FRAMEWORK or framework == XGBOOST_FRAMEWORK:
        from sklearn.externals import joblib
        model_id = directory_path[directory_path.rfind('/') + 1:] + ".pkl"
        return joblib.load(os.path.join(directory_path, model_id))
    elif framework == PMML_FRAMEWORK:
        pass
    else:
        raise WMLClientError('Invalid framework specified: \'{}\'.'.format(framework))


# def load_model_from_directory(framework, directory_path):
#     if framework == SPARK_MLLIB:
#         from pyspark.ml import PipelineModel
#         return PipelineModel.read().load(directory_path)
#     elif framework == SPSS_FRAMEWORK:
#         pass
#     elif framework == TENSORFLOW_FRAMEWORK:
#         pass
#     elif framework == SCIKIT_LEARN_FRAMEWORK or framework == XGBOOST_FRAMEWORK:
#         from sklearn.externals import joblib
#         model_id = directory_path[directory_path.rfind('/') + 1:] + ".pkl"
#         return joblib.load(os.path.join(directory_path, model_id))
#     elif framework == PMML_MODEL:
#         pass
#     else:
#         raise WMLClientError('Invalid framework specified: \'{}\'.'.format(framework))


def load_model_from_package(framework, directory):
    unpack(directory)
    load_model_from_directory(framework, directory)


def save_model_to_file(model, framework, base_path, filename):
    if filename.find('.') != -1:
        base_name = filename[:filename.find('.') + 1]
        file_extension = filename[filename.find('.'):]
    else:
        base_name = filename
        file_extension = 'tar.gz'

    if framework == SPARK_MLLIB:
        model.write.overwrite.save(os.path.join(base_path, base_name))
    elif framework == SPSS_FRAMEWORK:
        pass
    elif framework == TENSORFLOW_FRAMEWORK:
        pass
    elif framework == XGBOOST_FRAMEWORK:
        pass
    elif framework == SCIKIT_LEARN_FRAMEWORK:
        os.makedirs(os.path.join(base_path, base_name))
        from sklearn.externals import joblib
        joblib.dump(model, os.path.join(base_path, base_name, base_name + ".pkl"))
    elif framework == PMML_FRAMEWORK:
        pass
    else:
        raise WMLClientError('Invalid framework specified: \'{}\'.'.format(framework))


def format_metrics(latest_metrics_list):
    formatted_metrics = ''
    for i in latest_metrics_list:
        for j in i['values']:
            formatted_metrics = formatted_metrics + i['phase'] + ':' + j['name']+'='+"{0:.4f}".format(j['value']) + '\n'
    return formatted_metrics
