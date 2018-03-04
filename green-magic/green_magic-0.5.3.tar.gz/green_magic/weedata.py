import sys
import json
import pickle
from collections import Counter
from collections import OrderedDict as od
from .features import FeatureComputer
from .utils import extract_value, empty_field

attributes = ('effects', 'medical', 'negatives')
grow_info = ('difficulty', 'height', 'yield', 'flowering', 'stretch')
data_variables = tuple(['type'] + list(attributes) + ['flavors'] + list(grow_info))


class Weedataset:

    def __str__(self):
        incomplete = self.get_nb_missing('any')
        b = 'Strains dataset: {}\n Active variables: [{}]\n'.format(self.name, ', '.join(_ for _ in self.generate_variables()))
        b += 'Total datapoints: {},'.format(len(self.data))
        try:
            s = 0
            b += ' with encoded vector length: {}\n'.format(len(self.datapoints[0]))
            for var in self.generate_variables():
                b += ' {}: {} +'.format(var[:5], str(self.get_nb_values(var)))
                s += self.get_nb_values(var)
            b = b[:-1] + '= {}\n'.format(s)
        except IndexError:
            print("Feature space dim has not been established yet. Please call 'self.load_feature_vectors()' before printing the dataset")
        b += ' incomplete datapoints: {}\n'.format(incomplete)
        if incomplete != 0:
            b += '\n'.join('  empty \'' + var + '\' vals: ' + str(self.get_nb_missing(var)) for var in self.generate_variables())
        return b

    def __init__(self, a_name):
        self.name = a_name
        self.active_variables = set()
        self.data = []
        self.datapoints = []
        self.datapoint_index2_id = {}
        self.id2datapoint = {}
        self.id2strain = od()
        self.field2id = dict(zip(data_variables, ({} for _ in data_variables)))  # i.e. field2id['flavors']['mango']
        self.id2field = dict(zip(data_variables, ({} for _ in data_variables)))  # i.e. id2field['flavors'][0]
        self.value_sets = dict(zip(data_variables, (set() for _ in data_variables)))
        self.stats = od.fromkeys(data_variables, Counter())
        self.is_complete = None
        self.feature_computer = None

    def __getitem__(self, item):
        return self.data[item]

    def __len__(self):
        return len(self.data)

    def add(self, item):
        self.id2strain[str(item['_id'])] = item
        self.value_sets['type'].add(str(item['type']))
        if 'flavors' in item:
            for fl in item['flavors']:
                self.value_sets['flavors'].add(str(fl))
                self.stats['flavors'][str(fl)] += 1
        else:
            item['flavors'] = []
        for attr in attributes:
            for key in item[attr].keys():
                self.value_sets[attr].add(str(key))
                self.stats[attr][str(key)] += item[attr][key]
        for gr_inf in grow_info:
            if gr_inf in item['grow_info']:
                self.value_sets[gr_inf].add(str(item['grow_info'][gr_inf]))
                self.stats[gr_inf][str(item['grow_info'][gr_inf])] += 1
            else:
                item['grow_info'][gr_inf] = ''
        self.data.append(item)
        self.is_complete = None

    def load_feature_vectors(self):
        self.feature_computer = FeatureComputer(self)
        self.datapoints = []
        self.datapoint_index2_id = {}
        self.id2datapoint = {}
        for strain in self.data:
            datapoint = self.feature_computer.get_basic_feature_representation(strain)
            self.datapoints.append(datapoint)
            self.datapoint_index2_id[len(self.datapoints) - 1] = strain['_id']
            self.id2datapoint[strain['_id']] = datapoint
        return self.datapoints

    def load_feature_indexes(self):
        self.field2id = dict(zip(data_variables, (dict(zip(get_generator(self.value_sets[var]), (num_id for num_id in range(len(self.value_sets[var]))))) for var in data_variables)))
        self.id2field = dict(zip(data_variables, ({v: k for k, v in self.field2id[var].items()} for var in data_variables)))

    def get_nb_values(self, variable):
        """
        Returns the number of distinct and discrete values a data variable can "take". Eg get_nb_values('type') == 3 because set('indica', 'hybrid', 'sativa')
         and also get_nb_values('negative') == 6 despite 'negative' variables hold real numbers\n
        :param variable: the variable name of interest
        :type variable: str
        :return: the number of distinct values
        :rtype: int
        """
        return len(self.value_sets[variable])

    def get(self, _id):
        if _id not in self.id2strain:
            return None
        return self.id2strain[_id]

    def use_variables(self, list_of_variables):
        self.active_variables = set()
        for var in list_of_variables:
            if var in data_variables:
                self.active_variables.add(var)

    def ommit_variables(self, list_of_variables):
        self.active_variables -= set(list_of_variables)

    def add_variables(self, list_of_variables):
        for var in list_of_variables:
            if var in data_variables:
                self.active_variables.add(var)

    def clean(self):
        indexes_to_delete = []
        for index, strain in enumerate(self.data):
            if not self.is_full(strain):
                indexes_to_delete.append(index)
        for ind in sorted(indexes_to_delete, reverse=True):
            del self.data[ind]
        assert self.get_nb_missing('any') == 0

    def get_nb_missing(self, field):
        if field == 'any':
            missing = 0
            for ii in self.data:
                if not self.is_full(ii):
                    missing += 1
            if missing == 0:
                self.is_complete = True
            else:
                self.is_complete = False
        else:
            missing = sum(empty_field(strain, field) for strain in self.data)
            if missing != 0:
                self.is_complete = False
        return missing

    def get_missing_fields(self, strain):
        missing_fields = []
        for var in self.generate_variables():
            if empty_field(strain, var):
                missing_fields.append(var)
        return missing_fields

    def is_full(self, strain):
        for var in self.generate_variables():
            if empty_field(strain, var):
                return False
        return True

    def has_missing_values(self):
        if self.is_complete is not None:
            return not self.is_complete
        return self.get_nb_missing('any') != 0

    def generate_var_value_pairs(self, strain):
        for var in data_variables:
            if var in self.active_variables:
                if var in grow_info:
                    yield var, strain['grow_info'][var]
                else:
                    yield var, strain[var]

    def generate_variables(self):
        for var in data_variables:
            if var in self.active_variables:
                yield var


def get_generator(iterable):
    return (_ for _ in sorted(iterable, reverse=False))


def create_dataset_from_pickle(a_file):
    with open(a_file, 'rb') as pickle_file:
        weedataset = pickle.load(pickle_file)
        assert isinstance(weedataset, Weedataset)
    return weedataset
