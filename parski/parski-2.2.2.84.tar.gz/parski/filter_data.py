"""module for filtering data"""
from __future__ import print_function

import time
import re
from copy import deepcopy
from parski.utils import dict_to_paths, filter_datetime

def filter_data(data, search_input, max_results=5000, silent=False):
    """filter data class/function wrapper"""

    options = {}
    options['data'] = data
    options['search_input'] = search_input
    options['max_results'] = max_results
    options['silent'] = silent

    filter_object = FilterData(options)
    filter_object.filter_data()

    return filter_object

class FilterData(dict):
    """filter data using search_input"""
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, options):
        dict.__init__(self)
        for key in options.keys():
            self[key] = options[key]
        self.search_input = deepcopy(options['search_input'])
        self.metrics = {}
        self.results = []

    def _whisper(self, text):
        """print wrapper to check silent parameter"""
        if not self.silent:
            print(text)

    def filter_data(self):
        """filter data based on path list or search dict arrays"""

        #initialize metrics
        self.metrics = {
            'missing_keys': {
                'total': 0
            },
            'regex_errors': {
                'total': 0
            },
            'searches': 0,
            'search_time': 0
        }

        #standardize input
        self._standardize_input()

        if not self.data:
            self._whisper("Input data is empty.  No results found.")
            self.results = []
            return

        #Whisper of Life
        self._whisper("\nData length: %i" % len(self.data))
        self._whisper("Search Input:")
        for item in self.search_input:
            self._whisper(str(item))
        self._whisper("Running Search...")

        #each path_list is OR'd with each other, so results are added
        start_time = time.time()
        valid_indices = []
        for index, path_list in enumerate(self.search_input):

            #Remove paths where value is None
            path_list = [x for x in path_list if x['value'] is not None]

            #check each entry in data
            for i, entry in enumerate(self.data):
                #check if max results have been found
                if len(valid_indices) >= self.max_results:
                    self.metrics['search_time'] = time.time() - start_time
                    self.results = [self.data[index] for index in valid_indices]
                    return
                #actually do the filtering
                if i in valid_indices:
                    continue
                elif self._entry_filter(entry, path_list):
                    valid_indices.append(i)
                self.metrics['searches'] += 1

        #Write filtered results to results
        self.results = [self.data[index] for index in valid_indices]

        #Calculate Reults
        self.metrics['search_time'] = time.time() - start_time
        if self.metrics['searches'] == 0:
            self.metrics['search_avg'] = None
        else:
            self.metrics['search_avg'] = self.metrics['search_time'] / self.metrics['searches']

        #Dying Whisper
        self._whisper("Results found: %i" % len(valid_indices))


######################################################

    @staticmethod
    def _is_search_path(item):
        """check if item is a search_path"""
        if not isinstance(item, dict):
            return False
        if sorted(item.keys()) != ['path', 'value']:
            return False
        if not isinstance(item['path'], list):
            return False
        if isinstance(item['value'], (dict, list)):
            return False
        return True


    def _standardize_input(self):
        """standardize input to always have path group"""

        error_message = "Search input list must be ALL path groups or ALL search dicts"

        search_dict_found = False
        path_found = False
        #check if search path or search dict and converts to search path groups
        if isinstance(self.search_input, dict):
            if self._is_search_path(self.search_input):
                self.search_input = [[self.search_input]]
            else:
                self.search_input = [dict_to_paths(self.search_input)]

        #check if list of paths or list of dicts and converts if needed
        elif isinstance(self.search_input, list):
            for index, item in enumerate(self.search_input):

                #list of dicts
                if isinstance(item, dict):
                    if not self._is_search_path(item) and not path_found:
                        search_dict_found = True
                        self.search_input[index] = dict_to_paths(self.search_input[index])
                    elif self._is_search_path(item) and not search_dict_found:
                        path_found = True
                        self.search_input[index] = item
                    else:
                        raise TypeError(error_message)

                #list of lists
                elif isinstance(item, list):
                    for inner_item in item:
                        #list of lists must be search paths
                        if not self._is_search_path(inner_item):
                            raise TypeError(error_message)

                #list of garbage
                else:
                    raise TypeError(error_message)

            if path_found:
                self._sort_path_groups()

        #not list or dict
        else:
            raise TypeError("Search input must be a list or dict")

        self._check_first_index()

    def _sort_path_groups(self):
        new_search_input = []
        no_index = []
        remaining = []
        for path in self.search_input:
            try:
                int(path['path'][0])
                remaining.append(path)
            except ValueError:
                no_index.append(path)

        while remaining:
            current_path = remaining[0]
            new_group = [x for x in remaining if x['path'][0] == current_path['path'][0]]
            remaining = [x for x in remaining if x not in new_group]
            new_search_input.append(new_group)

        if no_index:
            new_search_input.append(no_index)
        self.search_input = new_search_input

    def _check_first_index(self):
        for index, path_group in enumerate(self.search_input):
            for path_index, path in enumerate(path_group):
                try:
                    int(path['path'][0])
                    self.search_input[index][path_index]['path'] = path['path'][1:]
                except ValueError:
                    pass

