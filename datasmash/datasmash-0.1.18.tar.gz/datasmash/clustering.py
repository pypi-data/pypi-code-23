import os
import csv
import time
import subprocess as sp
import numpy as np
import pandas as pd
from typing import Dict
from sklearn.cluster import KMeans
from datasmash.utils import (quantizer, DatasetLoader, pprint_dict,
                             quantize_inplace, smash, smashmatch,
                             matrix_list_p_norm, argmax_prod_matrix_list)
from datasmash.config import CWD, BIN_PATH

from d3m_metadata import container, hyperparams, metadata as metadata_module, params, utils
from primitive_interfaces.base import CallResult
from primitive_interfaces.clustering import ClusteringPrimitiveBase


Inputs = container.dataset.Dataset
Outputs = container.numpy.ndarray


class Params(params.Params):
    pass


class Hyperparams(hyperparams.Hyperparams):
    n_clusters = hyperparams.Hyperparameter[int](
        default = 2,
        description = 'Number of clusters per class. '
    )


class SmashClustering(ClusteringPrimitiveBase[Inputs, Outputs, Params,
                                              Hyperparams]):
    """

    """
    __author__ = "UChicago"
    metadata = metadata_module.PrimitiveMetadata({
        "algorithm_types": ['HIDDEN_MARKOV_MODEL', 'RANDOM_WALK',
                            'VARIABLE_ORDER_MARKOV_MODEL'],
        "name": "datasmash.classification.SmashClustering",
        "primitive_family": "CLUSTERING",
        "python_path": "d3m.primitives.datasmash.SmashClustering",
        "source": {'name': 'UChicago'},
        "version": "0.1.18",
        "id": "74767ad3-ac44-4d20-9c1c-248f56a42428",
        "installation": [
            {'type': metadata_module.PrimitiveInstallationType.PIP,
             'package': 'numpy',
             'version': '1.14.0'
            },
            {'type': metadata_module.PrimitiveInstallationType.PIP,
             'package': 'pandas',
             'version': '0.22.0'
            },
            {'type': metadata_module.PrimitiveInstallationType.PIP,
             'package': 'scikit-learn',
             'version': '0.19.1'
            },
            {'type': metadata_module.PrimitiveInstallationType.PIP,
             'package': 'imageio',
             'version': '2.2.0'
            },
            {'type': metadata_module.PrimitiveInstallationType.PIP,
             'package': 'datasmash',
             'version': '0.1.18'
            }
        ],
        "hyperparameters_to_tune": [
            "n_clusters"
        ],
        "keywords": [
            'time',
            'series',
            'data smashing',
            'data-smashing',
            'data_smashing',
            'datasmashing',
            'clustering',
            'parameter-free',
            'hyperparameter-free'
        ]
    })


    def __init__(self, *,
                 hyperparams: Hyperparams,
                 random_seed: int = 0,
                 docker_containers: Dict[str, str] = None,
                 _verbose: int = 0) -> None:

        super().__init__(hyperparams=hyperparams, random_seed=random_seed,
                         docker_containers=docker_containers)

        assert os.path.isfile(os.path.join(BIN_PATH, 'smash')), (
               "invalid smash bin path")
        assert os.path.isfile(os.path.join(BIN_PATH, 'smashmatch')), (
               "invalid smashmatch bin path")
        self._bin_path_smash = os.path.abspath(os.path.join(BIN_PATH, 'smash'))
        self._bin_path_smashmatch = os.path.abspath(os.path.join(BIN_PATH,
                                                                'smashmatch'))
        self._cwd = os.getcwd()
        self._d3m_reader = DatasetLoader()
        self._tmp_dir = ''
        self._partition = None
        self._num_streams = 0
        self._lib_files = {}

        self._channel_dirs = []
        self._channel_partition_map = {}
        self._selected_channels = set()

        self._channel_probabilities = {}
        self._channel_predictions = {}
        self._detrending = False
        self._channels = None

        self._n_clusters = self.hyperparams['n_clusters']
        #if cluster_class is None:
        self._cluster_class = KMeans(n_clusters=self._n_clusters)
        #else:
        #    self._cluster_class = cluster_class

        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        """
        outputs argument should be specified as None
        """
        self._d3m_reader.load_dataset(data=inputs,
                                     train_or_test='train')
        self._tmp_dir, self._channel_dirs, self._num_streams = (
            self._d3m_reader.write_libs(problem_type='unsupervised'))

        self._fitted = False

    def _fit_one_channel(self, directory):
        """

        """
        prune_range, detrending, normalization, partition = quantizer(directory,
                                                                      inplace=True,
                                                                      use_genesess=False,
                                                                      problem_type='unsupervised',
                                                                      num_streams=self._num_streams,)
        self._prune_range = prune_range
        self._detrending = detrending
        self._normalization = normalization

        return partition


    def fit(self, *, timeout: float = None, iterations: int = None) -> CallResult[None]:
        """

        """
        channels = self._channels
        if channels is not None:
            if channels == -1:
                pass
            elif not isinstance(channels, list):
                channels = [channels]
            selected_channels = ['channel_' + str(c) for c in channels]
            self._selected_channels = set(selected_channels)
        elif bool(self._selected_channels):
            selected_channels = self._selected_channels
        else:
            selected_channels = self._channel_dirs

        for channel_dir in selected_channels:
            partition = self._fit_one_channel(channel_dir)
            channel_name = channel_dir.split('/')[-1]
            self._channel_partition_map[channel_name] = partition

        #if verbose:
        #    print('Chosen partition:')
        #    pprint_dict(self._channel_partition_map)

        # run smash to get the distance matrix

        distance_matrices = []
        for channel_dir, partition in self._channel_partition_map.items():
            channel_path = os.path.join(self._tmp_dir, channel_dir)
            input_data = os.path.join(channel_path, 'dataset')
            output_file = os.path.join(channel_path, 'H.dst')
            results = smash(input_data, outfile=output_file)
            distance_matrices.append(results)
        final_dist_matrix = matrix_list_p_norm(distance_matrices, p=2)
        final_dist_matrix_path = os.path.join(self._tmp_dir, 'H_final.dst')
        np.savetxt(final_dist_matrix_path, final_dist_matrix)

        # run clustering algo to get clusters, use these clusters as targets
        # and save the original time series with the targets to form a
        # smashmatch problem
        cluster_assignments = self._cluster_class.fit_predict(final_dist_matrix)
        cluster_assignments = pd.DataFrame(cluster_assignments,
                                           columns=['cluster'])
        for channel_dir in self._channel_dirs:
            dataset_path = os.path.join(channel_dir, 'dataset')
            train_data = pd.read_csv(dataset_path, delimiter=' ', header=None)
            train_data = pd.concat([train_data, cluster_assignments], axis=1)
            train_data.to_csv('test')
            cluster_list = train_data['cluster'].unique().tolist()
            channel_name = channel_dir.split('/')[-1]
            self._lib_files[channel_name] = []
            for i in cluster_list:
                train_data_i = train_data[train_data['cluster']==i].iloc[:, :-1]
                lib_name = os.path.join(channel_dir, 'train_cluster_' + str(i))
                #lib_path = os.path.join(self._tmp_dir, lib_name)
                #for row in train_data_i:
                #    with open(lib_path, 'a') as outfile:
                #        wr = csv.writer(outfile, delimiter=' ',
                #                        quoting=csv.QUOTE_NONE)
                #        wr.writerow(row)
                train_data_i.to_csv(lib_name, sep=' ', header=False,
                                    index=False)
                self._lib_files[channel_name].append(lib_name)

    def produce(self, *, inputs: Inputs, timeout: float = None,
                iterations: int = None) -> CallResult[Outputs]:
        """

        """
        #if partition is not None:
        #    current_partition = partition
        #elif self._channel_partition_map is not None:
        current_partition = self._channel_partition_map
        self._d3m_reader.load_dataset(data=inputs,
                                     train_or_test='test')

        channels = self._channels
        if channels is not None:
            if not isinstance(channels, list):
                channels = [channels]
            if bool(self._selected_channels):
                for channel in channels:
                    if channel not in self._selected_channels:
                        raise ValueError("The partition was not found for this "
                                         "channel. Re-run 'fit()' with this "
                                         "channel included before running "
                                         "'produce()' with this channel.")

        channel_problems = self._d3m_reader.write_test()

        for channel, problem in channel_problems.items():
            if channels is not None:
                channels_ = ['channel_' + str(c) for c in channels]
                if channel not in channels_:
                    #if verbose:
                    print('Excluding', channel, '...')
                    continue
            elif bool(self._selected_channels) and (channel not in
                                                    self._selected_channels):
                #if verbose:
                print('Excluding', channel, '...')
                continue

            #if verbose:
            start = time.time()
            test_file = problem[0]
            quantize_inplace(test_file, current_partition[channel],
                             pruning=self._prune_range,
                             detrending=self._detrending,
                             normalization=self._normalization)

            lib_files = self._lib_files[channel]
            output_prefix = os.path.join(self._tmp_dir, 'test', channel, 'out')
            smashmatch(test_file, lib_files=lib_files,
                       output_prefix=output_prefix)

            out_prob = np.loadtxt(output_prefix + '_prob')
            out_class = np.loadtxt(output_prefix + '_class')

            self._channel_probabilities[channel] = out_prob
            #if verbose:
            print('CHANNEL ' + channel.split('_')[-1] + ' DONE')
            print(out_class)
            end = time.time()
            print('TIME:', end - start, '\n')
        prob_list = list(self._channel_probabilities.values())
        predictions = argmax_prod_matrix_list(prob_list, index_class_map=None)
        return CallResult(predictions)

    #@property
    #def channel_predictions(self):
    #    return self._channel_predictions

    def get_params(self) -> Params:
        '''
        A noop
        '''
        return None

    def set_params(self, *, params: Params) -> None:
        '''
        A noop
        '''
        return None

