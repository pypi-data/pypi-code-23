import time
import os
import numpy as np
import subprocess as sp
from typing import Dict
from sklearn.ensemble import RandomForestClassifier
from datasmash.utils import quantize_inplace, quantizer, genesess, DatasetLoader
from datasmash.utils import pprint_dict, argmax_prod_matrix_list, line_by_line
from datasmash.config import CWD, BIN_PATH

from d3m_metadata import container, hyperparams, metadata as metadata_module, params, utils
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
    a no-op
    """
    depth = hyperparams.UniformInt(
        default = 1000,
        lower = 100,
        upper = 10000,
        description = 'Exponentiated tree depth in inferred Markov Model. '
    )


class XG2(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):
    """

    """
    __author__ = "UChicago"
    metadata = metadata_module.PrimitiveMetadata({
        "algorithm_types": ['HIDDEN_MARKOV_MODEL', 'RANDOM_WALK',
                            'VARIABLE_ORDER_MARKOV_MODEL'],
        "name": "datasmash.classification.XG2",
        "primitive_family": "TIMESERIES_CLASSIFICATION",
        "python_path": "d3m.primitives.datasmash.XG2",
        "source": {'name': 'UChicago'},
        "version": "0.1.9",
        "id": "d989655c-a583-4bc3-94bc-cdd7b3ccb3aa",
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
             'version': '0.1.9'
            }
        ]
    })


    def __init__(self, *,
                 hyperparams: Hyperparams,
                 random_seed: int = 0,
                 docker_containers: Dict[str, str] = None,
                 _verbose: int = 0) -> None:

        super().__init__(hyperparams=hyperparams, random_seed=random_seed,
                         docker_containers=docker_containers)

        assert os.path.isfile(os.path.join(BIN_PATH, 'genESeSS')), "invalid bin path."
        self._bin_path = BIN_PATH
        self._channel_partition_map = {}
        self._cwd = os.getcwd()
        self._d3m_reader = DatasetLoader()
        self._tmp_dir = ''
        self._channel_dirs = []
        self._selected_channels = set()
        self._detrending = False
        self._inplace = True
        self._channel_probabilities = {}
        self._channel_predictions = {}
        self._fitted = False
        self._depth = self.hyperparams['depth']
        self._channels = None

        #if classifier is not None:
        #    self._classifier = classifier
        #else:
        self._classifier = RandomForestClassifier(n_estimators=500,
                                                 max_depth=None,
                                                 min_samples_split=2,
                                                 random_state=random_seed,
                                                 class_weight='balanced')

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

        """
        self._d3m_reader.load_dataset(data=inputs,
                                     train_or_test='train')
        self._tmp_dir, self._channel_dirs, _ = (
            self._d3m_reader.write_libs(problem_type='supervised'))
        self._fitted = False

    def _fit_one_channel(self, directory):
        """

        """
        #self.gen_epsilon = gen_epsilon
        #self.num_steps = num_steps
        #self.num_models = num_models
        #self.depth = depth
        #self.detrending = detrending
        #self.inplace = inplace
        lib_files = []
        prune_range, detrending, normalization, partition = quantizer(directory,
                                                                      bin_path=BIN_PATH,
                                                                      problem_type='supervised',
                                                                      use_genesess=False)
        self._prune_range = prune_range
        self._detrending = detrending
        self._normalization = normalization

        print('Chosen partition:')
        print(partition)

        for lib_file in os.listdir(directory):
            if (lib_file != 'library_list') and (not os.path.isdir(lib_file)):
                lib_path = os.path.join(directory, lib_file)
                new_lib_file = line_by_line(lib_path, function=genesess,
                                            depth=self._depth)
                print(new_lib_file)
                class_ = int(lib_file.split('_')[-1])
                print(class_)
                lib_files.append((new_lib_file, class_))
        print(lib_files)
        return partition, lib_files

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
            partition, lib_files = self._fit_one_channel(channel_dir)
            channel_name = channel_dir.split('/')[-1]
            self._channel_partition_map[channel_name] = partition

        #if verbose:
        #    print('Quantizing in place:', self.inplace)
        #    print('Chosen partition:')
        #    pprint_dict(self._channel_partition_map)

        X = []
        y = []
        for lib_file, class_ in lib_files:
            X_ = np.loadtxt(lib_file, dtype=float)
            y_ = class_ * np.ones(X_.shape[0])

            X.append(X_)
            y.append(y_)
        X = np.array([example for class_set in X for example in class_set])
        y = np.array([example for class_set in y for example in class_set])
        print(y)
        print(X.shape, y.shape)
        self._classifier.fit(X, y)

        self._fitted = True
        return CallResult(None)

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

            test_features = line_by_line(test_file, function=genesess,
                                         depth=self._depth)

            X = np.loadtxt(test_features)
            print(X.shape)
            probabilities = self._classifier.predict_proba(X)
            predictions = self._classifier.predict(X)
            self._channel_probabilities[channel] = probabilities
            self._channel_predictions[channel] = predictions
            print(predictions)

            #if verbose:
            print('CHANNEL ' + channel.split('_')[-1] + ' DONE')
            print(predictions)
            end = time.time()
            print('TIME:', end - start, '\n')
        prob_list = list(self._channel_probabilities.values())
        overall_predictions = argmax_prod_matrix_list(prob_list,
                                                      index_class_map=self._d3m_reader.index_class_map)
        return CallResult(overall_predictions)

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

