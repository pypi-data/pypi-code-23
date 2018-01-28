import time
import os
import numpy as np
import subprocess as sp
from sklearn.ensemble import RandomForestClassifier
from datasmash.utils import quantize_inplace, quantizer, xgenesess, DatasetLoader
from datasmash.utils import pprint_dict, argmax_prod_matrix_list, line_by_line
from datasmash.primitive_interfaces.supervised_learning import SupervisedLearnerPrimitiveBase
from datasmash.config import CWD, BIN_PATH


class XG1(SupervisedLearnerPrimitiveBase):
    """

    """
    def __init__(self, *, bin_path=BIN_PATH, classifier=None, ):
        assert os.path.isfile(os.path.join(bin_path, 'XgenESeSS')), "invalid bin path."
        self.bin_path = bin_path
        self.channel_partition_map = {}
        self.cwd = os.getcwd()
        self.d3m_reader = DatasetLoader()
        self.tmp_dir = ''
        self.channel_dirs = []
        self._selected_channels = set()
        self.detrending = False
        self.inplace = True
        self.channel_probabilities = {}
        self._channel_predictions = {}

        if classifier is not None:
            self.classifier = classifier
        else:
            self.classifier = RandomForestClassifier(n_estimators=500,
                                                     max_depth=None,
                                                     min_samples_split=2,
                                                     random_state=0,
                                                     class_weight='balanced')

    @property
    def selected_channels(self):
        return self._selected_channels

    @selected_channels.setter
    def selected_channels(self, channels):
        if not isinstance(channels, list):
            channels_ = [channels]
        else:
            channels_ = channels
        channels_ = ['channel_' + str(c) for c in channels_]
        self._selected_channels = set(channels_)

    def set_training_data(self, training_data_dir, *,
                          dataset_doc_json='datasetDoc.json',
                          verbose=False, **kwargs):
        """

        """
        self.d3m_reader.load_dataset(data_dir=training_data_dir,
                                     doc_json=dataset_doc_json,
                                     train_or_test='train',
                                     verbose=verbose, **kwargs)
        self.tmp_dir, self.channel_dirs, _ = (
            self.d3m_reader.write_libs(problem_type='supervised'))

    def _fit_one_channel(self, directory, *, inplace=True,
                         min_delay=0, max_delay=30, **kwargs):
        """

        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.inplace = inplace
        lib_files = []
        prune_range, detrending, normalization, partition = quantizer(directory,
                                                                      bin_path=BIN_PATH,
                                                                      problem_type='supervised',
                                                                      inplace=inplace,
                                                                      **kwargs)
        self.prune_range = prune_range
        self.detrending = detrending
        self.normalization = normalization

        print('Chosen partition:')
        print(partition)

        for lib_file in os.listdir(directory):
            if (lib_file != 'library_list') and (not os.path.isdir(lib_file)):
                lib_path = os.path.join(directory, lib_file)
                new_lib_file = line_by_line(lib_path, function=xgenesess,
                                            min_delay=min_delay, max_delay=max_delay)
                class_ = int(lib_file.split('_')[-1])
                lib_files.append((new_lib_file, class_))
        return partition, lib_files

    def fit(self, *, verbose=False, channels=None, **kwargs):
        """

        """
        if channels is not None:
            if channels == -1:
                pass
            elif not isinstance(channels, list):
                channels = [channels]
            selected_channels = ['channel_' + str(c) for c in channels]
            self._selected_channels = set(selected_channels)
        elif bool(self._selected_channels):
            selected_channels = self.selected_channels
        else:
            selected_channels = self.channel_dirs

        for channel_dir in selected_channels:
            partition, lib_files = self._fit_one_channel(channel_dir, **kwargs)
            channel_name = channel_dir.split('/')[-1]
            self.channel_partition_map[channel_name] = partition

        if verbose:
            print('Quantizing in place:', self.inplace)
            print('Chosen partition:')
            pprint_dict(self.channel_partition_map)

        X = []
        y = []
        for lib_file, class_ in lib_files:
            X_ = np.loadtxt(lib_file, dtype=float)
            y_ = class_ * np.ones(X_.shape[0])

            X.append(X_)
            y.append(y_)
        X = np.array([example for class_set in X for example in class_set])
        y = np.array([example for class_set in y for example in class_set])
        print(X.shape, y.shape)
        self.classifier.fit(X, y)

    def produce(self, test_dir, *,
                dataset_doc_json='datasetDoc.json',
                partition=None,
                channels=None,
                verbose=False):
        """

        """
        partition_check = bool(self.channel_partition_map) or (partition is not None)
        assert partition_check, "partition must be found via 'fit()' or inputted"
        if partition is not None:
            current_partition = partition
        elif self.channel_partition_map is not None:
            current_partition = self.channel_partition_map
        self.d3m_reader.load_dataset(data_dir=test_dir,
                                     doc_json=dataset_doc_json,
                                     train_or_test='test')

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

        channel_problems = self.d3m_reader.write_test()

        for channel, problem in channel_problems.items():
            if channels is not None:
                channels_ = ['channel_' + str(c) for c in channels]
                if channel not in channels_:
                    if verbose:
                        print('Excluding', channel, '...')
                    continue
            elif bool(self._selected_channels) and (channel not in
                                                    self._selected_channels):
                if verbose:
                    print('Excluding', channel, '...')
                continue

            if verbose:
                start = time.time()
            test_file = problem[0]


            if self.inplace:
                quantize_inplace(test_file, current_partition[channel],
                                 pruning=self.prune_range,
                                 detrending=self.detrending,
                                 normalization=self.normalization)

            test_features = line_by_line(test_file, function=xgenesess,
                                         min_delay=self.min_delay,
                                         max_delay=self.max_delay)

            X = np.loadtxt(test_features)
            print(X.shape)
            probabilities = self.classifier.predict_proba(X)
            predictions = self.classifier.predict(X)
            self.channel_probabilities[channel] = probabilities
            self._channel_predictions[channel] = predictions

            if verbose:
                print('CHANNEL ' + channel.split('_')[-1] + ' DONE')
                print(predictions)
                end = time.time()
                print('TIME:', end - start, '\n')
        prob_list = list(self.channel_probabilities.values())
        return argmax_prod_matrix_list(prob_list,
                                       index_class_map=self.d3m_reader.index_class_map)

    @property
    def channel_predictions(self):
        return self._channel_predictions


    def get_params(self):
        """
        A noop
        """
        return None

    def set_params(self):
        """
        A noop
        """
        return None

