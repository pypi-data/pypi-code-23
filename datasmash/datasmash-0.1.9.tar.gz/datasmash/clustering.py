import os
import csv
import time
import subprocess as sp
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from datasmash.primitive_interfaces.clustering import ClusteringPrimitiveBase
from datasmash.utils import quantizer, DatasetLoader, pprint_dict, quantize_inplace
from datasmash.utils import matrix_list_p_norm, argmax_prod_matrix_list
from datasmash.config import CWD, BIN_PATH


class SmashClustering(ClusteringPrimitiveBase):
    """

    """
    def __init__(self, *, bin_path=BIN_PATH,
                 cluster_class=None, n_clusters=2):
        assert os.path.isfile(os.path.join(bin_path, 'smash')), (
               "invalid smash bin path")
        assert os.path.isfile(os.path.join(bin_path, 'smashmatch')), (
               "invalid smashmatch bin path")
        self.bin_path_smash = os.path.abspath(os.path.join(bin_path, 'smash'))
        self.bin_path_smashmatch = os.path.abspath(os.path.join(bin_path,
                                                                'smashmatch'))
        self.cwd = os.getcwd()
        self.d3m_reader = DatasetLoader()
        self.tmp_dir = ''
        self.partition = None
        self.num_streams = 0
        self.lib_files = {}

        self.n_clusters = n_clusters
        if cluster_class is None:
            self.cluster_class = KMeans(n_clusters=self.n_clusters)
        else:
            self.cluster_class = cluster_class

        self.channel_dirs = []
        self.channel_partition_map = {}
        self._selected_channels = set()

        self.channel_probabilities = {}
        self._channel_predictions = {}

        self.detrending = False

    def set_training_data(self, training_data_dir, *,
                          dataset_doc_json='datasetDoc.json',
                          verbose=False, **kwargs):
        """

        """
        self.d3m_reader.load_dataset(data_dir=training_data_dir,
                                     doc_json=dataset_doc_json,
                                     train_or_test='train', verbose=verbose,
                                     **kwargs)
        self.tmp_dir, self.channel_dirs, self.num_streams = (
            self.d3m_reader.write_libs(problem_type='unsupervised'))

    def _fit_one_channel(self, directory, *, detrending=False, inplace=True, **kwargs):
        """

        """
        self.inplace = inplace
        self.detrending = detrending
        prune_range, detrending, normalization, partition = quantizer(directory,
                                                                      bin_path=BIN_PATH,
                                                                      problem_type='unsupervised',
                                                                      num_streams=self.num_streams,
                                                                      detrending=detrending,
                                                                      inplace=inplace,
                                                                      **kwargs)
        self.prune_range = prune_range
        self.detrending = detrending
        self.normalization = normalization

        return partition

    def fit(self, *, data_type, num_reruns=50, partition=None, verbose=False,
            channels=None, p=2, **kwargs):
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
            selected_channels = self._selected_channels
        else:
            selected_channels = self.channel_dirs

        for channel_dir in selected_channels:
            partition = self._fit_one_channel(channel_dir, **kwargs)
            channel_name = channel_dir.split('/')[-1]
            self.channel_partition_map[channel_name] = partition

        if verbose:
            print('Chosen partition:')
            pprint_dict(self.channel_partition_map)

        # run smash to get the distance matrix
        smash = [self.bin_path_smash]
        constants = ['-D', 'row']
        if self.inplace:
            constants.append(['-T', data_type])
        else:
            constants.append(['-T', 'symbolic'])

        distance_matrices = []
        nr = str(num_reruns)
        for channel_dir, partition in self.channel_partition_map.items():
            channel_path = os.path.join(self.tmp_dir, channel_dir)
            input_data = os.path.join(channel_path, 'dataset')
            output_file = os.path.join(channel_path, 'H.dst')
            file_io = ['-f', input_data, '-o', output_file]
            if self.inplace:
                partition = []
                detrending = []
            else:
                partition = ['-p'] + partition
                detrending = ['-u', str(int(self.detrending))]
            _num_reruns = ['-n', nr]
            command_list = (smash + file_io + constants + partition +
                            _num_reruns + detrending)
            sp.check_output(command_list)
            results = np.loadtxt(output_file, dtype=float)
            results += results.T
            distance_matrices.append(results)
        final_dist_matrix = matrix_list_p_norm(distance_matrices, p=p)
        final_dist_matrix_path = os.path.join(self.tmp_dir, 'H_final.dst')
        np.savetxt(final_dist_matrix_path, final_dist_matrix)

        # run clustering algo to get clusters, use these clusters as targets
        # and save the original time series with the targets to form a
        # smashmatch problem
        cluster_assignments = self.cluster_class.fit_predict(final_dist_matrix)
        cluster_assignments = pd.DataFrame(cluster_assignments,
                                           columns=['cluster'])
        for channel_dir in self.channel_dirs:
            dataset_path = os.path.join(self.tmp_dir, channel_dir, 'dataset')
            train_data = pd.read_csv(dataset_path, delimiter=' ', header=None)
            train_data = pd.concat([train_data, cluster_assignments], axis=1)
            train_data.to_csv('test')
            cluster_list = train_data['cluster'].unique().tolist()
            self.lib_files[channel_dir] = []
            for i in cluster_list:
                train_data_i = train_data[train_data['cluster']==i].iloc[:, :-1]
                lib_name = os.path.join(channel_dir, 'train_cluster_' + str(i))
                lib_path = os.path.join(self.tmp_dir, lib_name)
                #for row in train_data_i:
                #    with open(lib_path, 'a') as outfile:
                #        wr = csv.writer(outfile, delimiter=' ',
                #                        quoting=csv.QUOTE_NONE)
                #        wr.writerow(row)
                train_data_i.to_csv(lib_path, sep=' ', header=False,
                                    index=False)
                self.lib_files[channel_dir].append(lib_path)

    def produce_(self, test_dir, *, data_type, dataset_doc_json='datasetDoc.json',
                partition=None, num_reruns=100):
        """

        """
        check = (self.partition is not None) or (partition is not None)
        assert check, "partition must be found via 'fit()' or inputted"
        if partition is not None:
            current_partition = partition
        elif self.partition is not None:
            current_partition = self.partition

        # load test data in smashmatch format and save to temporary directory
        self.d3m_reader.load_dataset(data_dir=test_dir,
                                     doc_json=dataset_doc_json,
                                     train_or_test='test')
        test_file = self.d3m_reader.write_test()

        constants = ['-D', 'row']
        if self.inplace:
            quantize_inplace(test_file, current_partition,
                             pruning=self.prune_range,
                             detrending=self.detrending,
                             normalization=self.normalization)
            partition = []
            dtype = ['-T', 'symbolic']
        else:
            partition = ['-P'] + current_partition
            dtype = ['-T', data_type]

        smashmatch = [self.bin_path_smashmatch]
        file_in = ['-f', test_file, '-F'] + self.lib_files
        output_prefix = os.path.join(self.tmp_dir, 'out')
        file_out = ['-o', output_prefix]
        constants = ['-T', data_type, '-D', 'row']
        num_reruns = ['-n', str(num_reruns)]
        command_list = smashmatch + file_in + file_out + constants + dtype + partition

        sp.check_output(command_list)
        out_class = os.path.join(self.tmp_dir, 'out_class')
        return np.loadtxt(out_class)

    def produce(self, test_dir, *,
                data_type,
                dataset_doc_json='datasetDoc.json',
                partition=None,
                num_reruns=100,
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

        smashmatch = [self.bin_path_smashmatch]
        nr = str(num_reruns)
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
            lib_files = self.lib_files[channel]
            file_in = ['-f', test_file, '-F'] + lib_files
            output_prefix = os.path.join(self.tmp_dir, 'test', channel, 'out')
            file_out = ['-o', output_prefix]
            constants = ['-T', data_type, '-D', 'row']
            partition = ['-P'] + current_partition[channel]
            num_reruns = ['-n', nr]
            command_list = (smashmatch + file_in + file_out + constants + partition
                           + num_reruns)

            sp.check_output(command_list)
            out_prob = np.loadtxt(output_prefix + '_prob')
            out_class = np.loadtxt(output_prefix + '_class')
            self.channel_probabilities[channel] = out_prob
            if verbose:
                print('CHANNEL ' + channel.split('_')[-1] + ' DONE')
                print(out_class)
                end = time.time()
                print('TIME:', end - start, '\n')
        prob_list = list(self.channel_probabilities.values())
        return argmax_prod_matrix_list(prob_list)

    @property
    def channel_predictions(self):
        return self._channel_predictions

    def get_params(self):
        '''
        A noop
        '''
        return None

    def set_params(self):
        '''
        A noop
        '''
        return None

