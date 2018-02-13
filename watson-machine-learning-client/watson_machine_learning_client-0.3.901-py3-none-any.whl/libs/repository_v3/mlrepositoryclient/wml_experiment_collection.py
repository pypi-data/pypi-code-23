################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


import logging, re

from repository_v3.mlrepository import MetaNames
from repository_v3.mlrepositoryartifact.experiment_artifact import ExperimentArtifact
from repository_v3.swagger_client.api_client import ApiException
import json
from .wml_experiment_adapter import WmlExperimentCollectionAdapter
from repository_v3.swagger_client.models import ExperimentInput,ExperimentAssetTag,\
    ExperimentInputSettings,MetricObjectExperiments,HyperParametersOptimizationExperiments,EvaluationDefinitionExperiments
from repository_v3.swagger_client.models import TrainingReferenceExperiments,ComputeConfigurationExperiments,HyperParametersExperimentsInnerValuesRange
from repository_v3.swagger_client.models import  ConnectionObjectTargetExperiments,ConnectionObjectSourceExperiments,AuthorExperiments, PatchOperationExperiments, HyperParametersExperiments

logger = logging.getLogger('WmlExperimentCollection')


class WmlExperimentCollection:
    """
    Client operating on experiments in repository service.

    :param str base_path: base url to Watson Machine Learning instance
    :param MLRepositoryApi repository_api: client connecting to repository rest api
    :param MLRepositoryClient client: high level client used for simplification and argument for constructors
    """
    def __init__(self, base_path, repository_api, client):

        from repository_v3.mlrepositoryclient import MLRepositoryApi, MLRepositoryClient

        if not isinstance(base_path, str) and not isinstance(base_path, unicode):
            raise ValueError('Invalid type for base_path: {}'.format(base_path.__class__.__name__))

        if not isinstance(repository_api, MLRepositoryApi):
            raise ValueError('Invalid type for repository_api: {}'.format(repository_api.__class__.__name__))

        if not isinstance(client, MLRepositoryClient):
            raise ValueError('Invalid type for client: {}'.format(client.__class__.__name__))

        self.base_path = base_path
        self.repository_api = repository_api
        self.client = client


    def all(self, queryMap=None):
        """
        Gets info about all experiments which belong to this user.

        Not complete information is provided by all(). To get detailed information about experiment use get().

        :return: info about experiments
        :rtype: list[ExperimentsArtifact]
        """
        all_experiments = self.repository_api.repository_listexperiments(queryMap)
        list_experiment_artifact = []
        if all_experiments is not None:
            resr = all_experiments.resources

            for iter1 in resr:
                list_experiment_artifact.append(WmlExperimentCollectionAdapter(iter1, self.client).artifact())
            return list_experiment_artifact
        else:
            return []


    def get(self, experiment):

        """
        Gets detailed information about experiment.

        :param str experiment_id: uid used to identify experiment
        :return: returned object has all attributes of SparkPipelineArtifact but its class name is PipelineArtifact
        :rtype: PipelineArtifact(SparkPipelineLoader)
        """

        if not isinstance(experiment, str) and  not isinstance(experiment, unicode):
            raise ValueError('Invalid type for experiment_id: {}'.format(experiment.__class__.__name__))
        if(experiment.__contains__("/v3/experiments")):
            matched = re.search('.*/v3/experiments/([A-Za-z0-9\-]+)', experiment)
            if matched is not None:
                experiment_id = matched.group(1)
                return self.get(experiment_id)
            else:
                raise ValueError('Unexpected artifact href: {} format'.format(experiment))
        else:
            experiment_output = self.repository_api.v3_experiments_id_get(experiment)
            if experiment_output is not None:
                return WmlExperimentCollectionAdapter(experiment_output,self.client).artifact()
            else:
                raise Exception('Experiment not found'.format(experiment))


    def remove(self, experiment):
        """
        Removes experiment with given experiment_id.

        :param str experiment_id: uid used to identify experiment
        """

        if not isinstance(experiment, str) and not isinstance(experiment, unicode):
            raise ValueError('Invalid type for experiment_id: {}'.format(experiment.__class__.__name__))
        if(experiment.__contains__("/v3/experiments")):
            matched = re.search('.*/v3/experiments/([A-Za-z0-9\-]+)', experiment)
            if matched is not None:
                experiment_id = matched.group(1)
                self.remove(experiment_id)
            else:
                raise ValueError('Unexpected experiment artifact href: {} format'.format(experiment))
        else:
            return self.repository_api.v3_experiments_id_delete(experiment)

    def patch(self, experiment_id, artifact):
        experiment_patch_input = self.prepare_experiment_patch_input(artifact)
        experiment_patch_output = self.repository_api.v3_experiments_id_patch_with_http_info(experiment_id, experiment_patch_input)
        statuscode = experiment_patch_output[1]

        if statuscode is not 200:
            logger.info('Error while patching experiment: no location header')
            raise ApiException(statuscode,"Error while patching experiment")

        if experiment_patch_output is not None:
            new_artifact =  WmlExperimentCollectionAdapter(experiment_patch_output[0],self.client).artifact()
        return new_artifact

    def save(self, artifact):
        """
        Saves experiment in repository service.

        :param SparkPipelineArtifact artifact: artifact to be saved in the repository service
        :return: saved artifact with changed MetaProps
        :rtype: SparkPipelineArtifact
        """
        logger.debug('Creating a new WML experiment: {}'.format(artifact.name))

        if not issubclass(type(artifact), ExperimentArtifact):
            raise ValueError('Invalid type for artifact: {}'.format(artifact.__class__.__name__))

        experiment_input = self._prepare_wml_experiment_input(artifact)
        experiment_output = self.repository_api.wml_assets_experiment_creation_with_http_info(experiment_input)


        statuscode = experiment_output[1]
        if statuscode is not 201:
            logger.info('Error while creating experiment: no location header')
            raise ApiException(statuscode, 'No artifact location')

        if experiment_output is not None:
            new_artifact =  WmlExperimentCollectionAdapter(experiment_output[0],self.client).artifact()
        return new_artifact



    @staticmethod
    def _prepare_wml_experiment_input(artifact):

        tags_data_list = None
        settings_data = None
        training_reference_list=None
        training_data_ref = None
        training_results_ref=None
        hyper_param_list = None

        #tags
        tags=artifact.meta.prop(MetaNames.EXPERIMENTS.TAGS)
        if isinstance(tags, str):
            tags_list = json.loads(artifact.meta.prop(MetaNames.EXPERIMENTS.TAGS))
            tags_data_list = []
            if isinstance(tags_list, list):
               for iter1 in tags_list:
                 tags_data = ExperimentAssetTag()
                 for key in iter1:
                    if key == 'value':
                        tags_data.value= iter1['value']
                    if key == 'description':
                        tags_data.description = iter1['description']
                 tags_data_list.append(tags_data)
            else:
                raise ValueError("Invalid tag Input")

        #settings
        if artifact.meta.prop(MetaNames.EXPERIMENTS.SETTINGS) is  None:
           raise ValueError("MetaNames.EXPERIMENTS.SETTINGS not defined")

        settings=artifact.meta.prop(MetaNames.EXPERIMENTS.SETTINGS)
        if isinstance(settings, str):
            settings = json.loads(artifact.meta.prop(MetaNames.EXPERIMENTS.SETTINGS))

            if isinstance(settings, dict):
                author=settings.get('author', None)
                author_experiment = None
                if author is not None:
                    author_name = author.get('name',None)
                    author_email = author.get('email')
                    author_experiment = AuthorExperiments(author_name,author_email)

                hyper_parameters_optimization = settings.get('hyper_parameters_optimization', None)
                hyper_parameters_optimization_exp=None
                if hyper_parameters_optimization is not None:
                    hyper_parameters_optimization_method = hyper_parameters_optimization.get('method')
                    hyper_parameters_optimization_param = hyper_parameters_optimization.get('parameters' ,None)
                    hyper_parameters_optimization_exp = HyperParametersOptimizationExperiments(hyper_parameters_optimization_method,
                                                           hyper_parameters_optimization_param)

                evaluation_definition = settings.get('evaluation_definition',None)
                evaluation_definition_exp = None
                if evaluation_definition is not None:
                    evaluation_definition_method = evaluation_definition.get('method',None)
                    evaluation_definition_metrics = evaluation_definition.get('metrics')
                    metrics_experiments = []
                    if isinstance(evaluation_definition_metrics, list):
                      for iter1 in evaluation_definition_metrics:
                        metrics_data = MetricObjectExperiments()
                        for key in iter1:
                            if key == 'name':
                                metrics_data.name= iter1['name']
                            metrics_experiments.append(metrics_data)
                    else:
                        raise ValueError("Invalid Input: Metrics list Expected")
                    evaluation_definition_exp = EvaluationDefinitionExperiments(evaluation_definition_method,metrics_experiments)


                settings_data = ExperimentInputSettings(
                    name = settings.get('name'),
                    description = settings.get('description', None),
                    author=author_experiment,
                    label_column= settings.get('label_column', None),
                    hyper_parameters_optimization=hyper_parameters_optimization_exp,
                    evaluation_definition= evaluation_definition_exp
                    )

        #training_refrences
        training_ref=artifact.meta.prop(MetaNames.EXPERIMENTS.TRAINING_REFERENCES)
        if isinstance(training_ref, str):
            training_ref_list = json.loads(artifact.meta.prop(MetaNames.EXPERIMENTS.TRAINING_REFERENCES))
            training_reference_list = []
            if isinstance(training_ref_list, list):
                for iter1 in training_ref_list:
                    compute = iter1.get('compute_configuration', None)
                    compute_config_object = None
                    if compute is not None:
                        compute_name = compute.get('name')
                        compute_nodes = compute.get('nodes',None)
                        compute_config_object = ComputeConfigurationExperiments(compute_name, compute_nodes)


                    hyper_params = iter1.get('hyper_parameters', None)



                    hyper_params_values_range_object = None
                    if isinstance(hyper_params, list):
                        hyper_param_list = []
                        hyper_params_object = None
                        for iter2 in hyper_params:
                            for key in iter2:
                                if key == 'name':
                                    hyper_params_name= iter2['name']
                                if key == 'values':
                                    hyper_params_values = iter2['values']
                                if key == 'values_range':
                                    hyper_params_values_range = iter2['values_range']
                                    if hyper_params_values_range is not None:
                                        hyper_params_from = hyper_params_values_range.get('from')
                                        hyper_params_to  = hyper_params_values_range.get('to')
                                        hyper_params_step  = hyper_params_values_range.get('step')
                                        hyper_params_values_range_object = HyperParametersExperimentsInnerValuesRange(
                                            hyper_params_from, hyper_params_to, hyper_params_step)

                            hyper_params_object = HyperParametersExperiments(hyper_params_name,
                                                                                  hyper_params_values,
                                                                                  hyper_params_values_range_object )
                            hyper_param_list.append(hyper_params_object)

                    training_reference = TrainingReferenceExperiments(
                            name = iter1.get('name'),
                            training_definition_url= iter1.get('training_definition_url'),
                            command = iter1.get('command', None),
                            hyper_parameters = hyper_param_list,
                            compute_configuration = compute_config_object,
                            pretrained_model_url = iter1.get('pretrained_model_url', None)
                        )
                    training_reference_list.append(training_reference)

            else:
                raise ApiException(404, 'Invalid Input')

        #Training_data_reference
        if artifact.meta.prop(MetaNames.EXPERIMENTS.TRAINING_DATA_REFERENCE) is  None:
            raise ValueError("MetaNames.EXPERIMENTS.TRAINING_DATA_REFERENCE not defined")

        training_data_ref = artifact.meta.prop(MetaNames.EXPERIMENTS.TRAINING_DATA_REFERENCE)
        if isinstance(training_data_ref, str):
            dataref = json.loads(artifact.meta.prop(MetaNames.EXPERIMENTS.TRAINING_DATA_REFERENCE))
            if isinstance(dataref, dict):
                training_data_ref = ConnectionObjectSourceExperiments(
                        dataref.get('type'),
                        dataref.get('connection'),
                        dataref.get('source')
                    )
            else:
                raise ApiException(404, 'Invalid  TRAINING_DATA_REFERENCE Input')

        #Training_result_refernce
        if artifact.meta.prop(MetaNames.EXPERIMENTS.TRAINING_RESULTS_REFERENCE) is not None:
            training_results_ref = artifact.meta.prop(MetaNames.EXPERIMENTS.TRAINING_RESULTS_REFERENCE)
            if isinstance(training_results_ref, str):
                resultref_dict = json.loads(artifact.meta.prop(MetaNames.EXPERIMENTS.TRAINING_RESULTS_REFERENCE))
                if isinstance(resultref_dict, dict):
                    training_results_ref = ConnectionObjectTargetExperiments(
                        resultref_dict.get('type', None),
                        resultref_dict.get('connection', None),
                        resultref_dict.get('target', None)
                    )
                else:
                    raise ApiException(404, 'Invalid TRAINING_RESULTS_REFERENCE Input')


        experiments_input = ExperimentInput(
            tags=tags_data_list,
            settings=settings_data,
            training_references=training_reference_list,
            training_data_reference=training_data_ref,
            training_results_reference=training_results_ref

        )

        return experiments_input


    @staticmethod
    def prepare_experiment_patch_input(artifact):
        patch_list =[]
        patch_input = artifact.meta.prop(MetaNames.EXPERIMENTS.PATCH_INPUT)
        if isinstance(patch_input, str):
            patch_input_list = json.loads(artifact.meta.prop(MetaNames.EXPERIMENTS.PATCH_INPUT))
            if isinstance(patch_input_list, list):
                for iter1 in patch_input_list:
                    experiment_patch = PatchOperationExperiments(
                        op = iter1.get('op'),
                        path= iter1.get('path'),
                        value = iter1.get('value', None),
                        _from =iter1.get('from', None),
                    )
                    patch_list.append(experiment_patch)

                return patch_list
            else:
                raise ApiException(404, 'Invalid Patch Input')
        else:
            raise ApiException(404, 'Invalid Patch Input')
