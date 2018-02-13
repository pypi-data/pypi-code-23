################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


from repository_v3.mlrepositoryclient import MLRepositoryClient
from repository_v3.mlrepositoryartifact import MLRepositoryArtifact
from repository_v3.mlrepository import MetaProps, MetaNames
import requests
from watson_machine_learning_client.utils import get_headers, MODEL_DETAILS_TYPE, DEFINITION_DETAILS_TYPE, EXPERIMENT_DETAILS_TYPE, load_model_from_directory
from watson_machine_learning_client.metanames import ModelDefinitionMetaNames, ModelMetaNames, ExperimentMetaNames
import os
import copy
import json
from watson_machine_learning_client.wml_client_error import WMLClientError, MissingMetaProp
from watson_machine_learning_client.href_definitions import is_uid
from watson_machine_learning_client.wml_resource import WMLResource
from multiprocessing import Pool


class Repository(WMLResource):
    """
    Manage your models using Watson Machine Learning Repository.
    """
    DefinitionMetaNames = ModelDefinitionMetaNames()
    """MetaNames for definitions creation."""
    ModelMetaNames = ModelMetaNames()
    """MetaNames for models creation."""
    ExperimentMetaNames = ExperimentMetaNames()
    """MetaNames for experiments creation."""

    def __init__(self, client, wml_credentials, wml_token, ml_repository_client, instance_details):
        WMLResource.__init__(self, __name__, client, wml_credentials, wml_token, instance_details)
        Repository._validate_type(ml_repository_client, 'ml_repository_client', object, True)
        self._ml_repository_client = ml_repository_client
        self._definition_endpoint = '{}/v3/ml_assets/training_definitions'.format(self._wml_credentials['url'])
        self._experiment_endpoint = '{}/v3/experiments'.format(self._wml_credentials['url'])

    def store_experiment(self, meta_props):
        """
           Store experiment into Watson Machine Learning repository on IBM Cloud.

            :param meta_props: meta data of the experiment configuration. To see available meta names use:

               >>> client.repository.ExperimentMetaNames.get()
            :type meta_props: dict

            :returns: stored experiment details
            :rtype: dict

           A way you might use me is:

           >>> metadata = {
           >>>  client.repository.ExperimentMetaNames.NAME: "my_experiment",
           >>>  client.repository.ExperimentMetaNames.AUTHOR_EMAIL: "john.smith@ibm.com",
           >>>  client.repository.ExperimentMetaNames.EVALUATION_METRICS: ["accuracy"],
           >>>  client.repository.ExperimentMetaNames.TRAINING_DATA_REFERENCE: {"connection": {"endpoint_url": "https://s3-api.us-geo.objectstorage.softlayer.net", "access_key_id": "***", "secret_access_key": "***"}, "source": {"bucket": "train-data"}, "type": "s3"},
           >>>  client.repository.ExperimentMetaNames.TRAINING_RESULTS_REFERENCE: {"connection": {"endpoint_url": "https://s3-api.us-geo.objectstorage.softlayer.net", "access_key_id": "***", "secret_access_key": "***"}, "target": {"bucket": "result-data"}, "type": "s3"},
           >>>  client.repository.ExperimentMetaNames.TRAINING_REFERENCES: [
           >>>      {
           >>>        "training_definition_url": definition_url_1
           >>>      },
           >>>      {
           >>>        "training_definition_url": definition_url_2
           >>>      },
           >>>   ],
           >>> }
           >>> experiment_details = client.repository.store_experiment(meta_props=metadata)
           >>> experiment_url = client.repository.get_experiment_url(experiment_details)
        """
        Repository._validate_type(meta_props, 'meta_props', dict, False)
        self.ExperimentMetaNames._validate(meta_props)

        training_references = copy.deepcopy(meta_props[self.ExperimentMetaNames.TRAINING_REFERENCES])

        if any('training_definition_url' not in x for x in training_references):
            raise MissingMetaProp('training_references.training_definition_url')

        for ref in training_references:
            if 'name' not in ref or 'command' not in ref:

                training_definition_response = requests.get(ref['training_definition_url'].replace('/content', ''), headers=get_headers(self._wml_token))
                result = self._handle_response(200, 'getting training definition', training_definition_response)

                if not 'name' in ref:
                    ref.update({'name': result['entity']['name']})
                if not 'command' in ref:
                    ref.update({'command': result['entity']['command']})


        # TODO description, and method probably should be removed
        experiment_metadata = {
                       "settings": {
                          "name": meta_props[self.ExperimentMetaNames.NAME],
                          "description": "",
                          "author": {
                              "email": meta_props[self.ExperimentMetaNames.AUTHOR_EMAIL]
                          },
                          "evaluation_definition": {
                             "method": "multiclass",
                             "metrics": [{"name": x} for x in meta_props[self.ExperimentMetaNames.EVALUATION_METRICS]]
                          }
                       },
                       "training_references": training_references,
                       "training_data_reference": meta_props[self.ExperimentMetaNames.TRAINING_DATA_REFERENCE],
                       "training_results_reference": meta_props[self.ExperimentMetaNames.TRAINING_RESULTS_REFERENCE],
                    }

        if self.ExperimentMetaNames.DESCRIPTION in meta_props:
            experiment_metadata['settings'].update({'description': meta_props[self.ExperimentMetaNames.DESCRIPTION]})

        if self.ExperimentMetaNames.AUTHOR_NAME in meta_props:
            experiment_metadata['settings']['author'].update({'name': meta_props[self.ExperimentMetaNames.AUTHOR_NAME]})

        if self.ExperimentMetaNames.EVALUATION_METHOD in meta_props:
            experiment_metadata['settings']['evaluation_definition'].update({'method': meta_props[self.ExperimentMetaNames.EVALUATION_METHOD]})

        if self.ExperimentMetaNames.OPTIMIZATION_METHOD in meta_props or self.ExperimentMetaNames.OPTIMIZATION_PARAMETERS in meta_props:
            experiment_metadata['settings'].update({'hyper_parameters_optimization': {}})
            if self.ExperimentMetaNames.OPTIMIZATION_METHOD in meta_props:
                experiment_metadata['settings']['hyper_parameters_optimization'].update({'method': meta_props[self.ExperimentMetaNames.OPTIMIZATION_METHOD]})
            if self.ExperimentMetaNames.OPTIMIZATION_PARAMETERS in meta_props:
                experiment_metadata['settings']['hyper_parameters_optimization'].update({'parameters': meta_props[self.ExperimentMetaNames.OPTIMIZATION_PARAMETERS]})

        response_experiment_post = requests.post(self._experiment_endpoint, json=experiment_metadata, headers=get_headers(self._wml_token))

        return self._handle_response(201, 'saving experiment', response_experiment_post)

    def store_definition(self, training_definition, meta_props):
        """
            Store training definition into Watson Machine Learning repository on IBM Cloud.

            :param training_definition:  path to zipped model_definition
            :type training_definition: str

            :param meta_props: meta data of the training definition. To see available meta names use:

               >>> client.repository.DefinitionMetaNames.get()
            :type meta_props: dict


            :returns: stored training definition details
            :rtype: dict

            A way you might use me is:

            >>> metadata = {
            >>>  client.repository.DefinitionMetaNames.NAME: "my_training_definition",
            >>>  client.repository.DefinitionMetaNames.AUTHOR_EMAIL: "js@js.com",
            >>>  client.repository.DefinitionMetaNames.FRAMEWORK_NAME: "tensorflow",
            >>>  client.repository.DefinitionMetaNames.FRAMEWORK_VERSION: "1.2",
            >>>  client.repository.DefinitionMetaNames.RUNTIME_NAME: "python",
            >>>  client.repository.DefinitionMetaNames.RUNTIME_VERSION: "3.5",
            >>>  client.repository.DefinitionMetaNames.EXECUTION_COMMAND: "python3 tensorflow_mnist_softmax.py --trainingIters 20"
            >>> }
            >>> definition_details = client.repository.store_definition(training_definition_filepath, meta_props=metadata)
            >>> definition_url = client.repository.get_definition_url(definition_details)
        """
        Repository._validate_type(training_definition, 'training_definition', str, True)
        Repository._validate_type(meta_props, 'meta_props', dict, True)
        self.DefinitionMetaNames._validate(meta_props)

        # TODO to be replaced with repository client

        training_definition_metadata = {
                               "name": meta_props[self.DefinitionMetaNames.NAME],
                               "framework": {
                                   "name": meta_props[self.DefinitionMetaNames.FRAMEWORK_NAME],
                                   "version": meta_props[self.DefinitionMetaNames.FRAMEWORK_VERSION],
                                   "runtimes": [{
                                        "name": meta_props[self.DefinitionMetaNames.RUNTIME_NAME],
                                        "version": meta_props[self.DefinitionMetaNames.RUNTIME_VERSION]
                                    }]
                                },
                               "command": meta_props[self.DefinitionMetaNames.EXECUTION_COMMAND]
        }

        if self.DefinitionMetaNames.DESCRIPTION in meta_props:
            training_definition_metadata.update({'description': meta_props[self.DefinitionMetaNames.DESCRIPTION]})

        response_definition_post = requests.post(self._definition_endpoint, json=training_definition_metadata, headers=get_headers(self._wml_token))

        details = self._handle_response(201, 'saving model definition', response_definition_post)

        definition_version_content_url = details['entity']['training_definition_version']['content_url']
        # save model definition content
        put_header = {'Authorization': "Bearer " + self._wml_token, 'Content-Type': 'application/octet-stream'}
        data = open(training_definition, 'rb').read()
        response_definition_put = requests.put(definition_version_content_url, data=data, headers=put_header)

        self._handle_response(200, 'saving model definition content', response_definition_put)

        return details

    def _publish_from_object(self, model, meta_props, training_data=None, training_target=None, pipeline=None):
        """
        Store model from object in memory into Watson Machine Learning repository on Cloud
        """
        if self.ModelMetaNames.NAME not in meta_props:
            raise MissingMetaProp(self.ModelMetaNames.NAME)

        try:
            ml_repository_client = MLRepositoryClient(self._wml_credentials['url'])
            ml_repository_client.authorize(self._wml_credentials['username'], self._wml_credentials['password'])

            meta_data = MetaProps(meta_props)

            if 'pyspark.ml.pipeline.PipelineModel' in str(type(model)):
                pipeline_artifact = MLRepositoryArtifact(pipeline, name=meta_props[self.ModelMetaNames.NAME])
                model_artifact = MLRepositoryArtifact(model, name=meta_props[self.ModelMetaNames.NAME], meta_props=meta_data, training_data=training_data, pipeline_artifact=pipeline_artifact)
            else:
                model_artifact = MLRepositoryArtifact(model, name=meta_props[self.ModelMetaNames.NAME], meta_props=meta_data, training_data=training_data, training_target=training_target)

            saved_model = ml_repository_client.models.save(model_artifact)
        except Exception as e:
            raise WMLClientError("Publishing model failed.", e)
        else:
            return self.get_details(saved_model.uid)

    def _publish_from_training(self, model, meta_props, training_data=None, training_target=None):
        """
        Store trained model from object storage into Watson Machine Learning repository on IBM Cloud
        """
        self._validate_meta_prop(meta_props, self.ModelMetaNames.NAME, str, True)

        # TODO - check type etc
        #if not is_uid(model):
        #    raise WMLClientError('Invalid uid: \'{}\'.'.format(model))

        ml_asset_endpoint = '{}/v3/models/{}/ml_asset'.format(self._wml_credentials['url'], model)
        details = self._client.training.get_details(model)

        if details is not None:
            base_payload = {self.DefinitionMetaNames.NAME: meta_props[self.ModelMetaNames.NAME]}

            if meta_props is None:
                payload = base_payload
            else:
                payload = dict(base_payload, **meta_props)

            response_model_put = requests.put(ml_asset_endpoint, json=payload, headers=get_headers(self._wml_token))

            saved_model_details = self._handle_response(202, 'saving trained model', response_model_put)

            model_guid = WMLResource._get_required_element_from_dict(saved_model_details, 'saved_model_details', ['entity', 'ml_asset_guid'])
            content_status_endpoint = self._wml_credentials['url'] + '/v3/ml_assets/models/' + str(model_guid)
            response_content_status_get = requests.get(content_status_endpoint, headers=get_headers(self._wml_token))

            state = self._handle_response(200, 'checking saved model content status', response_content_status_get)['entity']['model_version']['content_status']['state']

            while ('persisted' not in state) and ('persisting_failed' not in state) and ('failure' not in state):
                response_content_status_get = requests.get(content_status_endpoint, headers=get_headers(self._wml_token))

                state = self._handle_response(200, 'checking saved model content status', response_content_status_get)['entity']['model_version']['content_status']['state']

            if 'persisted' in state:
                return saved_model_details
            else:
                raise WMLClientError('Saving trained model in repository for url: \'{}\' failed.'.format(content_status_endpoint), response_content_status_get.text)

    def _publish_from_file(self, model, meta_props=None, training_data=None, training_target=None):
        """
        Store saved model into Watson Machine Learning repository on IBM Cloud
        """
        def is_xml(model_filepath):
            return os.path.splitext(os.path.basename(model_filepath))[-1] == '.xml'

        self._validate_meta_prop(meta_props, self.ModelMetaNames.NAME, str, True)
        self._validate_meta_prop(meta_props, self.ModelMetaNames.FRAMEWORK_NAME, str, True)

        import tarfile
        import zipfile

        model_filepath = model
        if os.path.isdir(model):
            if meta_props[self.ModelMetaNames.FRAMEWORK_NAME] == "tensorflow": # TODO this part is ugly, but will work. In final solution this will be removed
                # TODO currently tar.gz is required for tensorflow - the same ext should be supported for all frameworks
                if os.path.basename(model) == '':
                    model = os.path.dirname(model)
                filename = os.path.basename(model) + '.tar.gz'
                current_dir = os.getcwd()
                os.chdir(model)
                target_path = os.path.dirname(model)

                with tarfile.open(os.path.join('..', filename), mode='w:gz') as tar:
                    tar.add('.')

                os.chdir(current_dir)
                model_filepath = os.path.join(target_path, filename)
                if tarfile.is_tarfile(model_filepath) or zipfile.is_zipfile(model_filepath) or is_xml(model_filepath):
                    try:
                        ml_repository_client = MLRepositoryClient(self._wml_credentials['url'])
                        ml_repository_client.authorize(self._wml_credentials['username'],
                                                       self._wml_credentials['password'])

                        model_artifact = MLRepositoryArtifact(model_filepath, name=meta_props[self.ModelMetaNames.NAME],
                                                              meta_props=MetaProps(meta_props))
                        saved_model = ml_repository_client.models.save(model_artifact)
                    except Exception as e:
                        raise WMLClientError("Publishing model failed.", e)
                    else:
                        return self.get_details(saved_model.uid)
            else:
                self._validate_meta_prop(meta_props, self.ModelMetaNames.FRAMEWORK_NAME, str, True)

                loaded_model = load_model_from_directory(meta_props[self.ModelMetaNames.FRAMEWORK_NAME], model)

                saved_model = self._publish_from_object(loaded_model, meta_props, training_data, training_target)

                return saved_model

        elif tarfile.is_tarfile(model_filepath) or zipfile.is_zipfile(model_filepath) or is_xml(model_filepath):
            try:
                ml_repository_client = MLRepositoryClient(self._wml_credentials['url'])
                ml_repository_client.authorize(self._wml_credentials['username'], self._wml_credentials['password'])

                model_artifact = MLRepositoryArtifact(model_filepath, name=meta_props[self.ModelMetaNames.NAME], meta_props=MetaProps(meta_props))
                saved_model = ml_repository_client.models.save(model_artifact)
            except Exception as e:
                raise WMLClientError("Publishing model failed.", e)
            else:
                return self.get_details(saved_model.uid)
        else:
            raise WMLClientError('Saving trained model in repository failed. \'{}\' file does not have valid format'.format(model_filepath))

    def store_model(self, model, meta_props=None, training_data=None, training_target=None, pipeline=None):
        """
        Store trained model into Watson Machine Learning repository on Cloud.

        :param model:  The train model object (e.g: spark PipelineModel), or path to saved model (`tar.gz`/`str`/`xml` or directory), or trained model guid
        :type model: object/str

        :param meta_props: meta data of the training definition. To see available meta names use:

            >>> client.repository.ModelMetaNames.get()

        :type meta_props: dict/str

        :param training_data:  Spark DataFrame supported for spark models. Pandas dataframe, numpy.ndarray or array supported for scikit-learn models
        :type training_data: spark dataframe, pandas dataframe, numpy.ndarray or array

        :param training_target: array with labels required for scikit-learn models
        :type training_target: array

        :param pipeline: pipeline required for spark mllib models
        :type training_target: object

        :returns: stored model details
        :rtype: dict

        The most simple use is:

        >>> stored_model_details = client.repository.store_model(model, name)

        In more complicated cases you should create proper metadata, similar to this one:

        >>> metadata = {
        >>>        client.repository.ModelMetaNames.NAME: "customer satisfaction prediction model",
        >>>        client.repository.ModelMetaNames.AUTHOR_EMAIL: "john.smith@ibm.com",
        >>>        client.repository.ModelMetaNames.FRAMEWORK_NAME: "tensorflow",
        >>>        client.repository.ModelMetaNames.FRAMEWORK_VERSION: "1.2",
        >>>        client.repository.ModelMetaNames.RUNTIME_NAME: "python",
        >>>        client.repository.ModelMetaNames.RUNTIME_VERSION: "3.5"
        >>>}

        where FRAMEWORK_NAME may be one of following: "spss-modeler", "tensorflow", "xgboost", "scikit-learn", "pmml".

        A way you might use me with local file containing model:

        >>> stored_model_details = client.repository.store_model(path_to_model_file, meta_props=metadata, training_data=None)

        A way you might use me with local directory containing model:

        >>> stored_model_details = client.repository.store_model(path_to_model_directory, meta_props=metadata, training_data=None)

        A way you might use me with trained model guid:

        >>> stored_model_details = client.repository.store_model(trained_model_guid, meta_props=metadata, training_data=None)
        """

        Repository._validate_type(model, 'model', object, True)
        Repository._validate_type(meta_props, 'meta_props', dict, True)
        # Repository._validate_type(training_data, 'training_data', object, False)
        # Repository._validate_type(training_target, 'training_target', list, False)
        self.ModelMetaNames._validate(meta_props)

        if (self.ModelMetaNames.RUNTIME_NAME in list(meta_props)) and (self.ModelMetaNames.RUNTIME_VERSION in list(meta_props)):
            meta_props[MetaNames.RUNTIMES] = json.dumps([{"name": meta_props[self.ModelMetaNames.RUNTIME_NAME], "version": meta_props[self.ModelMetaNames.RUNTIME_VERSION]}])

        if not isinstance(model, str):
            saved_model = self._publish_from_object(model=model, meta_props=meta_props, training_data=training_data, training_target=training_target, pipeline=pipeline)
        else:
            if (os.path.sep in model) or os.path.isfile(model) or os.path.isdir(model):
                if not os.path.isfile(model) and not os.path.isdir(model):
                    raise WMLClientError("Invalid path: neither file nor directory exists under this path: \'{}\'.".format(model))
                saved_model = self._publish_from_file(model=model, meta_props=meta_props, training_data=training_data, training_target=training_target)
            else:
                saved_model = self._publish_from_training(model=model, meta_props=meta_props, training_data=training_data, training_target=training_target)

        return saved_model


    def update_experiment(self, experiment_uid, changes):
        """
        Updates existing experiment metadata.

        :param experiment_uid: UID of experiment which definition should be updated
        :type experiment_uid: str

        :param changes: elements which should be changed, where keys are ExperimentMetaNames
        :type changes: dict

        :return: metadata of updated experiment
        :rtype: dict
        """
        self._validate_type(experiment_uid, "experiment_uid", str, True)
        self._validate_type(changes, "changes", dict, True)
        Repository._validate_meta_prop(changes, self.ExperimentMetaNames.NAME, str, False)
        Repository._validate_meta_prop(changes, self.ExperimentMetaNames.DESCRIPTION, str, False)
        Repository._validate_meta_prop(changes, self.ExperimentMetaNames.AUTHOR_NAME, str, False)
        Repository._validate_meta_prop(changes, self.ExperimentMetaNames.AUTHOR_EMAIL, str, False)
        Repository._validate_meta_prop(changes, self.ExperimentMetaNames.OPTIMIZATION_METHOD, str, False)
        Repository._validate_meta_prop(changes, self.ExperimentMetaNames.OPTIMIZATION_PARAMETERS, list, False)
        Repository._validate_meta_prop(changes, self.ExperimentMetaNames.EVALUATION_METHOD, str, False)
        Repository._validate_meta_prop(changes, self.ExperimentMetaNames.EVALUATION_METRICS, list, False)
        Repository._validate_meta_prop(changes, self.ExperimentMetaNames.TRAINING_REFERENCES, object, False)
        Repository._validate_meta_prop(changes, self.ExperimentMetaNames.TRAINING_DATA_REFERENCE, object, False)
        Repository._validate_meta_prop(changes, self.ExperimentMetaNames.TRAINING_RESULTS_REFERENCE, object, False)

        details = self.get_experiment_details(experiment_uid)

        def _decide_op(details, path):
            try:
                if len(path) == 1:
                    x = details[path[0]]
                    if x is not None:
                        return "replace"
                    else:
                        return "add"
                else:
                    _decide_op(details[path[0]], path[1:])
            except:
                return "add"


        def _update_patch_payload(patch_payload, changes, path, meta_name, value=None):
            if meta_name in changes:
                if value is None:
                    value = changes[meta_name]

                patch_payload.append(
                    {
                        "op": _decide_op(details, path),
                        "path": "/" + "/".join(path),
                        "value": value
                    }
                )


        patch_payload = []
        _update_patch_payload(patch_payload, changes, ["settings", "name"], self.ExperimentMetaNames.NAME)
        _update_patch_payload(patch_payload, changes, ["settings", "description"], self.ExperimentMetaNames.DESCRIPTION)
        _update_patch_payload(patch_payload, changes, ["settings", "author", "name"], self.ExperimentMetaNames.AUTHOR_NAME)
        _update_patch_payload(patch_payload, changes, ["settings", "author", "email"], self.ExperimentMetaNames.AUTHOR_EMAIL)
        _update_patch_payload(patch_payload, changes, ["settings", "hyper_parameters_optimization", "method"], self.ExperimentMetaNames.OPTIMIZATION_METHOD)
        _update_patch_payload(patch_payload, changes, ["settings", "hyper_parameters_optimization", "parameters"], self.ExperimentMetaNames.OPTIMIZATION_PARAMETERS)
        _update_patch_payload(patch_payload, changes, ["settings", "evaluation_definition", "method"], self.ExperimentMetaNames.EVALUATION_METHOD)
        _update_patch_payload(patch_payload, changes, ["training_data_reference"], self.ExperimentMetaNames.TRAINING_DATA_REFERENCE)
        _update_patch_payload(patch_payload, changes, ["training_results_reference"], self.ExperimentMetaNames.TRAINING_RESULTS_REFERENCE)

        if self.ExperimentMetaNames.EVALUATION_METRICS in changes:
            prepared_metrics = [{"name": x} for x in changes[self.ExperimentMetaNames.EVALUATION_METRICS]]
            _update_patch_payload(patch_payload, changes, ["settings", "evaluation_definition", "metrics"], self.ExperimentMetaNames.EVALUATION_METRICS, prepared_metrics)

        if self.ExperimentMetaNames.TRAINING_REFERENCES in changes:
            prepared_references = copy.deepcopy(changes[self.ExperimentMetaNames.TRAINING_REFERENCES])
            for ref in prepared_references:
                if 'name' not in ref or 'command' not in ref:

                    training_definition_response = requests.get(ref['training_definition_url'].replace('/content', ''),
                                                                headers=get_headers(self._wml_token))
                    result = self._handle_response(200, 'getting training definition', training_definition_response)

                    if not 'name' in ref:
                        ref.update({'name': result['entity']['name']})
                    if not 'command' in ref:
                        ref.update({'command': result['entity']['command']})
            _update_patch_payload(patch_payload, changes, ["training_references"], self.ExperimentMetaNames.TRAINING_REFERENCES, prepared_references)

        url = self._href_definitions.get_experiment_href(experiment_uid)
        response = requests.patch(url, json=patch_payload, headers=get_headers(self._wml_token))
        updated_details = self._handle_response(200, 'experiment patch', response)

        return updated_details

    def load(self, artifact_uid):
        """
        Load model from repository to object in local environment.

        :param artifact_uid:  stored model UID
        :type artifact_uid: str

        :returns: trained model
        :rtype: object

        A way you might use me is:

        >>> model = client.repository.load(model_uid)
        """
        Repository._validate_type(artifact_uid, 'artifact_uid', str, True)

        try:
            ml_repository_client = MLRepositoryClient(self._wml_credentials['url'])
            ml_repository_client.authorize(self._wml_credentials['username'], self._wml_credentials['password'])
            loaded_model = ml_repository_client.models.get(artifact_uid)
            loaded_model = loaded_model.model_instance()
            self._logger.info('Successfully loaded artifact with artifact_uid: {}'.format(artifact_uid))
            return loaded_model
        except Exception as e:
            raise WMLClientError("Loading model with artifact_uid: \'{}\' failed.".format(artifact_uid), e)

    def download(self, artifact_uid, filename='downloaded_model.tar.gz'):
        """
        Download model from repository to local file.

        :param artifact_uid: stored model UID
        :type artifact_uid: str

        :param filename: name of local file to create (optional)
        :type filename: str

        Side effect:
            save model to file.

        A way you might use me is:

        >>> client.repository.download(model_uid, 'my_model.tar.gz')
        """
        if os.path.isfile(filename):
            raise WMLClientError('File with name: \'{}\' already exists.'.format(filename))

        Repository._validate_type(artifact_uid, 'artifact_uid', str, True)
        Repository._validate_type(filename, 'filename', str, True)

        artifact_url = self._href_definitions.get_model_last_version_href(artifact_uid)

        try:
            artifact_content_url = artifact_url + '/content'
            downloaded_model = self._ml_repository_client.repository_api.download_artifact_content(artifact_content_url, accept='application/gzip')
            self._logger.info('Successfully downloaded artifact with artifact_url: {}'.format(artifact_url))
        except Exception as e:
            raise WMLClientError("Downloading model with artifact_url: \'{}\' failed.".format(artifact_url), e)

        try:
            with open(filename, 'wb') as f:
                f.write(downloaded_model.data)
            self._logger.info('Successfully saved artifact to file: \'{}\''.format(filename))
            return None
        except IOError as e:
            raise WMLClientError("Saving model with artifact_url: \'{}\' failed.".format(filename), e)

    def delete(self, artifact_uid):
        """
            Delete model, definition or experiment from repository.

            :param artifact_uid: stored model, definition, or experiment UID
            :type artifact_uid: str

            A way you might use me is:

            >>> client.repository.delete(artifact_uid)
        """
        Repository._validate_type(artifact_uid, 'artifact_uid', str, True)

        artifact_type = self._check_artifact_type(artifact_uid)
        self._logger.debug('Attempting deletion of artifact with type: \'{}\''.format(str(artifact_type)))

        if artifact_type['model'] is True:
            try:
                deleted = self._ml_repository_client.models.remove(artifact_uid)
                self._logger.info('Successfully deleted model with artifact_uid: \'{}\''.format(artifact_uid))
                self._logger.debug('Return object: {}'.format(deleted))
                return
            except Exception as e:
                raise WMLClientError("Model deletion failed.", e)
        elif artifact_type['definition'] is True:
            definition_endpoint = self._definition_endpoint + '/' + artifact_uid
            self._logger.debug('Deletion artifact definition endpoint: {}'.format(definition_endpoint))
            response_delete = requests.delete(definition_endpoint, headers=get_headers(self._wml_token))

            self._handle_response(204, 'model definition deletion', response_delete, False)
            return

        elif artifact_type['experiment'] is True:
            experiment_endpoint = self._experiment_endpoint + '/' + artifact_uid
            self._logger.debug('Deletion artifact experiment endpoint: {}'.format(experiment_endpoint))
            response_delete = requests.delete(experiment_endpoint, headers=get_headers(self._wml_token))

            self._handle_response(204, 'experiment deletion', response_delete, False)
            return

        else:
            raise WMLClientError('Artifact with artifact_uid: \'{}\' does not exist.'.format(artifact_uid))

    def get_details(self, artifact_uid=None):
        """
           Get metadata of stored artifacts. If uid is not specified returns all models and definitions metadata.

           :param artifact_uid:  stored model, definition or experiment UID (optional)
           :type artifact_uid: str

           :returns: stored artifacts metadata
           :rtype: dict

           A way you might use me is:

           >>> details = client.repository.get_details(artifact_uid)
           >>> details = client.repository.get_details()
        """
        Repository._validate_type(artifact_uid, 'artifact_uid', str, False)

        if artifact_uid is None:
            model_details = self.get_model_details()
            definition_details = self.get_definition_details()
            details = {'models:': model_details, 'definitions': definition_details}
        else:
            uid_type = self._check_artifact_type(artifact_uid)
            if uid_type['model'] is True:
                details = self.get_model_details(artifact_uid)
            elif uid_type['definition'] is True:
                details = self.get_definition_details(artifact_uid)
            elif uid_type['experiment'] is True:
                details = self.get_definition_details(artifact_uid)
            else:
                raise WMLClientError('Getting artifact details failed. Artifact uid: \'{}\' not found.'.format(artifact_uid))

        return details

    def get_model_details(self, model_uid=None):
        """
           Get metadata of stored models. If model uid is not specified returns all models metadata.

           :param model_uid: stored model, definition or pipeline UID (optional)
           :type model_uid: str

           :returns: stored model(s) metadata
           :rtype: dict

           A way you might use me is:

           >>> model_details = client.repository.get_model_details(model_uid)
           >>> models_details = client.repository.get_model_details()
        """
        Repository._validate_type(model_uid, 'model_uid', str, False)

        url = self._instance_details.get('entity').get('published_models').get('url')

        if model_uid is None:
            response_get = requests.get(
                url,
                headers=get_headers(self._wml_token))
        else:
            if not is_uid(model_uid):
                raise('Failure during getting model details, invalid uid: \'{}\''.format(model_uid))
            else:
                url = url + "/" + model_uid

            response_get = requests.get(
                url,
                headers=get_headers(self._wml_token))

        return self._handle_response(200, 'getting model details', response_get)

    def get_definition_details(self, definition_uid=None):
        """
            Get metadata of stored definitions. If definition uid is not specified returns all model definitions metadata.

            :param definition_uid:  stored model definition UID (optional)
            :type definition_uid: str

            :returns: stored definition(s) metadata
            :rtype: dict

            A way you might use me is:

            >>> definition_details = client.repository.get_definition_details(definition_uid)
            >>> definition_details = client.repository.get_definition_details()
         """
        Repository._validate_type(definition_uid, 'definition_uid', str, False)

        url = self._definition_endpoint

        if definition_uid is None:
            params = {'limit': '1000'}
            response_get = requests.get(url, headers=get_headers(self._wml_token), params=params)
        else:
            if not is_uid(definition_uid):
                raise WMLClientError('Failure during getting definition details, invalid uid: \'{}\''.format(definition_uid))
            else:
                url = url + '/' + definition_uid

            response_get = requests.get(url, headers=get_headers(self._wml_token))

        return self._handle_response(200, 'getting definition details', response_get)

    def get_experiment_details(self, experiment_uid=None):
        """
            Get metadata of stored experiments. If neither experiment uid nor url is specified all experiments metadata is returned.

            :param experiment_uid: stored experiment UID (optional)
            :type experiment_uid: str

            :returns: stored experiment(s) metadata
            :rtype: dict

            A way you might use me is:

            >>> experiment_details = client.repository.get_experiment_details(experiment_uid)
            >>> experiment_details = client.repository.get_experiment_details()
         """
        Repository._validate_type(experiment_uid, 'experiment_uid', str, False)

        url = self._experiment_endpoint

        if experiment_uid is None:
            params = {'limit': '1000'}
            response_get = requests.get(url, headers=get_headers(self._wml_token), params=params)
        else:
            if not is_uid(experiment_uid):
                raise WMLClientError('Failure during getting experiment details, invalid uid: \'{}\''.format(experiment_uid))
            else:
                url = url + '/' + experiment_uid

            response_get = requests.get(url, headers=get_headers(self._wml_token))

        return self._handle_response(200, 'getting experiment details', response_get)

    @staticmethod
    def get_model_url(model_details):
        """
            Get url of stored model.

            :param model_details:  stored model details
            :type model_details: dict

            :returns: url to stored model
            :rtype: str

            A way you might use me is:

            >>> model_url = client.repository.get_model_url(model_details)
        """
        Repository._validate_type(model_details, 'model_details', object, True)
        Repository._validate_type_of_details(model_details, MODEL_DETAILS_TYPE)

        try:
            return model_details['entity']['ml_asset_url']
        except:
            return WMLResource._get_required_element_from_dict(model_details, 'model_details', ['metadata', 'url'])

    @staticmethod
    def get_model_uid(model_details):
        """
            Get uid of stored model.

            :param model_details:  stored model details
            :type model_details: dict

            :returns: uid of stored model
            :rtype: str

            A way you might use me is:

            >>> model_uid = client.repository.get_model_uid(model_details)
        """
        Repository._validate_type(model_details, 'model_details', object, True)
        Repository._validate_type_of_details(model_details, MODEL_DETAILS_TYPE)

        try:
            return model_details['entity']['ml_asset_guid']
        except:
            return WMLResource._get_required_element_from_dict(model_details, 'model_details', ['metadata', 'guid'])

    @staticmethod
    def get_definition_url(definition_details):
        """
            Get url of stored definition.

            :param definition_details:  stored definition details
            :type definition_details: dict

            :returns: url of stored definition
            :rtype: str

            A way you might use me is:

            >>> definition_url = client.repository.get_definition_url(definition_details)
        """
        Repository._validate_type(definition_details, 'definition_details', object, True)
        Repository._validate_type_of_details(definition_details, DEFINITION_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(definition_details, 'definition_details', ['metadata', 'url'])

    @staticmethod
    def get_definition_uid(definition_details):
        """
            Get uid of stored model.

            :param definition_details: stored definition details
            :type definition_details: dict

            :returns: uid of stored model
            :rtype: str

            A way you might use me is:

            >>> definition_uid = client.repository.get_definition_uid(definition_details)
        """
        Repository._validate_type(definition_details, 'definition_details', object, True)
        Repository._validate_type_of_details(definition_details, DEFINITION_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(definition_details, 'definition_details', ['metadata', 'guid'])

    @staticmethod
    def get_experiment_uid(experiment_details):
        """
            Get uid of stored experiment.

            :param experiment_details: stored experiment details
            :type experiment_details: dict

            :returns: uid of stored experiment
            :rtype: str

            A way you might use me is:

            >>> experiment_uid = client.repository.get_experiment_uid(experiment_details)
        """
        Repository._validate_type(experiment_details, 'experiment_details', object, True)
        Repository._validate_type_of_details(experiment_details, EXPERIMENT_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(experiment_details, 'experiment_details', ['metadata', 'guid'])

    @staticmethod
    def get_experiment_url(experiment_details):
        """
            Get url of stored experiment.

            :param experiment_details:  stored experiment details
            :type experiment_details: dict

            :returns: url of stored experiment
            :rtype: str

            A way you might use me is:

            >>> experiment_url = client.repository.get_experiment_url(experiment_details)
        """
        Repository._validate_type(experiment_details, 'experiment_details', object, True)
        Repository._validate_type_of_details(experiment_details, EXPERIMENT_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(experiment_details, 'experiment_details', ['metadata', 'url'])

    def list(self):
        """
           List stored models, definitions and experiments.

           A way you might use me is:

           >>> client.repository.list()
        """
        from tabulate import tabulate

        headers = get_headers(self._wml_token)
        params = {'limit': '1000'}

        with Pool(processes=4) as pool:
            model_get = pool.apply_async(Repository._get, (self._instance_details.get('entity').get('published_models').get('url'), headers))
            definition_get = pool.apply_async(Repository._get, (self._definition_endpoint, headers, params))
            experiment_get = pool.apply_async(Repository._get, (self._experiment_endpoint, headers, params))

            model_resources = []
            definition_resources = []
            experiment_resources = []

            try:
                model_response = model_get.get()
                model_text = self._handle_response(200, "getting all models", model_response)
                model_resources = model_text['resources']
            except Exception as e:
                self._logger.error(e)
            try:
                definition_response = definition_get.get()
                definition_text = self._handle_response(200, "getting all definitions", definition_response)
                definition_resources = definition_text['resources']
            except Exception as e:
                self._logger.error(e)
            try:
                experiment_response = experiment_get.get()
                experiment_text = self._handle_response(200, "getting all experiments", experiment_response)
                experiment_resources = experiment_text['resources']
            except Exception as e:
                self._logger.error(e)

        model_values = [(m['metadata']['guid'], m['entity']['name'], m['metadata']['created_at'], m['entity']['model_type'], 'model') for m in model_resources]
        experiment_values = [(m['metadata']['guid'], m['entity']['settings']['name'], m['metadata']['created_at'], '-', 'experiment') for m in experiment_resources]
        definition_values = [(m['metadata']['guid'], m['entity']['name'], m['metadata']['created_at'], m['entity']['framework']['name'], 'definition') for m in definition_resources]

        values = sorted(list(set(model_values + definition_values + experiment_values)), key=lambda x: x[4])
        table = tabulate([["GUID", "NAME", "CREATED", "FRAMEWORK", "TYPE"]] + values)
        print(table)

    def list_models(self):
        """
           List stored models.

           A way you might use me is

           >>> client.repository.list_models()
        """
        from tabulate import tabulate

        model_resources = self.get_model_details()['resources']
        model_values = [(m['metadata']['guid'], m['entity']['name'], m['metadata']['created_at'], m['entity']['model_type'], 'model') for m in model_resources]
        table = tabulate([["GUID", "NAME", "CREATED", "FRAMEWORK", "TYPE"]] + model_values)
        print(table)

    def list_experiments(self):
        """
           List stored experiments.

           A way you might use me is

           >>> client.repository.list_experiments()
        """
        from tabulate import tabulate

        experiment_resources = self.get_experiment_details()['resources']
        experiment_values = [(m['metadata']['guid'], m['entity']['settings']['name'], m['metadata']['created_at'], '-', 'experiment') for m in experiment_resources]
        table = tabulate([["GUID", "NAME", "CREATED", "FRAMEWORK", "TYPE"]] + experiment_values)
        print(table)

    def list_definitions(self):
        """
           List stored definitions.

           A way you might use me is

           >>> client.repository.list_definitions()
        """
        from tabulate import tabulate

        definition_resources = self.get_definition_details()['resources']
        definition_values = [(m['metadata']['guid'], m['entity']['name'], m['metadata']['created_at'], m['entity']['framework']['name'], 'definition') for m in definition_resources]
        table = tabulate([["GUID", "NAME", "CREATED", "FRAMEWORK", "TYPE"]] + definition_values)

        print(table)

    @staticmethod
    def _get(url, headers, params=None):
        return requests.get(url, headers=headers, params=params)

    def _check_artifact_type(self, artifact_uid):
        Repository._validate_type(artifact_uid, 'artifact_uid', str, True)
        is_model = False
        is_definition = False
        is_experiment = False

        with Pool(processes=4) as pool:
            definition_future = pool.apply_async(self._get, (
                self._definition_endpoint + '/' + artifact_uid,
                get_headers(self._wml_token)
            ))
            model_future = pool.apply_async(self._get, (
                self._instance_details.get('entity').get('published_models').get('url') + "/" + artifact_uid,
                get_headers(self._wml_token)
            ))
            experiment_future = pool.apply_async(self._get, (
                self._experiment_endpoint + "/" + artifact_uid,
                get_headers(self._wml_token)
            ))

            response_definition_get = None
            response_model_get = None
            response_experiment_get = None

            try:
                response_definition_get = definition_future.get()
                self._logger.debug('Response({})[{}]: {}'.format(self._definition_endpoint + '/' + artifact_uid, response_definition_get.status_code, response_definition_get.text))
            except Exception as e:
                self._logger.debug('Error during checking artifact type: ' + str(e))

            try:
                response_model_get = model_future.get()
                self._logger.debug('Response({})[{}]: {}'.format(self._instance_details.get('entity').get('published_models').get('url') + "/" + artifact_uid, response_model_get.status_code, response_model_get.text))
            except Exception as e:
                self._logger.debug('Error during checking artifact type: ' + str(e))

            try:
                response_experiment_get = experiment_future.get()
                self._logger.debug('Response({})[{}]: {}'.format(self._experiment_endpoint + "/" + artifact_uid, response_experiment_get.status_code, response_experiment_get.text))
            except Exception as e:
                self._logger.debug('Error during checking artifact type: ' + str(e))

        if response_model_get is not None and 'status_code' in dir(response_model_get) and response_model_get.status_code == 200:
            is_model = True
            return {'definition': is_definition, 'model': is_model, 'experiment': is_experiment}
        elif response_definition_get is not None and 'status_code' in dir(response_definition_get) and response_definition_get.status_code == 200:
            is_definition = True
            return {'definition': is_definition, 'model': is_model, 'experiment': is_experiment}
        elif response_experiment_get is not None and 'status_code' in dir(response_experiment_get) and response_experiment_get.status_code == 200:
            is_experiment = True
            return {'definition': is_definition, 'model': is_model, 'experiment': is_experiment}
        else:
            return {'definition': is_definition, 'model': is_model, 'experiment': is_experiment}
