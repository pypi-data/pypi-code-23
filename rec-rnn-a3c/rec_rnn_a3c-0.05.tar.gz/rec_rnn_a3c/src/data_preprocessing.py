from __future__ import division

import os
import sys

sys.path.append(os.path.join(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0], '..'))

import csv
import json
import tempfile
import threading
import multiprocessing


import boto3 as boto3
import pandas as pd
import tensorflow as tf
import botocore as botocore

from multiprocessing.pool import ThreadPool

from rec_rnn_a3c.src.util import replace_multiple, get_all_s3_keys, s3_download

S3 = boto3.client('s3', aws_access_key_id=os.environ.get('S3_KEY'), aws_secret_access_key=os.environ.get('S3_SECRET'))
BUCKET = 'rec-rnn-mpd'
WORKING_DIR = os.path.join(tempfile.gettempdir(), BUCKET)
DUMMY_FILENAMES = ["/Users/Tim/Documents/mpd.v1/data/mpd.slice.0-999.json",
                   "/Users/Tim/Documents/mpd.v1/data/mpd.slice.1000-1999.json"]

MAPPER = 'map'
DATA = 'data'
PREPROC_DATA = 'preproc_data'

URI_TO_FREQUENCY = 'uri-to-frequency.csv'
URI_TO_ID = 'uri-to-id.csv'
ID_TO_URI = 'id-to-uri.csv'
PLAYLIST_DATAFRAME = 'playlist-dataframe.csv'

