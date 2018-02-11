import glob, logging, re, os
import numpy as np
import pandas as pd
from collections import OrderedDict
from ubm.acquisition import Acquisition
from ubm.acquisition.dataset import Dataset


class LogsManager:
    DEFAULT_PATH = 'Data/log_files/*/'
    SUPPORTED_TYPES = ['hdf', 'csv']
    MAX_SEEK_DEPTH = -5

    def __init__(self, directory=DEFAULT_PATH, file_type=SUPPORTED_TYPES[0]):
        self.log_count = 0
        self.log_paths = []
        self.logs_file_type = file_type
        self.logs_directory = directory
        self.search_directory = ""
        self.log = logging.getLogger('logsManager')
        self.log.addHandler(logging.StreamHandler())
        self.log.setLevel(1)
        self.selected_logs = OrderedDict(
            [('dates', []), ('locations', []), ('specialities', []), ('drivers', []), ('attempts', [])])
        self.selected_variable_names = []
        self._load()
        self.log.info("Loaded " + str(len(self.log_paths)) + " logs, from " + self.search_directory)

    def get_acquisition(self, name):
        for log_path in self.log_paths:
            if log_path.get_name() == name:
                return Acquisition(log_path)

    def get_merged_dataset(self):
        selected_names = self.get_selected_log_names()
        data_frames = []
        for name in selected_names:
            data_frames.append(self.get_selected_data(name))
        return Dataset(pd.concat(data_frames))

    def set_dates(self, dates):
        self.selected_logs['dates'] = self._parse_set(dates)
        return self

    def set_locations(self, locations):
        self.selected_logs['locations'] = self._parse_set(locations)
        return self

    def set_specialities(self, specialities):
        self.selected_logs['specialities'] = self._parse_set(specialities)
        return self

    def set_drivers(self, drivers):
        self.selected_logs['drivers'] = self._parse_set(drivers)
        return self

    def set_attempts(self, attempts):
        self.selected_logs['attempts'] = self._parse_set(attempts)
        return self

    def set_variables(self, variable_names):
        self.selected_variable_names = self._parse_set(variable_names)
        return self

    def get_selected_data(self, log_name):
        data = self.get_acquisition(log_name).get_dataset().get_original_data()
        if len(self.selected_variable_names) > 0:
            data = data[1:len(data), self.get_existing_selected_variables(data)]
        return data

    def get_existing_selected_variables(self, data):
        existing_variables = []
        for variable_name in self.selected_variable_names:
            if variable_name in data.columns:
                existing_variables.append(variable_name)

    def get_selected_log_names(self):
        regex = self._build_selection_regexp()
        matches = []
        for log_path in self.log_paths:
            if re.search(regex, log_path.get_name()):
                matches.append(log_path.get_name())
        return matches

    def _load(self):
        paths = []
        for depth in np.arange(0, self.MAX_SEEK_DEPTH, -1):
            self.search_directory = self._build_search_directory(depth)
            paths = glob.glob(self.search_directory)
            if len(paths):
                break
        for raw_path in paths:
            self.log_paths.append(LogPath(raw_path))

    def _build_search_directory(self, depth):
        return '/'.join((os.getcwd() + '/').split('/')[:(depth - 1)]) + '/' + self._build_logs_directory()

    def _build_logs_directory(self):
        return self.logs_directory + self.logs_file_type + '/*.' + self.logs_file_type

    def _build_selection_regexp(self):
        regex = ''
        for field in self.selected_logs:
            regex = regex + self._get_selection_piece(field) + '_'
        return regex[0:len(regex) - 1]

    def _get_selection_piece(self, piece):
        if len(self.selected_logs[piece]):
            regex_piece = '('
            for selector in self.selected_logs[piece]:
                regex_piece += selector + '|'
            regex_piece = regex_piece[0:len(regex_piece) - 1] + ')'
        else:
            regex_piece = '.*'
        return regex_piece

    def _parse_set(self, argument):
        parsed = argument
        if isinstance(argument, str):
            parsed = [argument]
        return parsed


class LogPath:
    def __init__(self, raw_path):
        self.raw_path = raw_path
        self.dir = ''
        self.file_name = ''
        self.file_extension = ''
        self._parse()

    def get_path(self, file_type=None):
        if file_type is None:
            return self.raw_path
        else:
            return self.get_dir(file_type) + '/' + self.get_name() + '.' + file_type

    def get_dir(self, file_type=None):
        if file_type is None:
            return self.dir
        else:
            return self.dir + '/../' + file_type

    def get_file_type(self):
        return self.file_extension

    def get_name(self):
        return self.file_name

    def _parse(self):
        match = re.search('(.*)/(.*)\.(.*)', self.raw_path)
        self.dir = match.group(1)
        self.file_name = match.group(2)
        self.file_extension = match.group(3)
