import os
import subprocess as sp
import numpy as np
from typing import Dict
from datasmash.utils import (quantizer, DatasetLoader, pprint_dict,
                             matrix_list_p_norm, smash)
from datasmash.config import BIN_PATH
from sklearn.manifold import MDS

from d3m_metadata import container, hyperparams, metadata as metadata_module, params, utils
from primitive_interfaces.base import CallResult
from primitive_interfaces.transformer import TransformerPrimitiveBase


Inputs = container.dataset.Dataset
Outputs = container.numpy.matrix


class Params(params.Params):
    pass


class Hyperparams(hyperparams.Hyperparams):
    n_components = hyperparams.Hyperparameter[int](
        default = 2,
        description = 'Number of features to create from each time series. '
    )


class SmashFeaturization(TransformerPrimitiveBase[Inputs, Outputs, Hyperparams]):
    """

    """
    __author__ = "UChicago"
    metadata = metadata_module.PrimitiveMetadata({
        "algorithm_types": ['HIDDEN_MARKOV_MODEL', 'RANDOM_WALK',
                            'VARIABLE_ORDER_MARKOV_MODEL'],
        "name": "datasmash.classification.SmashFeaturization",
        "primitive_family": "FEATURE_CONSTRUCTION",
        "python_path": "d3m.primitives.datasmash.SmashFeaturization",
        "source": {'name': 'UChicago'},
        "version": "0.1.18",
        "id": "42ac4412-1194-475f-beb6-d982a347c862",
        'installation': [
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
            "n_components"
        ],
        "keywords": [
            'time',
            'series',
            'data smashing',
            'data-smashing',
            'data_smashing',
            'datasmashing',
            'feature construction',
            'embed'
            'embedding',
            'featurization',
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

        assert os.path.isfile(os.path.join(BIN_PATH, 'smash')), "Error: invalid bin path."
        self._bin_path = os.path.abspath(os.path.join(BIN_PATH, 'smash'))
        self._cwd = os.getcwd()
        self._d3m_reader = DatasetLoader()
        self._tmp_dir = ''
        self._channel_dirs = []
        self._channel_partition_map = {}
        self._selected_channels = set()
        self._num_streams = 0
        self._embed_class = MDS(n_components=2, dissimilarity='precomputed')

        self._channels = None

    def _fit_one_channel(self, directory):
        """

        """
        _, _, _, partition = quantizer(directory,
                                       inplace=True,
                                       use_genesess=False,
                                       problem_type='unsupervised',
                                       num_streams=self._num_streams)
        return partition

    def produce(self, *, inputs: Inputs, timeout: float = None,
                iterations: int = None) -> CallResult[Outputs]:
        """

        """
        self._d3m_reader.load_dataset(data=inputs,
                                     train_or_test='train')
        self._tmp_dir, self._channel_dirs, self._num_streams = self._d3m_reader.write_libs(problem_type='unsupervised')

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
        print('Chosen partition:')
        pprint_dict(self._channel_partition_map)

        # run smash to get the distance matrix

        distance_matrices = []
        for channel_dir, partition in self._channel_partition_map.items():
            channel_path = os.path.join(self._tmp_dir, channel_dir)
            input_data = os.path.join(channel_path, 'dataset')
            output_file = os.path.join(channel_path, 'H.dst')
            results = smash(input_data, outfile=output_file)
            distance_matrices.append(results)

        final_dist_matrix = matrix_list_p_norm(distance_matrices, p=2)
        feature_vector = self._embed_class.fit_transform(results)
        return CallResult(feature_vector)

