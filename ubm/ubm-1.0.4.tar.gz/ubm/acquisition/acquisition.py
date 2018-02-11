import pandas
from ubm.acquisition.dataset import Dataset


class Acquisition:

    START_WITH_CAR_OFFSET = 10

    def __init__(self, log_path):
        self.log_path = log_path
        self.dataset = Dataset(self.load_data())

    def get_name(self):
        return self.log_path.get_name()

    def get_dataset(self):
        return self.dataset

    def to_hdf(self):
        df = self.dataset.get_original_data()
        df.to_hdf(self.log_path.get_path('hdf'), 'table', append=True)

    def load_data(self):
        if self.log_path.get_file_type() == 'csv':
            return pandas.read_csv(self.log_path.get_path(), sep=',', engine='c', na_filter=False, low_memory=False)
        if self.log_path.get_file_type() == 'hdf':
            return pandas.read_hdf(self.log_path.get_path(), 'table', where=['index>0'])
