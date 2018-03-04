import os
import sys
import json
import pickle
import numpy as np
from .utils import ClusterManager
from .features import WeedLexicon
from .map_maker import MapMakerManager
from .weedata import Weedataset, create_dataset_from_pickle


class WeedMaster:

    def __init__(self, datasets_dir=None, graphs_dir=None):
        self.datasets_dir = datasets_dir
        if datasets_dir is None:
            self.datasets_dir = './'
        if graphs_dir is None:
            graphs_dir = './'
        self.id2dataset = {}
        self.selected_dt_id = None
        self.map_manager = MapMakerManager(self, graphs_dir)
        self.cluster_manager = ClusterManager(self)
        self.lexicon = WeedLexicon()

    @property
    def dt(self):
        """
        Returns the currently selected/active dataset as a reference to a Weedataset object.\n
        :return: the reference to the dataset
        :rtype: .weedata.Weedataset
        """
        return self.id2dataset[self.selected_dt_id]

    @property
    def som(self):
        """
        Returns the currently selected/active som instance, as a reference to a som object.\n
        :return: the reference to the self-organizing map
        :rtype: somoclu.Somoclu
        """
        return self.map_manager.som

    def get_feature_vectors(self, weedataset, list_of_variables=None):
        """
        This method must be called
        :param weedataset:
        :param list_of_variables:
        :return:
        """
        if not list_of_variables:
            return weedataset.load_feature_vectors()
        else:
            weedataset.use_variables(list_of_variables)
            return weedataset.load_feature_vectors()

    def create_weedataset(self, jl_file, dataset_id, ffilter=''):
        data_set = Weedataset(dataset_id)
        with open(jl_file, 'r') as json_lines_file:
            for line in json_lines_file:
                strain_dict = json.loads(line)
                if ffilter.split(':')[0] in strain_dict:
                    if strain_dict[ffilter.split(':')[0]] == ffilter.split(':')[1]:
                        data_set.add(strain_dict)
                        if 'description' in strain_dict:
                            self.lexicon.munch(strain_dict['description'])
                else:
                    data_set.add(strain_dict)
                    if 'description' in strain_dict:
                        self.lexicon.munch(strain_dict['description'])
        data_set.load_feature_indexes()
        self.id2dataset[dataset_id] = data_set
        self.selected_dt_id = dataset_id
        return data_set

    # def load_dataset_old(self, a_file):
    #     with open(a_file, 'rb') as pickle_file:
    #         weedataset = pickle.load(pickle_file)
    #         assert isinstance(weedataset, Weedataset)
    #     self.id2dataset[weedataset.name] = weedataset
    #     self.selected_dt_id = weedataset.name
    #     print("Loaded dataset with id '{}'".format(weedataset.name))
    #     return weedataset

    def load_dataset(self, a_file):
        weedataset = create_dataset_from_pickle(self.datasets_dir + '/' + a_file)
        self.id2dataset[weedataset.name] = weedataset
        self.selected_dt_id = weedataset.name
        print("Loaded dataset with id '{}'".format(weedataset.name))
        return weedataset

    def save_dataset(self, weedataset_id):
        dataset = self.id2dataset[weedataset_id]
        if dataset.has_missing_values():
            name = '-not-clean'
        else:
            name = '-clean'
        name = self.datasets_dir + '/' + dataset.name + name + '.pk'
        try:
            with open(name, 'wb') as pickled_dataset:
                pickle.dump(dataset, pickled_dataset, protocol=pickle.HIGHEST_PROTOCOL)
            print("Saved dataset with id '{}' as '{}'".format(weedataset_id, name))
        except RuntimeError as e:
            print(e)
            print("Failed to save dataset wtih id '{}'".format(weedataset_id))

    def __getitem__(self, wd_id):
        self.selected_dt_id = wd_id
        return self
