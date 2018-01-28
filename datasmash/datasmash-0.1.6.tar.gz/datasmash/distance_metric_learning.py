import os
import subprocess as sp
import numpy as np
from datasmash.utils import quantizer, DatasetLoader
from datasmash.utils import pprint_dict, matrix_list_p_norm
from datasmash.primitive_interfaces.transformer import TransformerPrimitiveBase
from datasmash.config import BIN_PATH


class SmashDistanceMetricLearning(TransformerPrimitiveBase):
    """

    """
    def __init__(self, *, bin_path=BIN_PATH, preproc=quantizer):
        assert os.path.isfile(os.path.join(bin_path, 'smash')), "Error: invalid bin path."
        self.bin_path = os.path.abspath(os.path.join(bin_path, 'smash'))
        self.preproc = preproc
        self.cwd = os.getcwd()
        self.d3m_reader = DatasetLoader()
        self.tmp_dir = ''
        self.channel_dirs = []
        self.num_streams = 0
        self.partition = None
        self._selected_channels = set()
        self.channel_partition_map = {}

    def set_training_data(self, data_dir, *,
                          dataset_doc_json='datasetDoc.json', verbose=False,
                          **kwargs):
        """

        """
        self.d3m_reader.load_dataset(data_dir=data_dir,
                                     doc_json=dataset_doc_json,
                                     train_or_test='train', verbose=verbose,
                                     **kwargs)
        self.tmp_dir, self.channel_dirs, self.num_streams = self.d3m_reader.write_libs(problem_type='unsupervised')

    def _fit_one_channel(self, directory, *, detrending=False, **kwargs):
        """

        """
        self.detrending = detrending
        partition = quantizer(directory,
                              bin_path=BIN_PATH,
                              problem_type='unsupervised',
                              num_streams=self.num_streams,
                              detrending=detrending,
                              **kwargs)
        return partition

    def produce(self, *, data_type, num_reruns=50, partition=None, verbose=False,
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
            selected_channels = self.selected_channels
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
        smash = [self.bin_path]
        constants = ['-T', data_type, '-D', 'row']

        distance_matrices = []
        nr = str(num_reruns)
        for channel_dir, partition in self.channel_partition_map.items():
            channel_path = os.path.join(self.tmp_dir, channel_dir)
            input_data = os.path.join(channel_path, 'dataset')
            output_file = os.path.join(channel_path, 'H.dst')
            file_io = ['-f', input_data, '-o', output_file]
            partition = ['-p'] + partition
            _num_reruns = ['-n', nr]
            detrending = ['-u', str(int(self.detrending))]

            command_list = (smash + file_io + constants + partition +
                            _num_reruns + detrending)
            sp.check_output(command_list)
            results = np.loadtxt(output_file, dtype=float)
            results += results.T
            distance_matrices.append(results)
        final_dist_matrix = matrix_list_p_norm(distance_matrices, p=p)
        return final_dist_matrix

