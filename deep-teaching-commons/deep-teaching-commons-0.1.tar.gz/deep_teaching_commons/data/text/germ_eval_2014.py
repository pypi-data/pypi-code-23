import os
import shutil
import zipfile
import tempfile
from glob import glob

# third party
import requests

# internal
from deep_teaching_commons import config


class GermEval2014:
    def __init__(self, base_data_dir=None, data_url=None, auto_download=True, verbose=True):
        self.base_data_dir = base_data_dir
        if self.base_data_dir is None:
            self.base_data_dir = config.BASE_DATA_DIR

        self.data_url = data_url
        if self.data_url is None:
            self.data_url = 'https://www.lt.informatik.tu-darmstadt.de/fileadmin/user_upload/Group_LangTech/data/' \
                            'GermEval2014_complete_data.zip'

        self.verbose = verbose

        self.data_dir = os.path.join(self.base_data_dir, 'GermEval2014')
        self.train_file = os.path.join(self.data_dir, 'NER-de-train.tsv')
        self.test_file = os.path.join(self.data_dir, 'NER-de-test.tsv')
        self.val_file = os.path.join(self.data_dir, 'NER-de-dev.tsv')

        if auto_download:
            if self.verbose:
                print('auto download is active, attempting download')
            self.download()

    def download(self):
        # download corpus if directory does not yet exist
        if os.path.exists(self.data_dir):
            if self.verbose:
                print('data directory already exists, no download required')
        else:
            if self.verbose:
                print('data directory does not exist, starting download')
            # create directories
            os.makedirs(self.data_dir)
            temp_dir = tempfile.mkdtemp()

            try:
                # stream download
                r = requests.post(self.data_url, stream=True)
                r.raise_for_status()
                temp_path = os.path.join(temp_dir, 'corpus.zip')
                with open(temp_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=4096):
                        if chunk:
                            f.write(chunk)
                r.raise_for_status()

                # extract zip
                with zipfile.ZipFile(temp_path, 'r') as z:
                    z.extractall(temp_dir)

                # move *.tsv files
                source_paths = glob(os.path.join(temp_dir, '*', '*.tsv'), recursive=True)
                for source_path in source_paths:
                    file_name = os.path.split(source_path)[1]
                    destination_path = os.path.join(self.data_dir, file_name)
                    shutil.move(source_path, destination_path)
            except:
                shutil.rmtree(self.data_dir)
                raise
            finally:
                shutil.rmtree(temp_dir)

            if self.verbose:
                print('data successfully downloaded')

    @staticmethod
    def sequences(data_file):
        with open(data_file) as f:
            sequence = []
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    continue
                if not line:
                    yield sequence
                    sequence = []
                    continue
                _, token, iob_outer, iob_inner = line.split()
                sequence.append((token, iob_outer, iob_inner))

            if sequence:
                yield sequence

    def train_sequences(self):
        return self.sequences(self.train_file)

    def test_sequences(self):
        return self.sequences(self.test_file)

    def val_sequences(self):
        return self.sequences(self.val_file)
