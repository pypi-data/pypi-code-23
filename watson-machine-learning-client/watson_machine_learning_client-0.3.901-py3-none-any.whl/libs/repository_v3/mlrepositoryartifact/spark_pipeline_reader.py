################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


import os
import shutil

from repository_v3.mlrepository.artifact_reader import ArtifactReader
from repository_v3.util.compression_util import CompressionUtil


# TODO this part needs to be implemented
class SparkPipelineReader(ArtifactReader):
    def __init__(self, ml_pipeline, type_name):
        self.archive_path = None
        self.ml_pipeline = ml_pipeline
        self.type_name = type_name

    def read(self):
        return self._open_stream()

    def close(self):
        os.remove(self.archive_path)
        self.archive_path = None

    def _save_pipeline_archive(self):
        temp_dir = './{}'.format(self.type_name)
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        self.ml_pipeline.write().overwrite().save(temp_dir)
        archive_path = self._compress_artifact(temp_dir)
        shutil.rmtree(temp_dir)
        return archive_path

    def _compress_artifact(self, compress_artifact):
        tar_filename = '{}_content.tar'.format(self.type_name)
        gz_filename = '{}.gz'.format(tar_filename)
        CompressionUtil.create_tar(compress_artifact, '.', tar_filename)
        CompressionUtil.compress_file_gzip(tar_filename, gz_filename)
        os.remove(tar_filename)
        return gz_filename

    def _open_stream(self):
        if self.archive_path is None:
            self.archive_path = self._save_pipeline_archive()
        return open(self.archive_path, 'rb')
