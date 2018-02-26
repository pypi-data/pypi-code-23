from pathlib import Path
import os
import requests
from urllib.parse import urlparse
import xyxy.config
from tqdm import tqdm
import abc
import csv


class Formula(abc.ABC):

    def __init__(self):
        self.name = self.__class__.__name__.lower()
        self.base_path = Path(xyxy.config.xyxy_base_path).expanduser() / self.name / 'data'
        os.makedirs(self.base_path, exist_ok=True)

        self.title = None
        self.description = None
        self.homepage = None

    def download_file(self, url, filename=None):
        if filename is None:
            o = urlparse(url)
            destination = self.base_path / os.path.basename(o.path)
        else:
            destination = self.base_path / filename

        chunk_size = 1024

        r = requests.get(url, stream=True)

        r.raise_for_status()

        total_size = int(r.headers.get('content-length', 0))

        with open(destination, 'wb') as f:
            for chunk in tqdm(r.iter_content(chunk_size), total=total_size // chunk_size + 1, unit='KB', leave=True):
                if chunk:
                    f.write(chunk)

        return destination

    def is_downloaded(self):
        return os.listdir(self.base_path) != []

    @abc.abstractmethod
    def download_dataset(self):
        pass

    @abc.abstractmethod
    def load_data(self):
        pass


class CSVFormula(Formula):

    def __init__(self):
        super().__init__()
        self.url = None

    def download_dataset(self):
        self.download_file(self.url, filename='{}.csv'.format(self.name))

    def load_data(self):
        with open(self.base_path / '{}.csv'.format(self.name), 'r') as f:
            return list(csv.DictReader(f))
