from pathlib import Path
import os
import requests
from urllib.parse import urlparse
import xyxy.config
from tqdm import tqdm
import abc
import csv
import shutil


class Formula(abc.ABC):

    def __init__(self):
        self.name = self.__class__.__name__.lower()
        self.formula_dir = Path(xyxy.config.xyxy_home_dir).expanduser() / self.name
        self.base_dir = Path(xyxy.config.xyxy_home_dir).expanduser() / self.name / 'data'
        os.makedirs(self.base_dir, exist_ok=True)

        self.title = None
        self.description = None
        self.homepage = None
        self.files = None

    def download_file(self, file):
        if file.get('as') is None:
            o = urlparse(file.get('url'))
            destination = self.base_dir / os.path.basename(o.path)
        else:
            destination = self.base_dir / file.get('as')

        chunk_size = 1024

        r = requests.get(file.get('url'), stream=True)

        r.raise_for_status()

        total_size = int(r.headers.get('content-length', 0))

        with open(destination, 'wb') as f:
            for chunk in tqdm(r.iter_content(chunk_size), total=total_size // chunk_size + 1,
                              unit='KB', leave=True):
                if chunk:
                    f.write(chunk)

        return destination

    def download(self):
        if self.files is None:
            raise NotImplementedError
        else:
            for file in self.files:
                self.download_file(file)
            self.post_download()

    def post_download(self):
        pass

    def is_downloaded(self):
        return os.listdir(self.base_dir) != []

    def clear(self):
        shutil.rmtree(self.formula_dir)

    @abc.abstractmethod
    def validate(self):
        pass

    @abc.abstractmethod
    def load(self):
        pass
