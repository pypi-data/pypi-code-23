from datetime import datetime
import logging
import os

import s3io
from sklearn.externals import joblib

from langassist_model_engine.constants import LOCAL_DUMP

logger = logging.getLogger(__name__)

class BaseModel():
    def __init__(self, feature_builder):
        self.feature_builder = feature_builder

    def train(self, x_train, y_train):
        raise NotImplementedError

    def predict(self, predict_x):
        raise NotImplementedError

    def test(self, x_test, y_test):
        raise NotImplementedError

    @staticmethod
    def _dump_dir():
        return "nli"

    def _archive_s3_models(self):
        pass

    def _archive_local_models(self):
        pass

    def _save_to_s3(self, latest=False):
        '''
        Save the model as a pickle in S3
        :return:
        '''
        credentials = dict(
            aws_access_key_id=os.environ['LANGASSIST_AWS_ACCESS_KEY'],
            aws_secret_access_key=os.environ['LANGASSIST_AWS_SECRET_KEY'],
        )
        bucket = os.environ['MODEL_BUCKET']
        key = self._pickle_name(latest)
        dump_dir = self._dump_dir()
        compress = ('gzip', 3)
        loc = 's3://{0}/{1}/{2}'.format(bucket, dump_dir, key)

        with s3io.open(
                loc,
                mode='w',
                **credentials
        ) as s3_file:
            joblib.dump(self, s3_file, compress=compress)

        logger.info("Saved model %s externally to %s" % (self.__str__(), loc))

    def _save_locally(self, latest=False):
        '''
        Save the model as a pickle in the local filesystem
        :return:
        '''

        dump_dir = self._dump_dir()
        loc = LOCAL_DUMP + dump_dir + '/' + self._pickle_name(latest)
        joblib.dump(self, loc)
        logger.info("Saved model %s locally to %s" % (self.__str__(), loc))

    def save(self, prod, latest=False):
        if(prod is True):
            self._archive_s3_models()
            self._save_to_s3(latest=latest)
        else:
            self._archive_local_models()
            self._save_locally(latest)

    @staticmethod
    def load(dir, key):
        credentials = dict(
            aws_access_key_id=os.environ['LANGASSIST_AWS_ACCESS_KEY'],
            aws_secret_access_key=os.environ['LANGASSIST_AWS_SECRET_KEY'],
        )
        bucket = os.environ['MODEL_BUCKET']

        with s3io.open(
                's3://{0}/{1}/{2}'.format(bucket, dir, key),
                mode='w',
                **credentials) as s3_file:
            return joblib.load(s3_file)

    def _pickle_name(self, latest=False):
        now = datetime.now()
        return "%s-%s_%d.%d.%d.%d.%d%s.pkl" % (self.__class__.__name__.lower(),
                                               self.feature_builder.__class__.__name__.lower(),
                                               now.year,
                                               now.month,
                                               now.day,
                                               now.hour,
                                               now.minute,
                                               "_latest" if latest else "")

    def __str__(self):
        return "[%s\t%s]" % (self.__class__.__name__, self.feature_builder.__class__.__name__)