####################################################

    def _entry_filter(self, entry, path_list):
        """filter single entry with path_list"""

        path_groups = []
        remaining = path_list

        #sort into path groups
        while remaining:
            current_path = remaining[0]
            #check if path has ended and doesn't equal value.
            if not current_path['path']:

                #One fail is total fail.  One pass is NOT total pass.
                if not self._value_check(entry, current_path['value']):
                    return False
                remaining = remaining[1:]

            #remaining paths sorted into groups based on first value
            else:
                new_group = [x for x in remaining if x['path'][0] == current_path['path'][0]]
                remaining = [x for x in remaining if x not in new_group]
                path_groups.append(new_group)

        return self._filter_path_groups(entry, path_groups)

    def _filter_path_groups(self, entry, path_groups):
        """Groups checks by list to ensure passes are at same index"""
        if entry is None:
            return False

        for group in path_groups:
            current_index = group[0]['path'][0]

            #check if list, if so check for at least one match
            if isinstance(entry, list):
                # split into groups for last path to check of end lists
                end_group = [x for x in group if len(x['path']) == 1]
                for end_path in end_group:
                    if not [x for x in entry if self._value_check(entry, end_path['value'])]:
                        return False

                # check for list of items
                cont_group = [x for x in group if x not in end_group]

                # go further down path
                cont_group = [{'value': x['value'], 'path': x['path'][1:]} for x in cont_group]
                cont_passes = [x for x in entry if self._entry_filter(x, cont_group)]

                if not cont_passes and cont_group:
                    return False
            elif current_index not in list(entry):
                self._add_to_missing_key(current_index)
                return False
            else:
                #go one further down the path
                group = [{'value': x['value'], 'path': x['path'][1:]} for x in group]
                if not self._entry_filter(entry[current_index], group):
                    return False
        return True

################################################

    def _value_check(self, entry, value):
        try:
            value = str(value)
            entry = str(entry)
            if value.lower() == 'null':
                value = 'None'
            regex_value = re.compile(value, re.IGNORECASE)
            return bool(re.search(regex_value, str(entry)) or filter_datetime(value, entry))
        except Exception:
            self._add_to_regex_errors(value)
            return False

#################################################

    def _add_to_missing_key(self, key):
        if key not in self.metrics['missing_keys']:
            self.metrics['missing_keys'][key] = 1
        else:
            self.metrics['missing_keys'][key] += 1
        self.metrics['missing_keys']['total'] += 1

    def _add_to_regex_errors(self, key):
        if key not in self.metrics['regex_errors']:
            self.metrics['regex_errors'][key] = 1
        else:
            self.metrics['regex_errors'][key] += 1
        self.metrics['regex_errors']['total'] += 1
