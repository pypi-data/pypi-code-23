# -*- author: Dimitri Scheftelowitsch -*-
# -*- coding:utf-8 -*-

import pandas as pd
from pandas.core.frame import DataFrame
from typing import Any, Dict, Iterable
import logging
from os.path import exists
from collider import Stage


class RunResult:
    def __init__(self, stage: str, value: Any, data: Dict[str, Any], index: int):
        self.stage = stage
        self.value = value
        self.data = data
        self.index = index


def csvfile(basename):
    return "{0}_results.csv".format(basename)


def picklefile(basename):
    return "{0}_results.pickle".format(basename)


def featherfile(basename):
    return "{0}_results.feather".format(basename)

class ResultLog:
    def __init__(self, experiment_name: str, values: Dict[str, Iterable[Any]]):
        self.csv_file = csvfile(experiment_name)
        self.pickle_file = picklefile(experiment_name)
        self.feather_file = featherfile(experiment_name)
        self.experiment_name = experiment_name
        self.values = values
        self.data = DataFrame()
        self.load()
        self.processed_items = 0
        printer = logging.getLogger("collider")
        printer.info("Result logger initialized")

    def put_result(self, next_result: RunResult, force_save=True):
        if len(self.data) > 0:
            stage_value_locations = self.stage_value_locations(next_result.stage, next_result.value)
            # remove previous results
            self.data = self.data[stage_value_locations.apply(lambda x: not x)]
        printer = logging.getLogger("collider")
        printer.info("Got a new result: stage {0} for value {1}".format(next_result.stage, next_result.value))
        # printer.debug("Result is {0}".format(next_result.data))
        data = next_result.data
        data['Stage'] = next_result.stage
        for i, k in enumerate(sorted(self.values.keys())):
            data[k] = next_result.value[i]
        i = len(self.data)
        # printer.debug("{} elements before: {}".format(self, i))
        frame = DataFrame(data, index=[0])
        self.data = pd.concat([self.data, frame], join='outer', verify_integrity=True, ignore_index=True)
        self.processed_items += 1
        # printer.debug("{} elements after: {}".format(self, len(self.data)))
        if (self.processed_items % 1000 == 0) or force_save:
            printer.debug("Processed {0} items, saving…".format(self.processed_items))
            self.save()

    def save(self):
        self.data.to_pickle(self.pickle_file)

    def save_csv(self):
        self.data.to_csv(self.csv_file, index=False)

    def load(self):
        if exists(self.pickle_file):
            self.data = pd.read_pickle(self.pickle_file)
        else:
            self.data = pd.DataFrame()

    def stage_value_locations(self, stage: str, value: Any) -> DataFrame:
        request = {'Stage': stage}
        for i, k in enumerate(sorted(self.values.keys())):
            request[k] = value[i]
        return self.data[list(request.keys())].apply(lambda x: x.tolist() == list(request.values()), axis=1)

    def get_stage_value_results(self, stage: str, value: Any) -> DataFrame:
        if len(self.data) > 0:
            locations = self.stage_value_locations(stage, value)
            return self.data.loc[locations]
        else:
            return DataFrame()

    def get_data(self, stage: Stage, value: Any) -> Dict[str, Any]:
        frame = self.get_stage_value_results(stage.name, value)
        # extract single value
        data = frame.iloc[0].to_dict()
        return data
