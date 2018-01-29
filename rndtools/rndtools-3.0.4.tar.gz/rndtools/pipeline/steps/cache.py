from rndtools.keras_dataset_generator import DataSerializer
from rndtools.pipeline import Step


class Cache(Step):
    GIVE_ALL = True

    def __init__(self, path):
        self.path = path

    def transform(self, params):
        DataSerializer(self.path).pickle_out(params)


class UnCache(Step):
    GIVE_ALL = True

    def __init__(self, path):
        self.path = path

    def transform(self, params):
        return DataSerializer(self.path).pickle_in()
