import csv
import tempfile
import gzip
import io
import contextlib
import os

from generic_report_generator import ResultDownloadStrategy

class RedshiftResultDownloadStrategy(ResultDownloadStrategy):
    def __init__(self, generic_storage):
        super().__init__()
        self.generic_storage = generic_storage

    def download(self, download_from, csv_header):
        return download_redshift_unload_and_insert_header(
            download_from,
            csv_header,
            self.generic_storage
        )

@contextlib.contextmanager
def download_redshift_unload_and_insert_header(
        unload_destination,
        header_to_insert,
        generic_storage
):
    local_result = _download_redshift(unload_destination, generic_storage)
    local_result_with_header = _insert_header_to_csv(header_to_insert, local_result)
    yield local_result_with_header
    os.remove(local_result)
    os.remove(local_result_with_header)

def _download_redshift(unload_destination, generic_storage):
    return generic_storage.download(unload_destination + "000.gz")

def _insert_header_to_csv(csv_headers, csv_source):
    result_csv_path = None
    with open(csv_source, 'rb') as csv_compressed_source_file, \
            tempfile.NamedTemporaryFile(mode='w+', delete=False) as csv_dest_file:
        with io.TextIOWrapper(
            gzip.GzipFile(fileobj=csv_compressed_source_file), encoding="utf8"
        ) as csv_source_file:
            csv_reader = csv.reader(csv_source_file)
            csv_writer = csv.writer(csv_dest_file)
            result_csv_path = csv_dest_file.name
            csv_writer.writerow(csv_headers)
            for row in csv_reader:
                csv_writer.writerow(row)
    return result_csv_path