class DataPreprocessor(object):
    def __init__(self, working_dir, files, num_examples, train_fraction=0.9):
        self.working_dir = working_dir
        self.files = files
        self.num_examples = num_examples
        self.train_fraction = train_fraction

        print("Set working dir to: %s" % working_dir)

        self.uri_to_frequency = None
        self.uri_to_id = None

    def _calculate_track_frequencies(self, file):
        file_path = os.path.join(self.working_dir, file)
        if s3_download(S3, file, BUCKET, working_dir):
            print("Downloaded %s from S3 Bucket %s" % (file, BUCKET))

        with open(file_path) as json_raw:
            current_thread = threading.currentThread()

            print("Thread %s: Start processing file %s" % (current_thread, file))

            json_data = json.load(json_raw)
            data_frame = pd.DataFrame.from_dict(json_data['playlists'])

            all_playlist_tracks = {}
            for index, row in data_frame[['pid', 'tracks']].iterrows():
                pid = row['pid']
                playlist_tracks = row['tracks']
                df_playlist_tracks = pd.DataFrame(playlist_tracks)
                all_playlist_tracks[pid] = df_playlist_tracks

            uri_to_frequency = {}
            for pid, df_tracks in all_playlist_tracks.iteritems():
                for _, track_uri in df_tracks['track_uri'].iteritems():
                    if track_uri in uri_to_frequency:
                        uri_to_frequency[track_uri] += 1
                    else:
                        uri_to_frequency[track_uri] = 1
            print("Thread %s: Finished processing file %s" % (current_thread, file))
            return uri_to_frequency


    def calculate_uri_to_freq(self, save=False):
        working_dir = os.path.join(self.working_dir, MAPPER)

        # Download necessary files from S3
        if s3_download(S3, 'map/uri-to-frequency.csv', BUCKET, self.working_dir):
            print("Downloaded %s from S3 Bucket %s" % (URI_TO_FREQUENCY, BUCKET))

        # Try to load serialized file from disk
        uri_to_frequency_path = os.path.join(working_dir, URI_TO_FREQUENCY)
        try:
            with open(uri_to_frequency_path, 'rb') as f:
                print("Loaded %s successfully" % URI_TO_FREQUENCY)
                reader = csv.reader(f)
                self.uri_to_frequency = dict(reader)
        # Calculate new file
        except IOError:
            print("Could not find %s - Now calculating..." % URI_TO_FREQUENCY)
            # Prepare Working Dir
            if not os.path.exists(working_dir):
                print("Created new dir %s" % working_dir)
                os.makedirs(working_dir)
            # Thread Pool for Parallelization
            num_threads = multiprocessing.cpu_count()
            pool = ThreadPool(processes=num_threads)

            results = pool.map(self._calculate_track_frequencies, self.files)
            pool.close()
            pool.join()

            # Combine parallelized results
            uri_to_frequency = {}
            for mapper in results:
                for track_uri, frequency in mapper.iteritems():
                    if track_uri in uri_to_frequency:
                        uri_to_frequency[track_uri] += frequency
                    else:
                        uri_to_frequency[track_uri] = frequency

            self.uri_to_frequency = uri_to_frequency

            # Save to disk
            if save:
                with open(uri_to_frequency_path, 'wb') as f:
                    writer = csv.writer(f)
                    for key, value in uri_to_frequency.items():
                        writer.writerow([key, value])
                    print("Saved %s successfully" % URI_TO_FREQUENCY)

    def calculate_uri_to_id(self, save=False):
        working_dir = os.path.join(self.working_dir, MAPPER)

        # Download necessary files from S3
        if s3_download(S3, 'map/uri-to-id.csv', BUCKET, self.working_dir):
            print("Downloaded %s from S3 Bucket %s" % (URI_TO_ID, BUCKET))
        try:
            uri_to_id_path = os.path.join(working_dir, URI_TO_ID)
            with open(uri_to_id_path, 'rb') as f:
                print("Loaded %s successfully" % URI_TO_ID)
                reader = csv.reader(f)
                self.uri_to_id = dict(reader)
        except IOError:
            print("Could not find %s - Now calculating..." % URI_TO_ID)

            # If uri_to_freq not present, calculate
            if not self.uri_to_frequency:
                self.calculate_uri_to_freq(working_dir)

            # Sort subject to frequency
            sorted_uris = sorted(self.uri_to_frequency, key=self.uri_to_frequency.get)[::-1]

            uri_to_id = {}
            for idx, uri in enumerate(sorted_uris):
                uri_to_id[uri] = idx

            self.uri_to_id = {}

            # Save to disk
            if save:
                uri_to_id_path = os.path.join(working_dir, URI_TO_ID)
                with open(uri_to_id_path, 'wb') as f:
                    writer = csv.writer(f)
                    for key, value in uri_to_id.items():
                        writer.writerow([key, value])
                print("Saved %s successfully" % URI_TO_ID)

    def _make_example(self, sequence, labels):
        ex = tf.train.SequenceExample()
        fl_tokens = ex.feature_lists.feature_list["train/sequence"]
        fl_labels = ex.feature_lists.feature_list["train/labels"]
        for token, label in zip(sequence, labels):
            fl_tokens.feature.add().int64_list.value.append(token)
            fl_labels.feature.add().int64_list.value.append(label)
        return ex

    def _convert_to_tfrecords(self, file):
        current_thread = threading.currentThread()
        print("Thread %s: Start processing file %s" % (current_thread, file))

        file_path = os.path.join(self.working_dir, file)

        type = 'train' if int(file.split('.')[-2].split('-')[-1]) / self.num_examples < self.train_fraction else 'eval'

        conv_file_path = replace_multiple(file_path, {DATA: PREPROC_DATA, 'json': type + '.tfrecords'})

        if os.path.isfile(conv_file_path):
            print("Thread %s: Converted file %s already exists." % (current_thread, file))
        else:
            if not os.path.isfile(file_path):
                try:
                    S3.download_file(BUCKET, file, file_path)
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "404":
                        print("Thread %s: File %s does not exist in S3." % (current_thread, file))
                    else:
                        raise

            with open(file_path) as json_raw:
                json_data = json.load(json_raw)
                data_frame = pd.DataFrame.from_dict(json_data['playlists'])

                sequences = []
                label_sequences = []
                for index, row in data_frame[['pid', 'tracks']].iterrows():
                    playlist_tracks = row['tracks']

                    seq = [self.uri_to_id[t['track_uri']] for t in playlist_tracks]
                    sequences.append(seq[:-1])
                    label_sequences.append(seq[1:])

                with open(conv_file_path, 'wb') as fp:
                    writer = tf.python_io.TFRecordWriter(fp.name)
                    for sequence, label_sequence in zip(sequences, label_sequences):
                        ex = self._make_example(map(int, sequence), map(int, label_sequence))
                        writer.write(ex.SerializeToString())
                    writer.close()
                    print('Thread %s: Saved file %s ...' % (current_thread, conv_file_path))

    def calculate_dataset(self):
        data_dir = os.path.join(self.working_dir, DATA)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        preproc_data_dir = os.path.join(self.working_dir, PREPROC_DATA)
        if not os.path.exists(preproc_data_dir):
            os.makedirs(preproc_data_dir)

        for _ in self.files:
            num_threads = multiprocessing.cpu_count()
            pool = ThreadPool(processes=num_threads)
            pool.map(self._convert_to_tfrecords, self.files)
            pool.close()


if __name__ == "__main__":
    working_dir = os.path.join(tempfile.gettempdir(), BUCKET)
    files = filter(lambda x: 'json' in x, get_all_s3_keys(S3, BUCKET))
    num_examples = int(files[-1].split('.')[-2].split('-')[-1])
    data_preprocessor = DataPreprocessor(
        working_dir=working_dir,
        files=files,
        num_examples=num_examples
    )

    data_preprocessor.calculate_uri_to_freq()
    data_preprocessor.calculate_uri_to_id()
    data_preprocessor.calculate_dataset()




