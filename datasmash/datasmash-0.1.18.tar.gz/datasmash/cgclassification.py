import time
import os
import subprocess as sp
import numpy as np
import pandas as pd
from typing import Dict
from sklearn.cluster import KMeans
from datasmash.utils import quantize_inplace, quantizer, smash, DatasetLoader, smashmatch
from datasmash.utils import pprint_dict, argmax_prod_matrix_list, genesess_libfile
from datasmash.config import CWD, BIN_PATH

#from d3m_metadata import container, hyperparams, metadata as metadata_module, params, utils
from d3m_metadata import hyperparams, params, metadata as metadata_module, utils
from d3m_metadata import container
from primitive_interfaces.base import CallResult
from primitive_interfaces.supervised_learning import SupervisedLearnerPrimitiveBase


Inputs = container.dataset.Dataset
Outputs = container.numpy.ndarray


class Params(params.Params):
    """
    a no-op
    """
    pass


class Hyperparams(hyperparams.Hyperparams):
    """

    """
    n_clusters = hyperparams.Hyperparameter[int](
        default = 2,
        description = 'Number of clusters per class. '
    )


class CGSmashClassification(SupervisedLearnerPrimitiveBase[Inputs, Outputs,
                                                         Params, Hyperparams]):
    """

    """
    __author__ = "UChicago"
    metadata = metadata_module.PrimitiveMetadata({
        "algorithm_types": ['HIDDEN_MARKOV_MODEL', 'RANDOM_WALK',
                            'VARIABLE_ORDER_MARKOV_MODEL'],
        "name": "datasmash.classification.CGSmashClassification",
        "primitive_family": "TIMESERIES_CLASSIFICATION",
        "python_path": "d3m.primitives.datasmash.CGSmashClassification",
        "source": {'name': 'UChicago'},
        "version": "0.1.18",
        "id": "c052a14f-194a-4dca-ace5-a12ec1e89197",
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
        "keywords": [
            'time',
            'series',
            'data smashing',
            'data-smashing',
            'data_smashing',
            'datasmashing',
            'classification',
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

        assert os.path.isfile(os.path.join(BIN_PATH, 'smashmatch')), "invalid bin path."
        self._bin_path = os.path.abspath(os.path.join(BIN_PATH, 'smashmatch'))
        self._channel_partition_map = {}
        self._cwd = os.getcwd()
        self._d3m_reader = DatasetLoader()
        self._tmp_dir = ''
        self._channel_dirs = []
        self._class_list = []
        self._selected_channels = set()
        self._detrending = False
        self._inplace = True
        self._channel_probabilities = {}
        self._channel_predictions = {}
        self._channels = None
        self._fitted = False
        self._n_clusters = self.hyperparams['n_clusters']

    #@property
    #def selected_channels(self):
    #    return self._selected_channels

    #@selected_channels.setter
    #def selected_channels(self, channels):
    #    if not isinstance(channels, list):
    #        channels_ = [channels]
    #    else:
    #        channels_ = channels
    #    channels_ = ['channel_' + str(c) for c in channels_]
    #    self._selected_channels = set(channels_)

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        """
        outputs argument should be specified as None
        """
        self._d3m_reader.load_dataset(data=inputs,
                                     train_or_test='train')
        self._tmp_dir, self._channel_dirs, self._class_list = (
            self._d3m_reader.write_libs(problem_type='supervised'))
        self._fitted = False

    def _fit_one_channel(self, directory):
        """

        """
        prune_range, detrending, normalization, partition = quantizer(directory,
                                                                      inplace=True,
                                                                      use_genesess=False,
                                                                      problem_type='supervised')
        self._prune_range = prune_range
        self._detrending = detrending
        self._normalization = normalization

        return partition

    def fit(self, *, timeout: float = None, iterations: int = None) -> CallResult[None]:
        """

        """
        if self._fitted:
            return CallResult(None)

        if self._channels is not None:
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
        #    print('Quantizing in place:', self._inplace)
        #    print('Chosen partition:')
        #    pprint_dict(self._channel_partition_map)

        # cluster libs
        self._cluster = True
        self._d3m_reader.cluster_libs(n_clusters=self._n_clusters)

        for channel, lib_file_list in self._d3m_reader.channel_problems.items():
            alphabet_size = len(self._channel_partition_map[channel]) + 1
            print(lib_file_list)
            for lib_file in lib_file_list[1]:
                print(lib_file)
                genesess_libfile(lib_file, alphabet_size, runfile=True)

        self._fitted = True
        return CallResult(None)

    def produce(self, *, inputs: Inputs, timeout: float = None,
                iterations: int = None) -> CallResult[Outputs]:
        """

        """
        partition_check = bool(self._channel_partition_map) or (partition is not None)
        assert partition_check, "partition must be found via 'fit()' or inputted"
        #if partition is not None:
        #    current_partition = partition
        #elif self.channel_partition_map is not None:
        current_partition = self._channel_partition_map
        self._d3m_reader.load_dataset(data=inputs,
                                     train_or_test='test')

        if self._channels is not None:
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

        #smashmatch = [self._bin_path]
        for channel, problem in channel_problems.items():
            if self._channels is not None:
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

            #partition = []
            #dtype = ['-T', 'symbolic']
            #else:
            #    error_msg = ("keyword-only argument 'data_type' must be set if"
            #                 "'inplace' keyword-only argument of 'fit()'"
            #                 "method was set to False")
            #    assert data_type is not None, error_msg
            #    partition = ['-P'] + current_partition[channel]
            #    dtype = ['-T', data_type]
            lib_files = problem[1]
            #file_in = ['-f', test_file, '-F'] + lib_files
            output_prefix = os.path.join(self._tmp_dir, 'test', channel, 'out')
            #file_out = ['-o', output_prefix]
            #constants = dtype + ['-D', 'row']
            #_num_reruns = ['-n', nr]
            #command_list = (smashmatch + file_in + file_out + constants + partition
            #                + _num_reruns)
            print('TESTING')
            smashmatch(test_file, lib_files=lib_files,
                       output_prefix=output_prefix)
            print('TESTING')

            #sp.check_output(command_list)
            out_prob = np.loadtxt(output_prefix + '_prob')

            dist_files = [output_prefix + '_' + lib_file.split('/')[-1] for lib_file
                          in lib_files]
            #distances = []
            #for dist_file in dist_files:
            #    distances.append(np.loadtxt(dist_file))
            #out_class_raw = np.argmin(np.array(distances), axis=0)

            out_class_raw = np.loadtxt(output_prefix + '_class')
            out_class = []

            for i in out_class_raw:
                out_class.append(self._d3m_reader.index_class_map[int(i)])

            self._channel_probabilities[channel] = out_prob
            self._channel_predictions[channel] = out_class
            #if verbose:
            #    print('CHANNEL ' + channel.split('_')[-1] + ' DONE')
            #    print(out_class)
            #    end = time.time()
            #    print('TIME:', end - start, '\n')
        prob_list = list(self._channel_probabilities.values())
        predictions = argmax_prod_matrix_list(prob_list,
                                                index_class_map=self._d3m_reader.index_class_map)

        return CallResult(predictions)

    #@property
    #def channel_predictions(self):
    #    return self._channel_predictions

    def get_params(self) -> Params:
        """
        A noop
        """
        return None

    def set_params(self, *, params: Params) -> None:
        """
        A noop
        """
        return None

#import time
#import os
#import subprocess as sp
#import numpy as np
#import pandas as pd
#from sklearn.cluster import KMeans
#from datasmash.utils import quantize_inplace, quantizer, smash, DatasetLoader
#from datasmash.utils import pprint_dict, argmax_prod_matrix_list, genesess_libfile
#from datasmash.primitive_interfaces.supervised_learning import SupervisedLearnerPrimitiveBase
#from datasmash.config import CWD, BIN_PATH
#
#
#class CGSmashClassification(SupervisedLearnerPrimitiveBase):
#    """
#
#    """
#    def __init__(self, *, bin_path=BIN_PATH):
#        assert os.path.isfile(os.path.join(bin_path, 'smashmatch')), "invalid bin path."
#        self.bin_path = os.path.abspath(os.path.join(bin_path, 'smashmatch'))
#        self.channel_partition_map = {}
#        self.cwd = os.getcwd()
#        self.d3m_reader = DatasetLoader()
#        self.tmp_dir = ''
#        self.channel_dirs = []
#        self.class_list = []
#        self._selected_channels = set()
#        self.detrending = False
#        self.inplace = True
#        self.channel_probabilities = {}
#        self._channel_predictions = {}
#        self.cluster = False
#
#    @property
#    def selected_channels(self):
#        return self._selected_channels
#
#    @selected_channels.setter
#    def selected_channels(self, channels):
#        if not isinstance(channels, list):
#            channels_ = [channels]
#        else:
#            channels_ = channels
#        channels_ = ['channel_' + str(c) for c in channels_]
#        self._selected_channels = set(channels_)
#
#    def set_training_data(self, training_data_dir, *,
#                          dataset_doc_json='datasetDoc.json',
#                          verbose=False, **kwargs):
#        """
#
#        """
#        self.d3m_reader.load_dataset(data_dir=training_data_dir,
#                                     doc_json=dataset_doc_json,
#                                     train_or_test='train',
#                                     verbose=verbose, **kwargs)
#        self.tmp_dir, self.channel_dirs, self.class_list = (
#            self.d3m_reader.write_libs(problem_type='supervised'))
#
#    def _fit_one_channel(self, directory, *, detrending=False, inplace=True,
#                         **kwargs):
#        """
#
#        """
#        self.inplace = inplace
#        prune_range, detrending, normalization, partition = quantizer(directory,
#                                                                      bin_path=BIN_PATH,
#                                                                      problem_type='supervised',
#                                                                      inplace=inplace,
#                                                                      use_genesess=False,
#                                                                      **kwargs)
#        self.prune_range = prune_range
#        self.detrending = detrending
#        self.normalization = normalization
#
#        return partition
#
#    def fit(self, *, verbose=False, channels=None, n_clusters=2,
#            cluster_class=None, gen_epsilon=0.02, num_steps=10000,
#            num_models=1, **kwargs):
#        """
#
#        """
#        if channels is not None:
#            if channels == -1:
#                pass
#            elif not isinstance(channels, list):
#                channels = [channels]
#            selected_channels = ['channel_' + str(c) for c in channels]
#            self._selected_channels = set(selected_channels)
#        elif bool(self._selected_channels):
#            selected_channels = self.selected_channels
#        else:
#            selected_channels = self.channel_dirs
#
#        for channel_dir in selected_channels:
#            partition = self._fit_one_channel(channel_dir, **kwargs)
#            channel_name = channel_dir.split('/')[-1]
#            self.channel_partition_map[channel_name] = partition
#
#        if verbose:
#            print('Quantizing in place:', self.inplace)
#            print('Chosen partition:')
#            pprint_dict(self.channel_partition_map)
#
#        # cluster libs
#        self.cluster = True
#        self.d3m_reader.cluster_libs(n_clusters=n_clusters)
#
#        for channel, lib_file_list in self.d3m_reader.channel_problems.items():
#            alphabet_size = len(self.channel_partition_map[channel]) + 1
#            for lib_file in lib_file_list:
#                genesess_libfile(lib_file, alphabet_size,
#                                 gen_epsilon=gen_epsilon, num_steps=num_steps,
#                                 num_models=num_models, runfile=True)
#
#    def produce(self, test_dir, *,
#                data_type=None,
#                dataset_doc_json='datasetDoc.json',
#                partition=None,
#                num_reruns=50,
#                channels=None,
#                verbose=False):
#        """
#
#        """
#        partition_check = bool(self.channel_partition_map) or (partition is not None)
#        assert partition_check, "partition must be found via 'fit()' or inputted"
#        if partition is not None:
#            current_partition = partition
#        elif self.channel_partition_map is not None:
#            current_partition = self.channel_partition_map
#        self.d3m_reader.load_dataset(data_dir=test_dir,
#                                     doc_json=dataset_doc_json,
#                                     train_or_test='test')
#
#        if channels is not None:
#            if not isinstance(channels, list):
#                channels = [channels]
#            if bool(self._selected_channels):
#                for channel in channels:
#                    if channel not in self._selected_channels:
#                        raise ValueError("The partition was not found for this "
#                                         "channel. Re-run 'fit()' with this "
#                                         "channel included before running "
#                                         "'produce()' with this channel.")
#
#        channel_problems = self.d3m_reader.write_test()
#
#        smashmatch = [self.bin_path]
#        nr = str(num_reruns)
#        for channel, problem in channel_problems.items():
#            if channels is not None:
#                channels_ = ['channel_' + str(c) for c in channels]
#                if channel not in channels_:
#                    if verbose:
#                        print('Excluding', channel, '...')
#                    continue
#            elif bool(self._selected_channels) and (channel not in
#                self._selected_channels):
#                if verbose:
#                    print('Excluding', channel, '...')
#                continue
#
#            if verbose:
#                start = time.time()
#            test_file = problem[0]
#            if self.inplace:
#                quantize_inplace(test_file, current_partition[channel],
#                                 pruning=self.prune_range,
#                                 detrending=self.detrending,
#                                 normalization=self.normalization)
#
#                partition = []
#                dtype = ['-T', 'symbolic']
#            else:
#                error_msg = ("keyword-only argument 'data_type' must be set if"
#                             "'inplace' keyword-only argument of 'fit()'"
#                             "method was set to False")
#                assert data_type is not None, error_msg
#                partition = ['-P'] + current_partition[channel]
#                dtype = ['-T', data_type]
#            lib_files = problem[1]
#            file_in = ['-f', test_file, '-F'] + lib_files
#            output_prefix = os.path.join(self.tmp_dir, 'test', channel, 'out')
#            file_out = ['-o', output_prefix]
#            constants = dtype + ['-D', 'row']
#            _num_reruns = ['-n', nr]
#            command_list = (smashmatch + file_in + file_out + constants + partition
#                            + _num_reruns)
#
#            sp.check_output(command_list)
#            out_prob = np.loadtxt(output_prefix + '_prob')
#
#            dist_files = [output_prefix + '_' + lib_file.split('/')[-1] for lib_file
#                          in lib_files]
#            distances = []
#            for dist_file in dist_files:
#                distances.append(np.loadtxt(dist_file))
#            out_class_raw = np.argmin(np.array(distances), axis=0)
#            print(out_class_raw.shape)
#
#            #out_class_raw = np.loadtxt(output_prefix + '_class')
#            out_class = []
#
#            for i in out_class_raw:
#                out_class.append(self.d3m_reader.index_class_map[int(i)])
#
#            self.channel_probabilities[channel] = out_prob
#            self._channel_predictions[channel] = out_class
#            if verbose:
#                print('CHANNEL ' + channel.split('_')[-1] + ' DONE')
#                print(out_class)
#                end = time.time()
#                print('TIME:', end - start, '\n')
#        prob_list = list(self.channel_probabilities.values())
#        return argmax_prod_matrix_list(prob_list,
#                                       index_class_map=self.d3m_reader.index_class_map)
#
#    @property
#    def channel_predictions(self):
#        return self._channel_predictions
#
#
#    def get_params(self):
#        """
#        A noop
#        """
#        return None
#
#    def set_params(self):
#        """
#        A noop
#        """
#        return None
#
